"""
Analyseur de comparaison entre datasets MODIS
=============================================

Ce module fournit des outils pour comparer les tendances et patterns
entre les produits MCD43A3 et MOD10A1, incluant les analyses statistiques
et la détection de différences significatives.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import warnings

# Import from package
from config import (
    FRACTION_CLASSES, CLASS_LABELS, COMPARISON_CONFIG,
    ANALYSIS_CONFIG, FRACTION_COLORS
)
from utils.helpers import print_section_header, ensure_directory_exists
from analysis.trends import TrendCalculator

class ComparisonAnalyzer:
    """
    Analyseur pour comparer les datasets MCD43A3 et MOD10A1
    """
    
    def __init__(self, comparison_data):
        """
        Initialise l'analyseur de comparaison
        
        Args:
            comparison_data (dict): Données de comparaison du DatasetManager
        """
        self.comparison_data = comparison_data
        self.merged_data = comparison_data['merged']
        self.mcd43a3_data = comparison_data['mcd43a3']
        self.mod10a1_data = comparison_data['mod10a1']
        self.results = {}
        
    def calculate_correlations(self, method='pearson'):
        """
        Calcule les corrélations entre les datasets pour chaque fraction
        
        Args:
            method (str): 'pearson' ou 'spearman'
            
        Returns:
            dict: Résultats des corrélations
        """
        print_section_header(f"Calcul des corrélations ({method})", level=3)
        
        correlations = {}
        
        for fraction in FRACTION_CLASSES:
            mcd_col = f'mcd43a3_{fraction}_mean'
            mod_col = f'mod10a1_{fraction}_mean'
            
            if mcd_col in self.merged_data.columns and mod_col in self.merged_data.columns:
                # Données valides
                valid_data = self.merged_data[[mcd_col, mod_col]].dropna()
                
                if len(valid_data) >= 10:  # Minimum pour correlation fiable
                    if method == 'pearson':
                        corr, p_value = pearsonr(valid_data[mcd_col], valid_data[mod_col])
                    else:  # spearman
                        corr, p_value = spearmanr(valid_data[mcd_col], valid_data[mod_col])
                    
                    # Calcul de l'intervalle de confiance (approximatif)
                    n = len(valid_data)
                    ci_95 = 1.96 / np.sqrt(n - 3)  # Fisher transform approximation
                    
                    correlations[fraction] = {
                        'correlation': corr,
                        'p_value': p_value,
                        'n_observations': n,
                        'significant': p_value < COMPARISON_CONFIG['significance_level'],
                        'ci_lower': max(-1, corr - ci_95),
                        'ci_upper': min(1, corr + ci_95),
                        'strength': self._assess_correlation_strength(corr)
                    }
                    
                    print(f"  {CLASS_LABELS[fraction]}: r = {corr:.3f} (p = {p_value:.4f}, n = {n})")
                else:
                    correlations[fraction] = {
                        'correlation': np.nan,
                        'p_value': np.nan,
                        'n_observations': len(valid_data),
                        'significant': False,
                        'error': 'Données insuffisantes'
                    }
                    print(f"  {CLASS_LABELS[fraction]}: Données insuffisantes (n = {len(valid_data)})")
        
        self.results['correlations'] = correlations
        return correlations
    
    def _assess_correlation_strength(self, corr):
        """
        Évalue la force de la corrélation
        
        Args:
            corr (float): Coefficient de corrélation
            
        Returns:
            str: Description de la force
        """
        abs_corr = abs(corr)
        if abs_corr >= 0.8:
            return "Très forte"
        elif abs_corr >= 0.6:
            return "Forte"
        elif abs_corr >= 0.4:
            return "Modérée"
        elif abs_corr >= 0.2:
            return "Faible"
        else:
            return "Très faible"
    
    def calculate_differences(self):
        """
        Calcule les différences statistiques entre les datasets
        
        Returns:
            dict: Statistiques des différences
        """
        print_section_header("Calcul des différences (MOD10A1 - MCD43A3)", level=3)
        
        differences = {}
        
        for fraction in FRACTION_CLASSES:
            mcd_col = f'mcd43a3_{fraction}_mean'
            mod_col = f'mod10a1_{fraction}_mean'
            
            if mcd_col in self.merged_data.columns and mod_col in self.merged_data.columns:
                # Données valides
                valid_data = self.merged_data[[mcd_col, mod_col]].dropna()
                
                if len(valid_data) >= 10:
                    diff = valid_data[mod_col] - valid_data[mcd_col]
                    
                    # Test de Student pour différence de moyenne
                    t_stat, t_p_value = stats.ttest_1samp(diff, 0)
                    
                    # Test de Wilcoxon (non-paramétrique)
                    try:
                        w_stat, w_p_value = stats.wilcoxon(diff, alternative='two-sided')
                    except ValueError:
                        w_stat, w_p_value = np.nan, np.nan
                    
                    differences[fraction] = {
                        'mean_difference': diff.mean(),
                        'median_difference': diff.median(),
                        'std_difference': diff.std(),
                        'rmse': np.sqrt((diff ** 2).mean()),
                        'mae': abs(diff).mean(),
                        'percentile_25': diff.quantile(0.25),
                        'percentile_75': diff.quantile(0.75),
                        'n_observations': len(diff),
                        'ttest_statistic': t_stat,
                        'ttest_p_value': t_p_value,
                        'wilcoxon_statistic': w_stat,
                        'wilcoxon_p_value': w_p_value,
                        'significant_difference': t_p_value < COMPARISON_CONFIG['significance_level'],
                        'bias_direction': 'MOD10A1 > MCD43A3' if diff.mean() > 0 else 'MOD10A1 < MCD43A3'
                    }
                    
                    print(f"  {CLASS_LABELS[fraction]}:")
                    print(f"    Différence moyenne: {diff.mean():+.4f} ± {diff.std():.4f}")
                    print(f"    RMSE: {differences[fraction]['rmse']:.4f}")
                    print(f"    Test t: p = {t_p_value:.4f} {'*' if t_p_value < 0.05 else ''}")
        
        self.results['differences'] = differences
        return differences
    
    def analyze_temporal_patterns(self):
        """
        Analyse les patterns temporels des différences
        
        Returns:
            dict: Analyse temporelle
        """
        print_section_header("Analyse des patterns temporels", level=3)
        
        temporal_results = {}
        
        # Analyse par mois
        monthly_analysis = {}
        for month in [6, 7, 8, 9]:  # Juin à Septembre
            month_data = self.merged_data[self.merged_data['month'] == month]
            monthly_analysis[month] = self._analyze_month_differences(month_data, month)
        
        # Analyse par année
        yearly_analysis = {}
        for year in sorted(self.merged_data['year'].unique()):
            year_data = self.merged_data[self.merged_data['year'] == year]
            yearly_analysis[year] = self._analyze_year_differences(year_data, year)
        
        # Analyse de tendance des différences
        trend_analysis = self._analyze_difference_trends()
        
        temporal_results = {
            'monthly': monthly_analysis,
            'yearly': yearly_analysis,
            'trends': trend_analysis
        }
        
        self.results['temporal_patterns'] = temporal_results
        return temporal_results
    
    def _analyze_month_differences(self, month_data, month):
        """
        Analyse les différences pour un mois spécifique
        """
        month_results = {'month': month, 'fractions': {}}
        
        for fraction in FRACTION_CLASSES:
            mcd_col = f'mcd43a3_{fraction}_mean'
            mod_col = f'mod10a1_{fraction}_mean'
            
            if mcd_col in month_data.columns and mod_col in month_data.columns:
                valid_data = month_data[[mcd_col, mod_col]].dropna()
                
                if len(valid_data) >= 5:  # Minimum pour analyse mensuelle
                    diff = valid_data[mod_col] - valid_data[mcd_col]
                    
                    month_results['fractions'][fraction] = {
                        'mean_difference': diff.mean(),
                        'std_difference': diff.std(),
                        'n_observations': len(diff)
                    }
        
        return month_results
    
    def _analyze_year_differences(self, year_data, year):
        """
        Analyse les différences pour une année spécifique
        """
        year_results = {'year': year, 'fractions': {}}
        
        for fraction in FRACTION_CLASSES:
            mcd_col = f'mcd43a3_{fraction}_mean'
            mod_col = f'mod10a1_{fraction}_mean'
            
            if mcd_col in year_data.columns and mod_col in year_data.columns:
                valid_data = year_data[[mcd_col, mod_col]].dropna()
                
                if len(valid_data) >= 5:
                    diff = valid_data[mod_col] - valid_data[mcd_col]
                    
                    year_results['fractions'][fraction] = {
                        'mean_difference': diff.mean(),
                        'std_difference': diff.std(),
                        'n_observations': len(diff)
                    }
        
        return year_results
    
    def _analyze_difference_trends(self):
        """
        Analyse les tendances temporelles des différences
        """
        trend_results = {}
        
        for fraction in FRACTION_CLASSES:
            mcd_col = f'mcd43a3_{fraction}_mean'
            mod_col = f'mod10a1_{fraction}_mean'
            
            if mcd_col in self.merged_data.columns and mod_col in self.merged_data.columns:
                valid_data = self.merged_data[[mcd_col, mod_col, 'decimal_year']].dropna()
                
                if len(valid_data) >= 20:  # Minimum pour analyse de tendance
                    diff = valid_data[mod_col] - valid_data[mcd_col]
                    
                    # Régression linéaire de la différence vs temps
                    slope, intercept, r_value, p_value, std_err = stats.linregress(
                        valid_data['decimal_year'], diff
                    )
                    
                    trend_results[fraction] = {
                        'slope': slope,
                        'intercept': intercept,
                        'r_squared': r_value ** 2,
                        'p_value': p_value,
                        'std_error': std_err,
                        'significant_trend': p_value < COMPARISON_CONFIG['significance_level'],
                        'trend_direction': 'Divergence croissante' if slope > 0 else 'Convergence' if slope < 0 else 'Stable'
                    }
        
        return trend_results
    
    def compare_trend_analyses(self):
        """
        Compare les analyses de tendances Mann-Kendall entre les datasets
        
        Returns:
            dict: Comparaison des tendances
        """
        print_section_header("Comparaison des tendances Mann-Kendall", level=3)
        
        # Calculer les tendances pour chaque dataset
        mcd43a3_trends = self._calculate_mk_trends(self.mcd43a3_data, 'MCD43A3')
        mod10a1_trends = self._calculate_mk_trends(self.mod10a1_data, 'MOD10A1')
        
        # Comparer les résultats
        trend_comparison = {}
        
        for fraction in FRACTION_CLASSES:
            if fraction in mcd43a3_trends and fraction in mod10a1_trends:
                mcd_result = mcd43a3_trends[fraction]
                mod_result = mod10a1_trends[fraction]
                
                trend_comparison[fraction] = {
                    'mcd43a3': mcd_result,
                    'mod10a1': mod_result,
                    'agreement': {
                        'same_direction': np.sign(mcd_result.get('slope', 0)) == np.sign(mod_result.get('slope', 0)),
                        'both_significant': mcd_result.get('significant', False) and mod_result.get('significant', False),
                        'slope_difference': abs(mod_result.get('slope', 0) - mcd_result.get('slope', 0)),
                        'agreement_level': self._assess_trend_agreement(mcd_result, mod_result)
                    }
                }
        
        self.results['trend_comparison'] = trend_comparison
        return trend_comparison
    
    def _calculate_mk_trends(self, data, dataset_name):
        """
        Calcule les tendances Mann-Kendall pour un dataset
        """
        trends = {}
        
        # Importer pyMannKendall directement pour éviter les problèmes avec TrendCalculator
        try:
            import pyMannKendall as mk
        except ImportError:
            print("⚠️ pyMannKendall non installé. Installation de la méthode alternative.")
            # Méthode alternative sans pyMannKendall
            return self._calculate_mk_trends_simple(data, dataset_name)
        
        for fraction in FRACTION_CLASSES:
            col_name = f'{fraction}_mean'
            if col_name in data.columns:
                fraction_data = data[['decimal_year', col_name]].dropna()
                
                if len(fraction_data) >= 10:
                    # Calculer directement avec pyMannKendall
                    values = fraction_data[col_name].values
                    
                    # Test Mann-Kendall
                    mk_result = mk.original_test(values)
                    
                    # Pente de Sen
                    try:
                        sen_result = mk.sens_slope(values)
                        slope = sen_result.slope
                    except:
                        slope = np.nan
                    
                    trends[fraction] = {
                        'dataset': dataset_name,
                        'tau': mk_result.Tau,
                        'p_value': mk_result.p,
                        'slope': slope * 10,  # Convertir en décennie
                        'significant': mk_result.p < COMPARISON_CONFIG['significance_level'],
                        'trend_direction': mk_result.trend,
                        'n_observations': len(fraction_data)
                    }
        
        return trends
    
    def _calculate_mk_trends_simple(self, data, dataset_name):
        """
        Calcule les tendances Mann-Kendall de manière simplifiée sans pyMannKendall
        """
        trends = {}
        
        for fraction in FRACTION_CLASSES:
            col_name = f'{fraction}_mean'
            if col_name in data.columns:
                fraction_data = data[['decimal_year', col_name]].dropna()
                
                if len(fraction_data) >= 10:
                    # Régression linéaire simple comme approximation
                    x = fraction_data['decimal_year'].values
                    y = fraction_data[col_name].values
                    
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                    
                    trends[fraction] = {
                        'dataset': dataset_name,
                        'tau': r_value,  # Utiliser r comme approximation
                        'p_value': p_value,
                        'slope': slope * 10,  # Convertir en décennie
                        'significant': p_value < COMPARISON_CONFIG['significance_level'],
                        'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'no trend',
                        'n_observations': len(fraction_data)
                    }
        
        return trends
    
    def _assess_trend_agreement(self, trend1, trend2):
        """
        Évalue l'accord entre deux analyses de tendance
        """
        # Vérifier si les deux tendances sont significatives
        if not (trend1.get('significant', False) and trend2.get('significant', False)):
            return "Non comparable (au moins une tendance non significative)"
        
        # Vérifier la direction
        same_direction = np.sign(trend1.get('slope', 0)) == np.sign(trend2.get('slope', 0))
        
        if not same_direction:
            return "Désaccord (directions opposées)"
        
        # Comparer les magnitudes
        slope1 = abs(trend1.get('slope', 0))
        slope2 = abs(trend2.get('slope', 0))
        ratio = min(slope1, slope2) / max(slope1, slope2) if max(slope1, slope2) > 0 else 0
        
        if ratio > 0.8:
            return "Très bon accord"
        elif ratio > 0.6:
            return "Bon accord"
        elif ratio > 0.4:
            return "Accord modéré"
        else:
            return "Faible accord (magnitudes très différentes)"
    
    def export_comparison_results(self, output_dir="results"):
        """
        Exporte tous les résultats de comparaison
        
        Args:
            output_dir (str): Répertoire de sortie
        """
        ensure_directory_exists(output_dir)
        
        # Export des corrélations
        if 'correlations' in self.results:
            corr_df = pd.DataFrame(self.results['correlations']).T
            corr_path = f"{output_dir}/correlations_comparison.csv"
            corr_df.to_csv(corr_path)
            print(f"✓ Corrélations exportées: {corr_path}")
        
        # Export des différences
        if 'differences' in self.results:
            diff_df = pd.DataFrame(self.results['differences']).T
            diff_path = f"{output_dir}/differences_comparison.csv"
            diff_df.to_csv(diff_path)
            print(f"✓ Différences exportées: {diff_path}")
        
        # Export des comparaisons de tendances
        if 'trend_comparison' in self.results:
            trend_data = []
            for fraction, data in self.results['trend_comparison'].items():
                row = {
                    'fraction': fraction,
                    'mcd43a3_slope': data['mcd43a3'].get('slope', np.nan),
                    'mcd43a3_p_value': data['mcd43a3'].get('p_value', np.nan),
                    'mcd43a3_significant': data['mcd43a3'].get('significant', False),
                    'mod10a1_slope': data['mod10a1'].get('slope', np.nan),
                    'mod10a1_p_value': data['mod10a1'].get('p_value', np.nan),
                    'mod10a1_significant': data['mod10a1'].get('significant', False),
                    'same_direction': data['agreement']['same_direction'],
                    'both_significant': data['agreement']['both_significant'],
                    'slope_difference': data['agreement']['slope_difference'],
                    'agreement_level': data['agreement']['agreement_level']
                }
                trend_data.append(row)
            
            trend_df = pd.DataFrame(trend_data)
            trend_path = f"{output_dir}/trend_comparison.csv"
            trend_df.to_csv(trend_path, index=False)
            print(f"✓ Comparaison des tendances exportée: {trend_path}")
    
    def print_summary(self):
        """
        Affiche un résumé complet de la comparaison
        """
        print_section_header("RÉSUMÉ DE LA COMPARAISON MCD43A3 vs MOD10A1", level=1)
        
        print(f"📊 Données analysées: {len(self.merged_data)} observations communes")
        print(f"📅 Période: {self.merged_data['date'].min().strftime('%Y-%m-%d')} → {self.merged_data['date'].max().strftime('%Y-%m-%d')}")
        
        # Résumé des corrélations
        if 'correlations' in self.results:
            print(f"\n🔗 CORRÉLATIONS:")
            for fraction, data in self.results['correlations'].items():
                if 'correlation' in data and not np.isnan(data['correlation']):
                    corr = data['correlation']
                    sig = "***" if data['p_value'] < 0.001 else "**" if data['p_value'] < 0.01 else "*" if data['p_value'] < 0.05 else "ns"
                    print(f"  {CLASS_LABELS[fraction]}: r = {corr:.3f} {sig} ({data['strength']})")
        
        # Résumé des différences
        if 'differences' in self.results:
            print(f"\n📏 DIFFÉRENCES MOYENNES (MOD10A1 - MCD43A3):")
            for fraction, data in self.results['differences'].items():
                diff = data['mean_difference']
                rmse = data['rmse']
                sig = "*" if data['significant_difference'] else ""
                direction = "+" if diff > 0 else ""
                print(f"  {CLASS_LABELS[fraction]}: {direction}{diff:.4f} {sig} (RMSE: {rmse:.4f})")
        
        # Résumé des tendances
        if 'trend_comparison' in self.results:
            print(f"\n📈 ACCORD DES TENDANCES:")
            for fraction, data in self.results['trend_comparison'].items():
                agreement = data['agreement']['agreement_level']
                same_dir = "✅" if data['agreement']['same_direction'] else "❌"
                both_sig = "✅" if data['agreement']['both_significant'] else "❌"
                print(f"  {CLASS_LABELS[fraction]}: {agreement} (Direction: {same_dir}, Significativité: {both_sig})")


class DatasetComparator:
    """
    Simple dataset comparator for Streamlit interface
    """
    
    def __init__(self, dataset1, dataset2):
        """
        Initialize comparator with two AlbedoDataHandler objects
        
        Args:
            dataset1: First AlbedoDataHandler (e.g., MCD43A3)
            dataset2: Second AlbedoDataHandler (e.g., MOD10A1)
        """
        self.dataset1 = dataset1
        self.dataset2 = dataset2
    
    def align_daily(self, fraction):
        """
        Align datasets by date for daily comparison
        
        Args:
            fraction (str): Fraction class to compare
            
        Returns:
            pd.DataFrame: Aligned data with columns ['date', 'mcd43a3', 'mod10a1']
        """
        try:
            col_name = f"{fraction}_mean"
            
            # Get data from both datasets
            data1 = self.dataset1.data[['date', col_name]].dropna()
            data2 = self.dataset2.data[['date', col_name]].dropna()
            
            # Merge on date
            merged = pd.merge(data1, data2, on='date', suffixes=('_1', '_2'))
            merged = merged.rename(columns={f'{col_name}_1': 'mcd43a3', f'{col_name}_2': 'mod10a1'})
            
            return merged
            
        except Exception as e:
            print(f"Error aligning data: {str(e)}")
            return pd.DataFrame()
    
    def align_16day(self, fraction):
        """
        Align datasets using 16-day averaging
        
        Args:
            fraction (str): Fraction class to compare
            
        Returns:
            pd.DataFrame: Aligned data
        """
        try:
            # For simplicity, use daily alignment for now
            # In a full implementation, this would do 16-day averaging
            return self.align_daily(fraction)
            
        except Exception as e:
            print(f"Error in 16-day alignment: {str(e)}")
            return pd.DataFrame()
    
    def align_monthly(self, fraction):
        """
        Align datasets using monthly averaging
        
        Args:
            fraction (str): Fraction class to compare
            
        Returns:
            pd.DataFrame: Monthly aligned data
        """
        try:
            col_name = f"{fraction}_mean"
            
            # Monthly aggregation for both datasets
            data1 = self.dataset1.data[['date', col_name]].dropna()
            data2 = self.dataset2.data[['date', col_name]].dropna()
            
            # Add year-month column
            data1['year_month'] = data1['date'].dt.to_period('M')
            data2['year_month'] = data2['date'].dt.to_period('M')
            
            # Group by month and calculate means
            monthly1 = data1.groupby('year_month')[col_name].mean().reset_index()
            monthly2 = data2.groupby('year_month')[col_name].mean().reset_index()
            
            # Merge on year_month
            merged = pd.merge(monthly1, monthly2, on='year_month', suffixes=('_1', '_2'))
            merged['date'] = merged['year_month'].dt.to_timestamp()
            merged = merged.rename(columns={f'{col_name}_1': 'mcd43a3', f'{col_name}_2': 'mod10a1'})
            
            return merged[['date', 'mcd43a3', 'mod10a1']]
            
        except Exception as e:
            print(f"Error in monthly alignment: {str(e)}")
            return pd.DataFrame()
    
    def calculate_seasonal_patterns(self, dataset_name, fraction):
        """
        Calculate seasonal patterns for a dataset
        
        Args:
            dataset_name (str): 'MCD43A3' or 'MOD10A1'
            fraction (str): Fraction class
            
        Returns:
            dict: Seasonal pattern statistics
        """
        try:
            if dataset_name == 'MCD43A3':
                data = self.dataset1.data
            else:
                data = self.dataset2.data
            
            col_name = f"{fraction}_mean"
            if col_name not in data.columns:
                return None
            
            # Group by month and calculate statistics
            monthly_data = data[['date', col_name]].dropna()
            monthly_data['month'] = monthly_data['date'].dt.month
            
            monthly_stats = monthly_data.groupby('month')[col_name].agg(['mean', 'std']).reset_index()
            
            return {
                'mean': monthly_stats['mean'].tolist(),
                'std': monthly_stats['std'].tolist(),
                'months': monthly_stats['month'].tolist()
            }
            
        except Exception as e:
            print(f"Error calculating seasonal patterns: {str(e)}")
            return None
    
    def calculate_comparison_statistics(self, fraction):
        """
        Calculate comprehensive comparison statistics
        
        Args:
            fraction (str): Fraction class
            
        Returns:
            dict: Comparison statistics
        """
        try:
            col_name = f"{fraction}_mean"
            
            # Get data from both datasets
            data1 = self.dataset1.data[[col_name]].dropna()
            data2 = self.dataset2.data[[col_name]].dropna()
            
            # Calculate basic statistics
            stats1 = {
                'mean': float(data1[col_name].mean()),
                'median': float(data1[col_name].median()),
                'std': float(data1[col_name].std()),
                'min': float(data1[col_name].min()),
                'max': float(data1[col_name].max()),
                'skewness': float(data1[col_name].skew()),
                'kurtosis': float(data1[col_name].kurtosis()),
                'data': data1[col_name].tolist(),
                'trend': 0.0,  # Placeholder
                'trend_pvalue': 1.0  # Placeholder
            }
            
            stats2 = {
                'mean': float(data2[col_name].mean()),
                'median': float(data2[col_name].median()),
                'std': float(data2[col_name].std()),
                'min': float(data2[col_name].min()),
                'max': float(data2[col_name].max()),
                'skewness': float(data2[col_name].skew()),
                'kurtosis': float(data2[col_name].kurtosis()),
                'data': data2[col_name].tolist(),
                'trend': 0.0,  # Placeholder
                'trend_pvalue': 1.0  # Placeholder
            }
            
            return {
                'mcd43a3': stats1,
                'mod10a1': stats2
            }
            
        except Exception as e:
            print(f"Error calculating comparison statistics: {str(e)}")
            return None