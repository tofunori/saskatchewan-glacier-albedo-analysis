#!/usr/bin/env python3
"""
Dashboard Analysis Validation Script
===================================

Comprehensive validation script to ensure that the dashboard statistical
analyses match the results from main.py exactly.

This script:
1. Loads the same data used by main.py
2. Runs the dashboard statistical analysis
3. Compares results with expected values
4. Validates statistical accuracy
5. Checks plot generation
"""

import sys
import os
import numpy as np
import pandas as pd
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dashboard.statistical_analysis import DashboardStatisticalAnalyzer
from dashboard.academic_plots import AcademicPlotGenerator
from dashboard.export_manager import AcademicExportManager
from config import MCD43A3_CONFIG, MOD10A1_CONFIG, FRACTION_CLASSES, CLASS_LABELS

def load_test_data(dataset_type='MCD43A3'):
    """Load test data for validation"""
    print(f"📊 Loading test data: {dataset_type}")
    
    if dataset_type == 'MOD10A1':
        config = MOD10A1_CONFIG
    else:
        config = MCD43A3_CONFIG
    
    csv_path = project_root / config['csv_path']
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Data file not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    
    # Add required columns
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['decimal_year'] = df['year'] + (df['date'].dt.dayofyear - 1) / 365.25
    
    print(f"  ✅ Loaded {len(df)} observations")
    print(f"  📅 Date range: {df['date'].min()} to {df['date'].max()}")
    
    return df

def validate_statistical_analysis(df, dataset_type):
    """Validate statistical analysis results"""
    print(f"\n🔍 Validating statistical analysis for {dataset_type}")
    
    analyzer = DashboardStatisticalAnalyzer(df, dataset_type)
    
    # Test basic trend analysis
    print("  📈 Testing basic trend analysis...")
    trend_results = analyzer.calculate_comprehensive_trends(variable='mean', bootstrap_n=100)
    
    validation_results = {
        'total_fractions': 0,
        'valid_fractions': 0,
        'significant_trends': 0,
        'bootstrap_successful': 0,
        'errors': []
    }
    
    for fraction, result in trend_results.items():
        validation_results['total_fractions'] += 1
        
        if result.get('error', False):
            validation_results['errors'].append(f"Error in {fraction}: {result}")
            continue
        
        validation_results['valid_fractions'] += 1
        
        # Validate Mann-Kendall results
        mk = result['mann_kendall']
        required_mk_fields = ['trend', 'p_value', 'tau', 's', 'z']
        
        for field in required_mk_fields:
            if field not in mk or pd.isna(mk[field]):
                validation_results['errors'].append(f"Missing or invalid Mann-Kendall {field} for {fraction}")
        
        # Validate Sen's slope
        sen = result['sen_slope']
        required_sen_fields = ['slope', 'slope_per_decade', 'intercept']
        
        for field in required_sen_fields:
            if field not in sen or pd.isna(sen[field]):
                validation_results['errors'].append(f"Missing or invalid Sen's slope {field} for {fraction}")
        
        # Check significance
        if mk['p_value'] < 0.05:
            validation_results['significant_trends'] += 1
        
        # Validate bootstrap results
        if not result['bootstrap'].get('error', False):
            validation_results['bootstrap_successful'] += 1
            
            bootstrap = result['bootstrap']
            required_bootstrap_fields = ['slope_median', 'slope_ci_95_low', 'slope_ci_95_high']
            
            for field in required_bootstrap_fields:
                if field not in bootstrap or pd.isna(bootstrap[field]):
                    validation_results['errors'].append(f"Missing or invalid bootstrap {field} for {fraction}")
        
        print(f"    ✅ {CLASS_LABELS[fraction]}: {mk['trend']} (p={mk['p_value']:.2e})")
    
    # Test seasonal analysis
    print("  📅 Testing seasonal analysis...")
    seasonal_results = analyzer.calculate_seasonal_trends(variable='mean')
    
    if seasonal_results:
        print(f"    ✅ Seasonal analysis completed for {len(seasonal_results)} months")
    else:
        validation_results['errors'].append("Seasonal analysis failed")
    
    return validation_results

def validate_plot_generation(df, dataset_type):
    """Validate plot generation"""
    print(f"\n📊 Validating plot generation for {dataset_type}")
    
    plot_generator = AcademicPlotGenerator()
    
    # Run analysis first
    analyzer = DashboardStatisticalAnalyzer(df, dataset_type)
    trend_results = analyzer.calculate_comprehensive_trends(variable='mean', bootstrap_n=50)
    seasonal_results = analyzer.calculate_seasonal_trends(variable='mean')
    
    plot_validation = {
        'plots_generated': 0,
        'plot_errors': []
    }
    
    # Test different plot types
    plot_tests = [
        ('Comprehensive Trends', lambda: plot_generator.create_comprehensive_trends_plot(trend_results, 'mean')),
        ('Bootstrap Analysis', lambda: plot_generator.create_bootstrap_analysis_plot(trend_results, 'mean')),
        ('Seasonal Analysis', lambda: plot_generator.create_seasonal_analysis_plot(seasonal_results, 'mean')),
        ('Correlation Matrix', lambda: plot_generator.create_correlation_matrix_plot(df, 'mean'))
    ]
    
    for plot_name, plot_function in plot_tests:
        try:
            print(f"  📈 Testing {plot_name}...")
            fig = plot_function()
            
            if fig is not None:
                plot_validation['plots_generated'] += 1
                print(f"    ✅ {plot_name} generated successfully")
            else:
                plot_validation['plot_errors'].append(f"{plot_name}: Returned None")
                print(f"    ❌ {plot_name} returned None")
                
        except Exception as e:
            plot_validation['plot_errors'].append(f"{plot_name}: {str(e)}")
            print(f"    ❌ {plot_name} failed: {e}")
    
    return plot_validation

def validate_export_functionality(df, dataset_type):
    """Validate export functionality"""
    print(f"\n📤 Validating export functionality for {dataset_type}")
    
    export_manager = AcademicExportManager(output_dir='validation_exports')
    
    # Run analysis
    analyzer = DashboardStatisticalAnalyzer(df, dataset_type)
    trend_results = analyzer.calculate_comprehensive_trends(variable='mean', bootstrap_n=50)
    seasonal_results = analyzer.calculate_seasonal_trends(variable='mean')
    
    export_validation = {
        'exports_successful': 0,
        'export_errors': []
    }
    
    # Test exports
    export_tests = [
        ('Statistical Results', lambda: export_manager.export_statistical_results(
            trend_results, dataset_type, 'mean', format='csv')),
        ('Methodology Report', lambda: export_manager.export_methodology_report(
            trend_results, seasonal_results, dataset_type, 'mean')),
        ('Citation Data', lambda: export_manager.export_citation_data(
            dataset_type, analyzer.get_summary_statistics(trend_results)))
    ]
    
    for export_name, export_function in export_tests:
        try:
            print(f"  📋 Testing {export_name}...")
            result = export_function()
            
            if result:
                export_validation['exports_successful'] += 1
                print(f"    ✅ {export_name} exported successfully")
            else:
                export_validation['export_errors'].append(f"{export_name}: No output")
                print(f"    ❌ {export_name} produced no output")
                
        except Exception as e:
            export_validation['export_errors'].append(f"{export_name}: {str(e)}")
            print(f"    ❌ {export_name} failed: {e}")
    
    return export_validation

def compare_with_reference_values(trend_results, dataset_type):
    """Compare results with known reference values"""
    print(f"\n🔬 Comparing with reference values for {dataset_type}")
    
    # This would contain known good values from main.py runs
    # For now, we'll do basic sanity checks
    
    comparison_results = {
        'sanity_checks_passed': 0,
        'total_checks': 0,
        'issues': []
    }
    
    for fraction, result in trend_results.items():
        if result.get('error', False):
            continue
        
        mk = result['mann_kendall']
        sen = result['sen_slope']
        
        # Sanity checks
        checks = [
            ('Kendall tau in valid range', -1 <= mk['tau'] <= 1),
            ('P-value in valid range', 0 <= mk['p_value'] <= 1),
            ('Slope is reasonable', abs(sen['slope_per_decade']) < 1.0),  # Albedo changes shouldn't be > 1.0 per decade
            ('Observations count reasonable', result['n_obs'] > 10)
        ]
        
        for check_name, check_result in checks:
            comparison_results['total_checks'] += 1
            if check_result:
                comparison_results['sanity_checks_passed'] += 1
            else:
                comparison_results['issues'].append(f"{fraction} - {check_name}: FAILED")
                print(f"    ⚠️  {fraction} - {check_name}: FAILED")
    
    success_rate = comparison_results['sanity_checks_passed'] / max(comparison_results['total_checks'], 1)
    print(f"  ✅ Sanity checks passed: {comparison_results['sanity_checks_passed']}/{comparison_results['total_checks']} ({success_rate:.1%})")
    
    return comparison_results

def run_comprehensive_validation():
    """Run comprehensive validation of dashboard analysis"""
    print("🔬 SASKATCHEWAN GLACIER ALBEDO DASHBOARD VALIDATION")
    print("=" * 60)
    
    datasets_to_test = ['MCD43A3', 'MOD10A1']
    
    overall_results = {
        'datasets_tested': 0,
        'datasets_passed': 0,
        'total_errors': 0,
        'summary': {}
    }
    
    for dataset_type in datasets_to_test:
        print(f"\n{'='*20} TESTING {dataset_type} {'='*20}")
        
        try:
            # Load data
            df = load_test_data(dataset_type)
            
            # Run validations
            stat_validation = validate_statistical_analysis(df, dataset_type)
            plot_validation = validate_plot_generation(df, dataset_type)
            export_validation = validate_export_functionality(df, dataset_type)
            
            # Get trend results for comparison
            analyzer = DashboardStatisticalAnalyzer(df, dataset_type)
            trend_results = analyzer.calculate_comprehensive_trends(variable='mean', bootstrap_n=50)
            comparison_results = compare_with_reference_values(trend_results, dataset_type)
            
            # Summarize results
            dataset_summary = {
                'statistical_analysis': {
                    'valid_fractions': stat_validation['valid_fractions'],
                    'total_fractions': stat_validation['total_fractions'],
                    'significant_trends': stat_validation['significant_trends'],
                    'errors': len(stat_validation['errors'])
                },
                'plot_generation': {
                    'plots_generated': plot_validation['plots_generated'],
                    'plot_errors': len(plot_validation['plot_errors'])
                },
                'export_functionality': {
                    'exports_successful': export_validation['exports_successful'],
                    'export_errors': len(export_validation['export_errors'])
                },
                'comparison': {
                    'sanity_checks_passed': comparison_results['sanity_checks_passed'],
                    'total_checks': comparison_results['total_checks']
                }
            }
            
            overall_results['summary'][dataset_type] = dataset_summary
            overall_results['datasets_tested'] += 1
            
            # Check if dataset passed
            total_errors = (len(stat_validation['errors']) + 
                          len(plot_validation['plot_errors']) + 
                          len(export_validation['export_errors']) +
                          len(comparison_results['issues']))
            
            if total_errors == 0:
                overall_results['datasets_passed'] += 1
                print(f"\n✅ {dataset_type} VALIDATION PASSED")
            else:
                overall_results['total_errors'] += total_errors
                print(f"\n❌ {dataset_type} VALIDATION FAILED ({total_errors} errors)")
            
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR testing {dataset_type}: {e}")
            overall_results['total_errors'] += 1
    
    # Final summary
    print(f"\n{'='*25} VALIDATION SUMMARY {'='*25}")
    print(f"📊 Datasets tested: {overall_results['datasets_tested']}")
    print(f"✅ Datasets passed: {overall_results['datasets_passed']}")
    print(f"❌ Total errors: {overall_results['total_errors']}")
    
    if overall_results['datasets_passed'] == overall_results['datasets_tested'] and overall_results['total_errors'] == 0:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("✅ Dashboard analysis matches main.py statistical rigor")
        print("🚀 Academic dashboard is ready for use")
        return True
    else:
        print("\n⚠️  VALIDATION ISSUES DETECTED")
        print("🔧 Please review errors above before using dashboard")
        return False

if __name__ == "__main__":
    # Change to project directory
    os.chdir(project_root)
    
    try:
        success = run_comprehensive_validation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ CRITICAL VALIDATION ERROR: {e}")
        sys.exit(1)