"""
Analyses avancées pour les tendances d'albédo
=============================================

Ce module contient les analyses statistiques avancées incluant le contrôle 
d'autocorrélation, le pré-blanchiment et les intervalles de confiance bootstrap.
"""

import numpy as np
import pandas as pd
from sklearn.utils import resample
from .config import ANALYSIS_CONFIG, get_autocorr_status
from .utils import (prewhiten_series, calculate_autocorrelation, manual_mann_kendall,
                   validate_data, print_section_header, format_pvalue)
from .basic_trends import BasicTrendAnalyzer

class AdvancedAnalyzer:
    """
    Analyseur pour les tests statistiques avancés
    """
    
    def __init__(self, data_loader):
        """
        Initialise l'analyseur avancé
        
        Args:
            data_loader: Instance de SaskatchewanDataLoader avec données chargées
        """
        self.data_loader = data_loader
        self.data = data_loader.data
        self.fraction_classes = data_loader.fraction_classes
        self.class_labels = data_loader.class_labels
        self.results = {}
        
    def analyze_autocorrelation_effects(self, variable='mean'):
        """
        Analyse les effets d'autocorrélation et applique des corrections
        
        Args:
            variable (str): Variable à analyser ('mean' ou 'median')
            
        Returns:
            dict: Résultats des analyses d'autocorrélation
        """
        print_section_header(f"Analyses d'autocorrélation - Variable: {variable}", level=2)
        
        results = {}
        
        for fraction in self.fraction_classes:
            print(f"\n🔍 Analyse autocorrélation: {self.class_labels[fraction]}")
            
            try:
                # Extraire les données
                fraction_data = self.data_loader.get_fraction_data(
                    fraction, variable, dropna=True
                )
                
                if len(fraction_data) < 15:
                    print(f"  ⚠️  Données insuffisantes ({len(fraction_data)} observations)")
                    results[fraction] = self._create_empty_autocorr_result(fraction, variable)
                    continue
                
                values = fraction_data['value'].values
                times = fraction_data['decimal_year'].values
                
                # Valider les données
                is_valid, clean_values, n_removed = validate_data(values, min_obs=15)
                if not is_valid:
                    print(f"  ❌ Données insuffisantes après nettoyage")
                    results[fraction] = self._create_empty_autocorr_result(fraction, variable)
                    continue
                
                # Synchroniser les temps
                clean_times = times[~np.isnan(values)]
                
                # 1. Test Mann-Kendall original
                original_mk = manual_mann_kendall(clean_values)
                
                # 2. Analyse d'autocorrélation
                autocorr_lag1 = calculate_autocorrelation(clean_values, lag=1)
                autocorr_lag2 = calculate_autocorrelation(clean_values, lag=2)
                autocorr_lag3 = calculate_autocorrelation(clean_values, lag=3)
                
                autocorr_status = get_autocorr_status(autocorr_lag1)
                
                # 3. Test Mann-Kendall modifié si autocorrélation significative
                modified_mk = None
                if abs(autocorr_lag1) > ANALYSIS_CONFIG['autocorr_thresholds']['weak']:
                    modified_mk = self._modified_mann_kendall(clean_values, autocorr_lag1)
                
                # 4. Pré-blanchiment si autocorrélation forte
                prewhitened_mk = None
                if abs(autocorr_lag1) > ANALYSIS_CONFIG['autocorr_thresholds']['moderate']:
                    try:
                        prewhitened_series = prewhiten_series(clean_values)
                        if len(prewhitened_series) > 10:
                            prewhitened_mk = manual_mann_kendall(prewhitened_series)
                        else:
                            print(f"    ⚠️  Série pré-blanchie trop courte")
                    except Exception as e:
                        print(f"    ⚠️  Erreur pré-blanchiment: {e}")
                
                # Stocker les résultats
                results[fraction] = {
                    'fraction': fraction,
                    'label': self.class_labels[fraction],
                    'variable': variable,
                    'n_obs': len(clean_values),
                    'n_removed': n_removed,
                    'autocorrelation': {
                        'lag1': autocorr_lag1,
                        'lag2': autocorr_lag2,
                        'lag3': autocorr_lag3,
                        'status': autocorr_status,
                        'significant': abs(autocorr_lag1) > ANALYSIS_CONFIG['autocorr_thresholds']['weak']
                    },
                    'mann_kendall_original': original_mk,
                    'mann_kendall_modified': modified_mk,
                    'mann_kendall_prewhitened': prewhitened_mk,
                    'recommendation': self._get_test_recommendation(autocorr_lag1, original_mk, modified_mk, prewhitened_mk)
                }
                
                # Affichage des résultats
                self._print_autocorr_results(results[fraction])
                
            except Exception as e:
                print(f"  ❌ Erreur lors de l'analyse: {e}")
                results[fraction] = self._create_empty_autocorr_result(fraction, variable)
        
        self.results[f'autocorr_{variable}'] = results
        return results
    
    def calculate_bootstrap_confidence_intervals(self, variable='mean', n_bootstrap=None):
        """
        Calcule les intervalles de confiance bootstrap pour les pentes de Sen
        
        Args:
            variable (str): Variable à analyser
            n_bootstrap (int, optional): Nombre d'itérations bootstrap
            
        Returns:
            dict: Résultats des intervalles de confiance bootstrap
        """
        if n_bootstrap is None:
            n_bootstrap = ANALYSIS_CONFIG['bootstrap_iterations']
        
        print_section_header(f"Intervalles de confiance Bootstrap - Variable: {variable}", level=2)
        print(f"🔄 {n_bootstrap} itérations bootstrap par fraction")
        
        results = {}
        
        for fraction in self.fraction_classes:
            print(f"\n🎯 Bootstrap: {self.class_labels[fraction]}")
            
            try:
                # Extraire les données
                fraction_data = self.data_loader.get_fraction_data(
                    fraction, variable, dropna=True
                )
                
                if len(fraction_data) < 20:
                    print(f"  ⚠️  Données insuffisantes pour bootstrap ({len(fraction_data)} observations)")
                    results[fraction] = self._create_empty_bootstrap_result(fraction, variable)
                    continue
                
                values = fraction_data['value'].values
                times = fraction_data['decimal_year'].values
                
                # Bootstrap
                bootstrap_slopes = []
                bootstrap_pvalues = []
                
                for i in range(n_bootstrap):
                    # Échantillon bootstrap
                    indices = resample(range(len(values)), n_samples=len(values), random_state=i)
                    boot_values = values[indices]
                    boot_times = times[indices]
                    
                    # Test Mann-Kendall sur l'échantillon bootstrap
                    try:
                        mk_result = manual_mann_kendall(boot_values)
                        bootstrap_pvalues.append(mk_result['p_value'])
                        
                        # Calcul de la pente (approximation simple)
                        if len(boot_values) > 5:
                            from scipy.stats import theilslopes
                            slope, _, _, _ = theilslopes(boot_values, boot_times)
                            bootstrap_slopes.append(slope * 10)  # Par décennie
                    except:
                        continue
                
                # Analyse des résultats bootstrap
                if len(bootstrap_slopes) > 0:
                    slope_ci = np.percentile(bootstrap_slopes, [2.5, 50, 97.5])
                    pvalue_mean = np.mean(bootstrap_pvalues)
                    pvalue_ci = np.percentile(bootstrap_pvalues, [2.5, 97.5])
                    
                    # Proportion de tests significatifs
                    significant_prop = np.mean(np.array(bootstrap_pvalues) < 0.05)
                    
                    results[fraction] = {
                        'fraction': fraction,
                        'label': self.class_labels[fraction],
                        'variable': variable,
                        'n_obs': len(values),
                        'n_bootstrap': n_bootstrap,
                        'n_successful': len(bootstrap_slopes),
                        'slope_bootstrap': {
                            'median': slope_ci[1],
                            'ci_95_low': slope_ci[0],
                            'ci_95_high': slope_ci[2],
                            'std': np.std(bootstrap_slopes)
                        },
                        'pvalue_bootstrap': {
                            'mean': pvalue_mean,
                            'ci_95_low': pvalue_ci[0],
                            'ci_95_high': pvalue_ci[1],
                            'significant_proportion': significant_prop
                        },
                        'bootstrap_slopes': bootstrap_slopes,
                        'bootstrap_pvalues': bootstrap_pvalues\n                    }\n                    \n                    # Affichage des résultats\n                    self._print_bootstrap_results(results[fraction])\n                    \n                else:\n                    print(f\"  ❌ Échec de toutes les itérations bootstrap\")\n                    results[fraction] = self._create_empty_bootstrap_result(fraction, variable)\n                    \n            except Exception as e:\n                print(f\"  ❌ Erreur lors du bootstrap: {e}\")\n                results[fraction] = self._create_empty_bootstrap_result(fraction, variable)\n        \n        self.results[f'bootstrap_{variable}'] = results\n        return results\n    \n    def _modified_mann_kendall(self, values, autocorr_lag1):\n        \"\"\"\n        Calcule le test Mann-Kendall modifié pour tenir compte de l'autocorrélation\n        \n        Args:\n            values (array): Valeurs à analyser\n            autocorr_lag1 (float): Autocorrélation lag-1\n            \n        Returns:\n            dict: Résultats du test Mann-Kendall modifié\n        \"\"\"\n        try:\n            # Test Mann-Kendall de base\n            mk_result = manual_mann_kendall(values)\n            \n            # Correction de la variance pour l'autocorrélation\n            n = len(values)\n            s = mk_result['s']\n            \n            # Facteur de correction (approximation)\n            correction_factor = 1 + (2 * autocorr_lag1 * (n - 1) * (n - 2)) / (3 * n * (n - 1))\n            \n            # Variance corrigée\n            var_s_corrected = (n * (n - 1) * (2 * n + 5) / 18) * correction_factor\n            \n            # Z-score corrigé\n            if s > 0:\n                z_corrected = (s - 1) / np.sqrt(var_s_corrected)\n            elif s < 0:\n                z_corrected = (s + 1) / np.sqrt(var_s_corrected)\n            else:\n                z_corrected = 0\n            \n            # P-value corrigée\n            from scipy.stats import norm\n            p_value_corrected = 2 * (1 - norm.cdf(abs(z_corrected)))\n            \n            # Tendance corrigée\n            if p_value_corrected < 0.05:\n                trend_corrected = 'increasing' if s > 0 else 'decreasing'\n            else:\n                trend_corrected = 'no trend'\n            \n            return {\n                'trend': trend_corrected,\n                'p_value': p_value_corrected,\n                'z': z_corrected,\n                's': s,\n                'tau': mk_result['tau'],\n                'correction_factor': correction_factor,\n                'method': 'modified_mann_kendall'\n            }\n            \n        except Exception as e:\n            print(f\"    ⚠️  Erreur Mann-Kendall modifié: {e}\")\n            return None\n    \n    def _get_test_recommendation(self, autocorr_lag1, original_mk, modified_mk, prewhitened_mk):\n        \"\"\"\n        Détermine quel test utiliser selon le niveau d'autocorrélation\n        \"\"\"\n        abs_autocorr = abs(autocorr_lag1)\n        \n        if abs_autocorr <= ANALYSIS_CONFIG['autocorr_thresholds']['weak']:\n            return {\n                'recommended_test': 'original',\n                'reason': 'Autocorrélation faible, test original approprié',\n                'confidence': 'high'\n            }\n        elif abs_autocorr <= ANALYSIS_CONFIG['autocorr_thresholds']['moderate']:\n            return {\n                'recommended_test': 'modified',\n                'reason': 'Autocorrélation modérée, utiliser test modifié',\n                'confidence': 'medium'\n            }\n        else:\n            return {\n                'recommended_test': 'prewhitened',\n                'reason': 'Autocorrélation forte, pré-blanchiment recommandé',\n                'confidence': 'low' if prewhitened_mk is None else 'medium'\n            }\n    \n    def _create_empty_autocorr_result(self, fraction, variable):\n        \"\"\"Crée un résultat vide pour l'autocorrélation\"\"\"\n        return {\n            'fraction': fraction,\n            'label': self.class_labels[fraction],\n            'variable': variable,\n            'n_obs': 0,\n            'error': True,\n            'autocorrelation': {\n                'lag1': np.nan,\n                'status': 'Indéterminé',\n                'significant': False\n            },\n            'recommendation': {\n                'recommended_test': 'none',\n                'reason': 'Données insuffisantes',\n                'confidence': 'none'\n            }\n        }\n    \n    def _create_empty_bootstrap_result(self, fraction, variable):\n        \"\"\"Crée un résultat vide pour le bootstrap\"\"\"\n        return {\n            'fraction': fraction,\n            'label': self.class_labels[fraction],\n            'variable': variable,\n            'n_obs': 0,\n            'error': True,\n            'n_bootstrap': 0,\n            'n_successful': 0\n        }\n    \n    def _print_autocorr_results(self, result):\n        \"\"\"Affiche les résultats d'autocorrélation\"\"\"\n        autocorr = result['autocorrelation']\n        rec = result['recommendation']\n        \n        print(f\"  🔄 Autocorrélation lag-1: {autocorr['lag1']:.3f} ({autocorr['status']})\")\n        \n        if 'mann_kendall_original' in result:\n            orig = result['mann_kendall_original']\n            print(f\"  📊 Test original: {orig['trend']} (p={format_pvalue(orig['p_value'])})\")\n        \n        if result.get('mann_kendall_modified'):\n            mod = result['mann_kendall_modified']\n            print(f\"  🔧 Test modifié: {mod['trend']} (p={format_pvalue(mod['p_value'])})\")\n        \n        if result.get('mann_kendall_prewhitened'):\n            pre = result['mann_kendall_prewhitened']\n            print(f\"  🧹 Test pré-blanchi: {pre['trend']} (p={format_pvalue(pre['p_value'])})\")\n        \n        print(f\"  💡 Recommandation: {rec['recommended_test']} ({rec['confidence']})\")\n        print(f\"     Raison: {rec['reason']}\")\n    \n    def _print_bootstrap_results(self, result):\n        \"\"\"Affiche les résultats bootstrap\"\"\"\n        slope = result['slope_bootstrap']\n        pval = result['pvalue_bootstrap']\n        \n        print(f\"  🎯 Bootstrap réussi: {result['n_successful']}/{result['n_bootstrap']} itérations\")\n        print(f\"  📐 Pente médiane: {slope['median']:.6f}/décennie\")\n        print(f\"  🎯 IC 95%: [{slope['ci_95_low']:.6f}, {slope['ci_95_high']:.6f}]\")\n        print(f\"  📊 P-value moyenne: {format_pvalue(pval['mean'])}\")\n        print(f\"  ✅ Tests significatifs: {pval['significant_proportion']:.1%}\")\n    \n    def get_autocorr_summary_table(self, variable='mean'):\n        \"\"\"\n        Génère un tableau de résumé des analyses d'autocorrélation\n        \n        Args:\n            variable (str): Variable analysée\n            \n        Returns:\n            pd.DataFrame: Tableau de résumé\n        \"\"\"\n        if f'autocorr_{variable}' not in self.results:\n            raise ValueError(f\"Analyses d'autocorrélation non effectuées pour {variable}\")\n        \n        results = self.results[f'autocorr_{variable}']\n        summary_data = []\n        \n        for fraction, result in results.items():\n            if result.get('error', False):\n                continue\n            \n            autocorr = result['autocorrelation']\n            rec = result['recommendation']\n            \n            # Test recommandé\n            if rec['recommended_test'] == 'original':\n                recommended_result = result.get('mann_kendall_original', {})\n            elif rec['recommended_test'] == 'modified':\n                recommended_result = result.get('mann_kendall_modified', {})\n            elif rec['recommended_test'] == 'prewhitened':\n                recommended_result = result.get('mann_kendall_prewhitened', {})\n            else:\n                recommended_result = {}\n            \n            summary_data.append({\n                'Fraction': result['label'],\n                'N_obs': result['n_obs'],\n                'Autocorr_lag1': autocorr['lag1'],\n                'Autocorr_status': autocorr['status'],\n                'Test_recommande': rec['recommended_test'],\n                'Confiance_recommandation': rec['confidence'],\n                'Tendance_finale': recommended_result.get('trend', 'N/A'),\n                'P_value_finale': recommended_result.get('p_value', np.nan)\n            })\n        \n        return pd.DataFrame(summary_data)\n    \n    def print_advanced_summary(self, variable='mean'):\n        \"\"\"\n        Affiche un résumé des analyses avancées\n        \"\"\"\n        print_section_header(\"Résumé des analyses avancées\", level=2)\n        \n        # Résumé autocorrélation\n        if f'autocorr_{variable}' in self.results:\n            autocorr_results = self.results[f'autocorr_{variable}']\n            \n            autocorr_counts = {'weak': 0, 'moderate': 0, 'strong': 0}\n            test_recommendations = {'original': 0, 'modified': 0, 'prewhitened': 0}\n            \n            for fraction, result in autocorr_results.items():\n                if result.get('error', False):\n                    continue\n                \n                autocorr_val = abs(result['autocorrelation']['lag1'])\n                rec_test = result['recommendation']['recommended_test']\n                \n                if autocorr_val <= ANALYSIS_CONFIG['autocorr_thresholds']['weak']:\n                    autocorr_counts['weak'] += 1\n                elif autocorr_val <= ANALYSIS_CONFIG['autocorr_thresholds']['moderate']:\n                    autocorr_counts['moderate'] += 1\n                else:\n                    autocorr_counts['strong'] += 1\n                \n                if rec_test in test_recommendations:\n                    test_recommendations[rec_test] += 1\n            \n            print(\"🔄 Distribution d'autocorrélation:\")\n            print(f\"  🟢 Faible: {autocorr_counts['weak']} fractions\")\n            print(f\"  🟡 Modérée: {autocorr_counts['moderate']} fractions\")\n            print(f\"  🔴 Forte: {autocorr_counts['strong']} fractions\")\n            \n            print(\"\\n💡 Tests recommandés:\")\n            print(f\"  📊 Original: {test_recommendations['original']} fractions\")\n            print(f\"  🔧 Modifié: {test_recommendations['modified']} fractions\")\n            print(f\"  🧹 Pré-blanchi: {test_recommendations['prewhitened']} fractions\")\n        \n        # Résumé bootstrap\n        if f'bootstrap_{variable}' in self.results:\n            bootstrap_results = self.results[f'bootstrap_{variable}']\n            \n            successful_bootstraps = 0\n            total_fractions = 0\n            \n            for fraction, result in bootstrap_results.items():\n                if not result.get('error', False):\n                    total_fractions += 1\n                    if result['n_successful'] > 0:\n                        successful_bootstraps += 1\n            \n            print(f\"\\n🎯 Bootstrap:\")\n            print(f\"  ✅ Réussi pour {successful_bootstraps}/{total_fractions} fractions\")\n            \n            if successful_bootstraps > 0:\n                print(f\"  🔄 {ANALYSIS_CONFIG['bootstrap_iterations']} itérations par fraction\")\n        \n        else:\n            print(\"\\n❌ Analyses avancées non effectuées\")"