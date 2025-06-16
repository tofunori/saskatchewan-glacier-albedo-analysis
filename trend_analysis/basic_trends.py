"""
Analyses de tendances de base (Mann-Kendall et Sen's slope)
==========================================================

Ce module contient les analyses statistiques de base pour détecter les tendances
dans les données d'albédo du glacier Saskatchewan.
"""

import numpy as np
import pandas as pd
from scipy.stats import theilslopes

# Gérer les imports relatifs et absolus
try:
    from .config import FRACTION_CLASSES, CLASS_LABELS, TREND_SYMBOLS, get_significance_marker
    from .utils import (manual_mann_kendall, check_pymannkendall, validate_data, 
                       print_section_header, format_pvalue, calculate_autocorrelation)
except ImportError:
    from config import FRACTION_CLASSES, CLASS_LABELS, TREND_SYMBOLS, get_significance_marker
    from utils import (manual_mann_kendall, check_pymannkendall, validate_data, 
                      print_section_header, format_pvalue, calculate_autocorrelation)

# Import conditionnel de pymannkendall sera fait dans les fonctions

class BasicTrendAnalyzer:
    """
    Analyseur pour les tests de tendance de base (Mann-Kendall et Sen's slope)
    """
    
    def __init__(self, data_loader):
        """
        Initialise l'analyseur de tendances de base
        
        Args:
            data_loader: Instance de SaskatchewanDataLoader avec données chargées
        """
        self.data_loader = data_loader
        self.data = data_loader.data
        self.fraction_classes = FRACTION_CLASSES
        self.class_labels = CLASS_LABELS
        self.results = {}
        
    def calculate_trends(self, variable='mean'):
        """
        Calcule les tendances Mann-Kendall et pente de Sen pour chaque fraction
        
        Args:
            variable (str): Variable à analyser ('mean' ou 'median')
            
        Returns:
            dict: Résultats des analyses de tendances
        """
        print_section_header(f"Analyses de tendances - Variable: {variable}", level=2)
        
        results = {}
        
        for fraction in self.fraction_classes:
            print(f"\n🔍 Analyse: {self.class_labels[fraction]}")
            
            # Extraire les données pour cette fraction
            try:
                fraction_data = self.data_loader.get_fraction_data(
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
                mk_result = self._perform_mann_kendall(clean_values)
                
                # Pente de Sen
                sen_result = self._calculate_sen_slope(clean_times, clean_values)
                
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
        
        self.results[f'trends_{variable}'] = results
        return results
    
    def _perform_mann_kendall(self, values):
        """
        Effectue le test de Mann-Kendall
        
        Args:
            values (array): Valeurs à analyser
            
        Returns:
            dict: Résultats du test Mann-Kendall
        """
        if check_pymannkendall():
            try:
                import pymannkendall as mk
                mk_result = mk.original_test(values)
                return {
                    'trend': mk_result.trend,
                    'p_value': mk_result.p,
                    'tau': mk_result.Tau,
                    's': mk_result.s,
                    'z': mk_result.z,
                    'method': 'pymannkendall'
                }
            except Exception as e:
                print(f"    ⚠️  Erreur pymannkendall: {e}, utilisation manuelle")
                return manual_mann_kendall(values)
        else:
            return manual_mann_kendall(values)
    
    def _calculate_sen_slope(self, times, values):
        """
        Calcule la pente de Sen et intervalle de confiance
        
        Args:
            times (array): Temps (années décimales)
            values (array): Valeurs d'albédo
            
        Returns:
            dict: Résultats de la pente de Sen
        """
        try:
            # Calcul avec theilslopes de scipy
            slope, intercept, low_slope, high_slope = theilslopes(values, times, 0.95)
            
            return {
                'slope': slope,
                'slope_per_decade': slope * 10,  # Pente par décennie
                'intercept': intercept,
                'confidence_interval': {
                    'low': low_slope,
                    'high': high_slope,
                    'low_per_decade': low_slope * 10,
                    'high_per_decade': high_slope * 10
                },
                'method': 'theilslopes'
            }
        except Exception as e:
            print(f"    ⚠️  Erreur calcul pente Sen: {e}")
            return {
                'slope': np.nan,
                'slope_per_decade': np.nan,
                'intercept': np.nan,
                'confidence_interval': {
                    'low': np.nan,
                    'high': np.nan,
                    'low_per_decade': np.nan,
                    'high_per_decade': np.nan
                },
                'method': 'failed'
            }
    
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
    
    def get_summary_table(self, variable='mean'):
        """
        Génère un tableau de résumé des tendances
        
        Args:
            variable (str): Variable analysée
            
        Returns:
            pd.DataFrame: Tableau de résumé
        """
        if f'trends_{variable}' not in self.results:
            raise ValueError(f"Analyses non effectuées pour {variable}")
        
        results = self.results[f'trends_{variable}']
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
        
        if f'trends_{variable}' not in self.results:
            print("❌ Aucune analyse disponible")
            return
        
        results = self.results[f'trends_{variable}']
        
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