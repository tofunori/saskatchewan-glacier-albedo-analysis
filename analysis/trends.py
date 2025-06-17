"""
Calculateur de tendances statistiques pour l'analyse d'albédo
============================================================

Ce module contient tous les calculs statistiques pour détecter les tendances
dans les données d'albédo : Mann-Kendall, Sen's slope, autocorrélation, bootstrap.
"""

import numpy as np
import pandas as pd
from sklearn.utils import resample
from config import (FRACTION_CLASSES, CLASS_LABELS, TREND_SYMBOLS, 
                     get_significance_marker, ANALYSIS_CONFIG)
from utils.helpers import (perform_mann_kendall_test, calculate_sen_slope, 
                            calculate_autocorrelation, prewhiten_series, 
                            validate_data, print_section_header, format_pvalue)

class TrendCalculator:
    """
    Calculateur pour les analyses de tendances statistiques
    """
    
    def __init__(self, data_handler):
        """
        Initialise le calculateur de tendances
        
        Args:
            data_handler: Instance d'AlbedoDataHandler avec données chargées
        """
        self.data_handler = data_handler
        self.data = data_handler.data
        self.fraction_classes = FRACTION_CLASSES
        self.class_labels = CLASS_LABELS
        self.results = {}
        
    def calculate_basic_trends(self, variable='mean'):
        """
        Calcule les tendances Mann-Kendall et pente de Sen pour chaque fraction
        
        Args:
            variable (str): Variable à analyser ('mean' ou 'median')
            
        Returns:
            dict: Résultats des analyses de tendances
        """
        print_section_header(f"Analyses de tendances de base - Variable: {variable}", level=2)
        
        results = {}
        
        for fraction in self.fraction_classes:
            print(f"\n🔍 Analyse: {self.class_labels[fraction]}")
            
            try:
                # Extraire les données pour cette fraction
                fraction_data = self.data_handler.get_fraction_data(
                    fraction, variable, dropna=True
                )
                
                if len(fraction_data) < 10:
                    print(f"  ⚠️  Données insuffisantes ({len(fraction_data)} observations)")
                    results[fraction] = self._create_empty_result(fraction, variable)
                    continue
                
                # Préparer les données
                times = fraction_data['decimal_year'].values
                values = fraction_data['value'].values
                
                # Valider les données
                is_valid, clean_values, n_removed = validate_data(values)
                if n_removed > 0:
                    print(f"  📝 {n_removed} valeurs manquantes supprimées")
                
                if not is_valid:
                    print(f"  ❌ Données insuffisantes après nettoyage")
                    results[fraction] = self._create_empty_result(fraction, variable)
                    continue
                
                # Synchroniser les temps avec les valeurs nettoyées
                clean_times = times[~np.isnan(values)]
                
                # Test de Mann-Kendall
                mk_result = perform_mann_kendall_test(clean_values)
                
                # Pente de Sen
                sen_result = calculate_sen_slope(clean_times, clean_values)
                
                # Autocorrélation
                autocorr = calculate_autocorrelation(clean_values, lag=1)
                
                # Stocker les résultats
                results[fraction] = {
                    'fraction': fraction,
                    'label': self.class_labels[fraction],
                    'variable': variable,
                    'n_obs': len(clean_values),
                    'n_removed': n_removed,
                    'data_range': {
                        'start': fraction_data['date'].min(),
                        'end': fraction_data['date'].max()
                    },
                    'mann_kendall': mk_result,
                    'sen_slope': sen_result,
                    'autocorrelation': {
                        'lag1': autocorr,
                        'significant': abs(autocorr) > 0.1
                    },
                    'data': {
                        'times': clean_times,
                        'values': clean_values
                    }
                }
                
                # Affichage des résultats
                self._print_fraction_results(results[fraction])
                
            except Exception as e:
                print(f"  ❌ Erreur lors de l'analyse: {e}")
                results[fraction] = self._create_empty_result(fraction, variable)
        
        self.results[f'basic_trends_{variable}'] = results
        return results
    
    def calculate_monthly_trends(self, variable='mean'):
        """
        Analyse les tendances par mois
        
        Args:
            variable (str): Variable à analyser ('mean' ou 'median')
            
        Returns:
            dict: Résultats des analyses mensuelles
        """
        print_section_header(f"Analyses mensuelles - Variable: {variable}", level=2)
        
        from config import MONTH_NAMES
        results = {}
        
        # Analyser chaque mois de la saison de fonte
        for month in [6, 7, 8, 9]:
            month_name = MONTH_NAMES[month]
            print(f"\n📅 Analyse pour {month_name} (mois {month})")
            
            # Filtrer les données pour ce mois
            month_data = self.data[self.data['month'] == month].copy()
            
            if len(month_data) < 5:
                print(f"  ⚠️  Données insuffisantes pour {month_name} ({len(month_data)} observations)")
                continue
            
            # Analyser chaque fraction pour ce mois
            month_results = {}
            
            for fraction in self.fraction_classes:
                col_name = f"{fraction}_{variable}"
                
                if col_name not in month_data.columns:
                    continue
                
                # Extraire les données valides
                valid_data = month_data[['decimal_year', col_name]].dropna()
                
                if len(valid_data) < 5:
                    continue
                
                times = valid_data['decimal_year'].values
                values = valid_data[col_name].values
                
                # Test Mann-Kendall
                mk_result = perform_mann_kendall_test(values)
                
                # Pente de Sen
                sen_result = calculate_sen_slope(times, values)
                
                month_results[fraction] = {
                    'fraction': fraction,
                    'label': self.class_labels[fraction],
                    'n_obs': len(valid_data),
                    'mann_kendall': mk_result,
                    'sen_slope': sen_result,
                    'data': {
                        'times': times,
                        'values': values
                    }
                }
                
                # Afficher résultat bref
                trend = mk_result['trend']
                p_val = mk_result['p_value']
                slope_decade = sen_result['slope_per_decade']
                significance = get_significance_marker(p_val)
                
                print(f"    {self.class_labels[fraction]}: {trend} {significance} "
                      f"({slope_decade:.6f}/décennie)")
            
            results[month] = {
                'month': month,
                'month_name': month_name,
                'fractions': month_results
            }
        
        self.results[f'monthly_trends_{variable}'] = results
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
                fraction_data = self.data_handler.get_fraction_data(
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
                        mk_result = perform_mann_kendall_test(boot_values)
                        bootstrap_pvalues.append(mk_result['p_value'])
                        
                        # Calcul de la pente Sen
                        if len(boot_values) > 5:
                            sen_result = calculate_sen_slope(boot_times, boot_values)
                            bootstrap_slopes.append(sen_result['slope_per_decade'])
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
                        'bootstrap_pvalues': bootstrap_pvalues
                    }
                    
                    # Affichage des résultats
                    self._print_bootstrap_results(results[fraction])
                    
                else:
                    print(f"  ❌ Échec de toutes les itérations bootstrap")
                    results[fraction] = self._create_empty_bootstrap_result(fraction, variable)
                    
            except Exception as e:
                print(f"  ❌ Erreur lors du bootstrap: {e}")
                results[fraction] = self._create_empty_bootstrap_result(fraction, variable)
        
        self.results[f'bootstrap_{variable}'] = results
        return results
    
    def _create_empty_result(self, fraction, variable):
        """
        Crée un résultat vide pour les cas d'erreur
        """
        return {
            'fraction': fraction,
            'label': self.class_labels[fraction],
            'variable': variable,
            'n_obs': 0,
            'n_removed': 0,
            'error': True,
            'mann_kendall': {
                'trend': 'no trend',
                'p_value': np.nan,
                'tau': np.nan,
                's': np.nan,
                'z': np.nan
            },
            'sen_slope': {
                'slope': np.nan,
                'slope_per_decade': np.nan,
                'intercept': np.nan
            },
            'autocorrelation': {
                'lag1': np.nan,
                'significant': False
            }
        }
    
    def _create_empty_bootstrap_result(self, fraction, variable):
        """Crée un résultat vide pour le bootstrap"""
        return {
            'fraction': fraction,
            'label': self.class_labels[fraction],
            'variable': variable,
            'n_obs': 0,
            'error': True,
            'n_bootstrap': 0,
            'n_successful': 0
        }
    
    def _print_fraction_results(self, result):
        """
        Affiche les résultats pour une fraction
        """
        mk = result['mann_kendall']
        sen = result['sen_slope']
        
        # Symbole de tendance
        trend_symbol = TREND_SYMBOLS.get(mk['trend'], '❓')
        significance = get_significance_marker(mk['p_value'])
        
        print(f"  📈 Tendance: {trend_symbol} {mk['trend']} ({significance})")
        print(f"  📊 p-value: {format_pvalue(mk['p_value'])}")
        print(f"  📏 Tau de Kendall: {mk['tau']:.4f}")
        
        if not np.isnan(sen['slope_per_decade']):
            print(f"  📐 Pente Sen: {sen['slope_per_decade']:.6f}/décennie")
            
            if 'confidence_interval' in sen:
                ci_low = sen['confidence_interval']['low_per_decade']
                ci_high = sen['confidence_interval']['high_per_decade']
                if not (np.isnan(ci_low) or np.isnan(ci_high)):
                    print(f"  🎯 IC 95%: [{ci_low:.6f}, {ci_high:.6f}]/décennie")
        
        # Autocorrélation
        autocorr = result['autocorrelation']['lag1']
        if not np.isnan(autocorr):
            autocorr_status = "⚠️  Significative" if abs(autocorr) > 0.1 else "✓ Faible"
            print(f"  🔄 Autocorrélation: {autocorr:.3f} ({autocorr_status})")
    
    def _print_bootstrap_results(self, result):
        """Affiche les résultats bootstrap"""
        slope = result['slope_bootstrap']
        pval = result['pvalue_bootstrap']
        
        print(f"  🎯 Bootstrap réussi: {result['n_successful']}/{result['n_bootstrap']} itérations")
        print(f"  📐 Pente médiane: {slope['median']:.6f}/décennie")
        print(f"  🎯 IC 95%: [{slope['ci_95_low']:.6f}, {slope['ci_95_high']:.6f}]")
        print(f"  📊 P-value moyenne: {format_pvalue(pval['mean'])}")
        print(f"  ✅ Tests significatifs: {pval['significant_proportion']:.1%}")
    
    def get_summary_table(self, variable='mean'):
        """
        Génère un tableau de résumé des tendances
        
        Args:
            variable (str): Variable analysée
            
        Returns:
            pd.DataFrame: Tableau de résumé
        """
        if f'basic_trends_{variable}' not in self.results:
            raise ValueError(f"Analyses non effectuées pour {variable}")
        
        results = self.results[f'basic_trends_{variable}']
        summary_data = []
        
        for fraction, result in results.items():
            if result.get('error', False):
                continue
                
            mk = result['mann_kendall']
            sen = result['sen_slope']
            
            summary_data.append({
                'Fraction': result['label'],
                'N_obs': result['n_obs'],
                'Tendance': mk['trend'],
                'P_value': mk['p_value'],
                'Significativité': get_significance_marker(mk['p_value']),
                'Tau': mk['tau'],
                'Pente_Sen_decade': sen['slope_per_decade'],
                'IC_bas_decade': sen.get('confidence_interval', {}).get('low_per_decade', np.nan),
                'IC_haut_decade': sen.get('confidence_interval', {}).get('high_per_decade', np.nan),
                'Autocorr_lag1': result['autocorrelation']['lag1']
            })
        
        return pd.DataFrame(summary_data)
    
    def print_summary(self, variable='mean'):
        """
        Affiche un résumé des analyses
        """
        print_section_header("Résumé des analyses de tendances", level=2)
        
        if f'basic_trends_{variable}' not in self.results:
            print("❌ Aucune analyse disponible")
            return
        
        results = self.results[f'basic_trends_{variable}']
        
        # Compter les tendances
        trends_count = {'increasing': 0, 'decreasing': 0, 'no trend': 0}
        significant_trends = []
        
        for fraction, result in results.items():
            if result.get('error', False):
                continue
                
            trend = result['mann_kendall']['trend']
            p_value = result['mann_kendall']['p_value']
            
            trends_count[trend] += 1
            
            if p_value < 0.05:
                significant_trends.append({
                    'fraction': result['label'],
                    'trend': trend,
                    'p_value': p_value,
                    'slope_decade': result['sen_slope']['slope_per_decade']
                })
        
        print(f"📊 Tendances détectées:")
        print(f"  📈 Croissantes: {trends_count['increasing']}")
        print(f"  📉 Décroissantes: {trends_count['decreasing']}")
        print(f"  ➡️  Pas de tendance: {trends_count['no trend']}")
        
        if significant_trends:
            print(f"\n🎯 Tendances significatives (p < 0.05):")
            for trend in significant_trends:
                symbol = TREND_SYMBOLS[trend['trend']]
                print(f"  {symbol} {trend['fraction']}: {format_pvalue(trend['p_value'])} "
                      f"({trend['slope_decade']:.6f}/décennie)")
        else:
            print("\n❌ Aucune tendance significative détectée")