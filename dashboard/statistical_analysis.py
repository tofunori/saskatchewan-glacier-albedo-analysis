"""
Statistical Analysis Module for Academic Dashboard
================================================

Comprehensive statistical analysis integration for the Saskatchewan Glacier 
Albedo Analysis dashboard, providing academic-grade statistical tests and 
publication-quality results.

This module integrates:
- Mann-Kendall trend tests
- Sen's slope calculations with confidence intervals
- Bootstrap analysis with configurable iterations
- Autocorrelation analysis
- Seasonal trend decomposition
- Quality assessment metrics
"""

import numpy as np
import pandas as pd
import sys
import os
from scipy import stats
from sklearn.utils import resample
import warnings
warnings.filterwarnings('ignore')

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.helpers import (perform_mann_kendall_test, calculate_sen_slope, 
                            calculate_autocorrelation, validate_data, format_pvalue)
from config import (FRACTION_CLASSES, CLASS_LABELS, TREND_SYMBOLS, 
                     get_significance_marker, ANALYSIS_CONFIG, MONTH_NAMES)

class DashboardStatisticalAnalyzer:
    """
    Comprehensive statistical analyzer for dashboard integration
    """
    
    def __init__(self, data, dataset_name='MCD43A3'):
        """
        Initialize the statistical analyzer
        
        Args:
            data (pd.DataFrame): Loaded albedo data
            dataset_name (str): Name of the dataset being analyzed
        """
        self.data = data
        self.dataset_name = dataset_name
        self.fraction_classes = FRACTION_CLASSES
        self.class_labels = CLASS_LABELS
        self.results_cache = {}
        
    def calculate_comprehensive_trends(self, variable='mean', bootstrap_n=1000):
        """
        Calculate comprehensive trend analysis including Mann-Kendall, Sen's slope, 
        and bootstrap confidence intervals
        
        Args:
            variable (str): Variable to analyze ('mean' or 'median')
            bootstrap_n (int): Number of bootstrap iterations
            
        Returns:
            dict: Comprehensive trend analysis results
        """
        cache_key = f"trends_{variable}_{bootstrap_n}"
        if cache_key in self.results_cache:
            return self.results_cache[cache_key]
        
        results = {}
        
        for fraction in self.fraction_classes:
            try:
                # Extract fraction data
                fraction_data = self._get_fraction_data(fraction, variable)
                
                if len(fraction_data) < 10:
                    results[fraction] = self._create_empty_result(fraction, variable)
                    continue
                
                times = fraction_data['decimal_year'].values
                values = fraction_data['value'].values
                
                # Data validation
                is_valid, clean_values, n_removed = validate_data(values)
                if not is_valid:
                    results[fraction] = self._create_empty_result(fraction, variable)
                    continue
                
                clean_times = times[~np.isnan(values)]
                
                # Mann-Kendall test
                mk_result = perform_mann_kendall_test(clean_values)
                
                # Sen's slope
                sen_result = calculate_sen_slope(clean_times, clean_values)
                
                # Autocorrelation analysis
                autocorr = calculate_autocorrelation(clean_values, lag=1)
                autocorr_status = self._get_autocorr_status(autocorr)
                
                # Bootstrap confidence intervals
                bootstrap_result = self._calculate_bootstrap_ci(
                    clean_times, clean_values, bootstrap_n
                )
                
                # Data quality metrics
                quality_metrics = self._calculate_quality_metrics(fraction_data)
                
                results[fraction] = {
                    'fraction': fraction,
                    'label': self.class_labels[fraction],
                    'variable': variable,
                    'n_obs': len(clean_values),
                    'n_removed': n_removed,
                    'data_range': {
                        'start': fraction_data['date'].min(),
                        'end': fraction_data['date'].max(),
                        'years': len(fraction_data['date'].dt.year.unique())
                    },
                    'mann_kendall': mk_result,
                    'sen_slope': sen_result,
                    'autocorrelation': {
                        'lag1': autocorr,
                        'status': autocorr_status,
                        'significant': abs(autocorr) > 0.1
                    },
                    'bootstrap': bootstrap_result,
                    'quality_metrics': quality_metrics,
                    'data': {
                        'times': clean_times,
                        'values': clean_values
                    }
                }
                
            except Exception as e:
                print(f"Error analyzing {fraction}: {e}")
                results[fraction] = self._create_empty_result(fraction, variable)
        
        self.results_cache[cache_key] = results
        return results
    
    def calculate_seasonal_trends(self, variable='mean'):
        """
        Calculate seasonal and monthly trend analysis
        
        Args:
            variable (str): Variable to analyze
            
        Returns:
            dict: Seasonal trend analysis results
        """
        cache_key = f"seasonal_{variable}"
        if cache_key in self.results_cache:
            return self.results_cache[cache_key]
        
        results = {}
        
        # Analyze each month in melt season
        for month in [6, 7, 8, 9]:
            month_name = MONTH_NAMES[month]
            month_data = self.data[self.data['month'] == month].copy()
            
            if len(month_data) < 5:
                continue
            
            month_results = {}
            
            for fraction in self.fraction_classes:
                col_name = f"{fraction}_{variable}"
                
                if col_name not in month_data.columns:
                    continue
                
                valid_data = month_data[['decimal_year', col_name]].dropna()
                
                if len(valid_data) < 5:
                    continue
                
                times = valid_data['decimal_year'].values
                values = valid_data[col_name].values
                
                # Mann-Kendall and Sen's slope for monthly data
                mk_result = perform_mann_kendall_test(values)
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
            
            results[month] = {
                'month': month,
                'month_name': month_name,
                'fractions': month_results
            }
        
        self.results_cache[cache_key] = results
        return results
    
    def _get_fraction_data(self, fraction, variable):
        """Extract data for a specific fraction"""
        col_name = f"{fraction}_{variable}"
        
        if col_name not in self.data.columns:
            # Handle elevation data format
            if hasattr(self.data, 'fraction_class') and hasattr(self.data, 'albedo_mean'):
                subset = self.data[self.data['fraction_class'] == fraction].copy()
                if not subset.empty:
                    subset['value'] = subset['albedo_mean'] if variable == 'mean' else subset.get('albedo_median', subset['albedo_mean'])
                    subset['decimal_year'] = subset['date'].dt.year + (subset['date'].dt.dayofyear - 1) / 365.25
                    return subset[['date', 'decimal_year', 'value']].dropna()
            return pd.DataFrame()
        
        # Standard format
        subset = self.data[['date', col_name]].dropna()
        if subset.empty:
            return pd.DataFrame()
        
        subset = subset.rename(columns={col_name: 'value'})
        subset['decimal_year'] = subset['date'].dt.year + (subset['date'].dt.dayofyear - 1) / 365.25
        
        return subset
    
    def _calculate_bootstrap_ci(self, times, values, n_bootstrap=1000):
        """Calculate bootstrap confidence intervals"""
        bootstrap_slopes = []
        bootstrap_pvalues = []
        
        for i in range(n_bootstrap):
            try:
                # Bootstrap sample
                indices = resample(range(len(values)), n_samples=len(values), random_state=i)
                boot_values = values[indices]
                boot_times = times[indices]
                
                # Mann-Kendall test
                mk_result = perform_mann_kendall_test(boot_values)
                bootstrap_pvalues.append(mk_result['p_value'])
                
                # Sen's slope
                if len(boot_values) > 5:
                    sen_result = calculate_sen_slope(boot_times, boot_values)
                    bootstrap_slopes.append(sen_result['slope_per_decade'])
            except:
                continue
        
        if len(bootstrap_slopes) > 0:
            slope_ci = np.percentile(bootstrap_slopes, [2.5, 50, 97.5])
            pvalue_mean = np.mean(bootstrap_pvalues)
            pvalue_ci = np.percentile(bootstrap_pvalues, [2.5, 97.5])
            significant_prop = np.mean(np.array(bootstrap_pvalues) < 0.05)
            
            return {
                'n_successful': len(bootstrap_slopes),
                'slope_median': slope_ci[1],
                'slope_ci_95_low': slope_ci[0],
                'slope_ci_95_high': slope_ci[2],
                'slope_std': np.std(bootstrap_slopes),
                'pvalue_mean': pvalue_mean,
                'pvalue_ci_low': pvalue_ci[0],
                'pvalue_ci_high': pvalue_ci[1],
                'significant_proportion': significant_prop,
                'slopes': bootstrap_slopes,
                'pvalues': bootstrap_pvalues
            }
        
        return {'n_successful': 0, 'error': True}
    
    def _calculate_quality_metrics(self, fraction_data):
        """Calculate data quality metrics"""
        return {
            'completeness': len(fraction_data) / (365.25 * 15),  # 15 years expected
            'mean_value': fraction_data['value'].mean(),
            'std_value': fraction_data['value'].std(),
            'min_value': fraction_data['value'].min(),
            'max_value': fraction_data['value'].max(),
            'coefficient_of_variation': fraction_data['value'].std() / fraction_data['value'].mean() if fraction_data['value'].mean() != 0 else np.nan
        }
    
    def _get_autocorr_status(self, autocorr_value):
        """Get autocorrelation status with emoji"""
        abs_autocorr = abs(autocorr_value)
        
        if abs_autocorr > ANALYSIS_CONFIG['autocorr_thresholds']['strong']:
            return "🔴 Très forte"
        elif abs_autocorr > ANALYSIS_CONFIG['autocorr_thresholds']['moderate']:
            return "🔴 Forte" 
        elif abs_autocorr > ANALYSIS_CONFIG['autocorr_thresholds']['weak']:
            return "🟡 Modérée"
        else:
            return "🟢 Faible"
    
    def _create_empty_result(self, fraction, variable):
        """Create empty result for error cases"""
        return {
            'fraction': fraction,
            'label': self.class_labels[fraction],
            'variable': variable,
            'n_obs': 0,
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
                'status': '❓ Inconnu',
                'significant': False
            },
            'bootstrap': {'error': True, 'n_successful': 0}
        }
    
    def get_summary_statistics(self, results):
        """Generate summary statistics from trend results"""
        summary = {
            'total_fractions': len(results),
            'valid_fractions': sum(1 for r in results.values() if not r.get('error', False)),
            'significant_trends': sum(1 for r in results.values() 
                                    if not r.get('error', False) and r['mann_kendall']['p_value'] < 0.05),
            'trends': {'increasing': 0, 'decreasing': 0, 'no trend': 0},
            'autocorrelation_issues': sum(1 for r in results.values() 
                                        if not r.get('error', False) and r['autocorrelation']['significant'])
        }
        
        for result in results.values():
            if not result.get('error', False):
                trend = result['mann_kendall']['trend']
                summary['trends'][trend] += 1
        
        return summary
    
    def create_results_table(self, results, include_bootstrap=True):
        """Create a comprehensive results table for export"""
        table_data = []
        
        for fraction, result in results.items():
            if result.get('error', False):
                continue
            
            mk = result['mann_kendall']
            sen = result['sen_slope']
            autocorr = result['autocorrelation']
            
            row = {
                'Fraction': result['label'],
                'N_observations': result['n_obs'],
                'Data_years': result['data_range']['years'],
                'Trend_direction': mk['trend'],
                'P_value': mk['p_value'],
                'Significance': get_significance_marker(mk['p_value']),
                'Kendall_tau': mk['tau'],
                'Z_statistic': mk['z'],
                'Sen_slope_per_decade': sen['slope_per_decade'],
                'Sen_slope_per_year': sen['slope'],
                'Autocorrelation_lag1': autocorr['lag1'],
                'Autocorr_status': autocorr['status'],
                'Mean_albedo': result['quality_metrics']['mean_value'],
                'Std_albedo': result['quality_metrics']['std_value'],
                'CV_percent': result['quality_metrics']['coefficient_of_variation'] * 100
            }
            
            if include_bootstrap and not result['bootstrap'].get('error', False):
                bootstrap = result['bootstrap']
                row.update({
                    'Bootstrap_slope_median': bootstrap['slope_median'],
                    'Bootstrap_CI_95_low': bootstrap['slope_ci_95_low'],
                    'Bootstrap_CI_95_high': bootstrap['slope_ci_95_high'],
                    'Bootstrap_significant_prop': bootstrap['significant_proportion']
                })
            
            table_data.append(row)
        
        return pd.DataFrame(table_data)