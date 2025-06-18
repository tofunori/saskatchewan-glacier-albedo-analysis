"""
Export Manager for Academic Dashboard
====================================

Comprehensive export functionality for the Saskatchewan Glacier Albedo Analysis
dashboard, providing publication-ready outputs including statistical tables,
figures, and methodology documentation.

Features:
- Statistical results export (CSV, Excel, JSON)
- Publication-quality figure export (PNG, SVG, PDF)
- Comprehensive methodology reports
- Citation-ready data documentation
- Batch export capabilities
"""

import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import plotly.io as pio
import plotly.graph_objects as go

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config import get_significance_marker, ANALYSIS_CONFIG
from utils.helpers import format_pvalue

class AcademicExportManager:
    """
    Comprehensive export manager for academic research outputs
    """
    
    def __init__(self, output_dir='dashboard_exports'):
        """
        Initialize export manager
        
        Args:
            output_dir (str): Base directory for exports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.figures_dir = self.output_dir / 'figures'
        self.tables_dir = self.output_dir / 'tables'
        self.reports_dir = self.output_dir / 'reports'
        
        for directory in [self.figures_dir, self.tables_dir, self.reports_dir]:
            directory.mkdir(exist_ok=True)
        
        # Configure high-quality figure exports
        pio.kaleido.scope.default_width = 1200
        pio.kaleido.scope.default_height = 800
        pio.kaleido.scope.default_scale = 2  # 300 DPI equivalent
    
    def export_statistical_results(self, trend_results, dataset_name, variable='mean', 
                                 include_bootstrap=True, format='all'):
        """
        Export comprehensive statistical results
        
        Args:
            trend_results (dict): Statistical analysis results
            dataset_name (str): Name of the dataset
            variable (str): Variable analyzed
            include_bootstrap (bool): Include bootstrap results
            format (str): Export format ('csv', 'excel', 'json', 'all')
            
        Returns:
            dict: Paths to exported files
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f'{dataset_name}_{variable}_statistical_results_{timestamp}'
        
        # Create comprehensive results table
        results_table = self._create_comprehensive_results_table(
            trend_results, include_bootstrap
        )
        
        # Create summary statistics
        summary_stats = self._create_summary_statistics(trend_results)
        
        exported_files = {}
        
        if format in ['csv', 'all']:
            # Export main results
            csv_path = self.tables_dir / f'{base_filename}.csv'
            results_table.to_csv(csv_path, index=False)
            exported_files['csv_results'] = csv_path
            
            # Export summary
            summary_path = self.tables_dir / f'{dataset_name}_{variable}_summary_{timestamp}.csv'
            pd.DataFrame([summary_stats]).to_csv(summary_path, index=False)
            exported_files['csv_summary'] = summary_path
        
        if format in ['excel', 'all']:
            excel_path = self.tables_dir / f'{base_filename}.xlsx'
            
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                # Main results
                results_table.to_excel(writer, sheet_name='Statistical_Results', index=False)
                
                # Summary statistics
                pd.DataFrame([summary_stats]).to_excel(writer, sheet_name='Summary', index=False)
                
                # Methodology notes
                methodology_df = self._create_methodology_notes()
                methodology_df.to_excel(writer, sheet_name='Methodology', index=False)
                
                # Data quality metrics
                if include_bootstrap:
                    quality_df = self._create_quality_metrics_table(trend_results)
                    quality_df.to_excel(writer, sheet_name='Data_Quality', index=False)
            
            exported_files['excel'] = excel_path
        
        if format in ['json', 'all']:
            # Export as structured JSON for programmatic access
            json_path = self.tables_dir / f'{base_filename}.json'
            
            json_data = {
                'metadata': {
                    'dataset': dataset_name,
                    'variable': variable,
                    'analysis_date': datetime.now().isoformat(),
                    'bootstrap_included': include_bootstrap,
                    'significance_levels': ANALYSIS_CONFIG['significance_levels'],
                    'bootstrap_iterations': ANALYSIS_CONFIG.get('bootstrap_iterations', 1000)
                },
                'summary_statistics': summary_stats,
                'detailed_results': self._convert_results_to_json_format(trend_results),
                'methodology': self._get_methodology_info()
            }
            
            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=2, default=str)
            
            exported_files['json'] = json_path
        
        return exported_files
    
    def export_figure(self, figure, filename, formats=['png', 'svg'], 
                     width=1200, height=800, scale=2):
        """
        Export publication-quality figures in multiple formats
        
        Args:
            figure (plotly.graph_objects.Figure): Figure to export
            filename (str): Base filename (without extension)
            formats (list): List of formats to export ('png', 'svg', 'pdf', 'html')
            width (int): Figure width in pixels
            height (int): Figure height in pixels
            scale (int): Scale factor for raster formats
            
        Returns:
            dict: Paths to exported figure files
        """
        exported_files = {}
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f'{filename}_{timestamp}'
        
        for fmt in formats:
            if fmt == 'png':
                path = self.figures_dir / f'{base_filename}.png'
                figure.write_image(str(path), format='png', width=width, height=height, scale=scale)
                exported_files['png'] = path
            
            elif fmt == 'svg':
                path = self.figures_dir / f'{base_filename}.svg'
                figure.write_image(str(path), format='svg', width=width, height=height)
                exported_files['svg'] = path
            
            elif fmt == 'pdf':
                path = self.figures_dir / f'{base_filename}.pdf'
                figure.write_image(str(path), format='pdf', width=width, height=height)
                exported_files['pdf'] = path
            
            elif fmt == 'html':
                path = self.figures_dir / f'{base_filename}.html'
                figure.write_html(str(path), include_plotlyjs='cdn')
                exported_files['html'] = path
        
        return exported_files
    
    def export_methodology_report(self, trend_results, seasonal_results, 
                                dataset_name, variable='mean'):
        """
        Export comprehensive methodology and results report
        
        Args:
            trend_results (dict): Trend analysis results
            seasonal_results (dict): Seasonal analysis results
            dataset_name (str): Dataset name
            variable (str): Variable analyzed
            
        Returns:
            str: Path to exported report
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.reports_dir / f'{dataset_name}_{variable}_methodology_report_{timestamp}.md'
        
        report_content = self._generate_methodology_report(
            trend_results, seasonal_results, dataset_name, variable
        )
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_path
    
    def export_citation_data(self, dataset_name, analysis_summary):
        """
        Export citation-ready data documentation
        
        Args:
            dataset_name (str): Dataset name
            analysis_summary (dict): Analysis summary statistics
            
        Returns:
            str: Path to citation file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        citation_path = self.reports_dir / f'{dataset_name}_citation_data_{timestamp}.txt'
        
        citation_content = self._generate_citation_documentation(dataset_name, analysis_summary)
        
        with open(citation_path, 'w', encoding='utf-8') as f:
            f.write(citation_content)
        
        return citation_path
    
    def _create_comprehensive_results_table(self, trend_results, include_bootstrap=True):
        """Create comprehensive results table"""
        table_data = []
        
        for fraction, result in trend_results.items():
            if result.get('error', False):
                continue
            
            mk = result['mann_kendall']
            sen = result['sen_slope']
            autocorr = result['autocorrelation']
            quality = result.get('quality_metrics', {})
            
            row = {
                'Fraction_Class': result['label'],
                'Fraction_Code': fraction,
                'N_Observations': result['n_obs'],
                'Data_Years': result['data_range']['years'],
                'Start_Date': result['data_range']['start'],
                'End_Date': result['data_range']['end'],
                'Trend_Direction': mk['trend'],
                'Mann_Kendall_Tau': mk['tau'],
                'Mann_Kendall_Z': mk['z'],
                'Mann_Kendall_S': mk['s'],
                'P_Value': mk['p_value'],
                'P_Value_Formatted': format_pvalue(mk['p_value']),
                'Significance_Level': get_significance_marker(mk['p_value']),
                'Sen_Slope_Per_Year': sen['slope'],
                'Sen_Slope_Per_Decade': sen['slope_per_decade'],
                'Sen_Intercept': sen['intercept'],
                'Autocorrelation_Lag1': autocorr['lag1'],
                'Autocorr_Status': autocorr['status'],
                'Autocorr_Significant': autocorr['significant'],
                'Mean_Albedo': quality.get('mean_value', np.nan),
                'Std_Albedo': quality.get('std_value', np.nan),
                'Min_Albedo': quality.get('min_value', np.nan),
                'Max_Albedo': quality.get('max_value', np.nan),
                'Coefficient_of_Variation': quality.get('coefficient_of_variation', np.nan),
                'Data_Completeness': quality.get('completeness', np.nan)
            }
            
            if include_bootstrap and not result['bootstrap'].get('error', False):
                bootstrap = result['bootstrap']
                row.update({
                    'Bootstrap_Iterations': bootstrap['n_successful'],
                    'Bootstrap_Slope_Median': bootstrap['slope_median'],
                    'Bootstrap_CI_95_Lower': bootstrap['slope_ci_95_low'],
                    'Bootstrap_CI_95_Upper': bootstrap['slope_ci_95_high'],
                    'Bootstrap_Slope_Std': bootstrap['slope_std'],
                    'Bootstrap_P_Value_Mean': bootstrap['pvalue_mean'],
                    'Bootstrap_Significant_Proportion': bootstrap['significant_proportion']
                })
            
            table_data.append(row)
        
        return pd.DataFrame(table_data)
    
    def _create_summary_statistics(self, trend_results):
        """Create summary statistics"""
        valid_results = [r for r in trend_results.values() if not r.get('error', False)]
        
        if not valid_results:
            return {}
        
        trends = [r['mann_kendall']['trend'] for r in valid_results]
        p_values = [r['mann_kendall']['p_value'] for r in valid_results]
        
        return {
            'Total_Fractions_Analyzed': len(valid_results),
            'Increasing_Trends': trends.count('increasing'),
            'Decreasing_Trends': trends.count('decreasing'),
            'No_Trend': trends.count('no trend'),
            'Significant_Trends_p005': sum(1 for p in p_values if p < 0.05),
            'Significant_Trends_p001': sum(1 for p in p_values if p < 0.01),
            'Significant_Trends_p0001': sum(1 for p in p_values if p < 0.001),
            'Mean_P_Value': np.mean(p_values),
            'Median_P_Value': np.median(p_values),
            'Min_P_Value': np.min(p_values),
            'Max_P_Value': np.max(p_values),
            'Analysis_Date': datetime.now().isoformat()
        }
    
    def _create_methodology_notes(self):
        """Create methodology documentation table"""
        methodology_data = [
            {'Method': 'Mann-Kendall Test', 'Description': 'Non-parametric trend test for time series data'},
            {'Method': 'Sen\'s Slope', 'Description': 'Robust estimate of trend magnitude'},
            {'Method': 'Bootstrap Confidence Intervals', 'Description': 'Resampling-based confidence intervals for Sen\'s slope'},
            {'Method': 'Autocorrelation Analysis', 'Description': 'Assessment of temporal correlation in residuals'},
            {'Method': 'Significance Levels', 'Description': '*** p<0.001, ** p<0.01, * p<0.05, ns p≥0.05'},
            {'Method': 'Data Quality Assessment', 'Description': 'Completeness and variability metrics'},
            {'Method': 'Fraction Classes', 'Description': 'Ice coverage percentage classes (0-25%, 25-50%, 50-75%, 75-90%, 90-100%)'}
        ]
        return pd.DataFrame(methodology_data)
    
    def _create_quality_metrics_table(self, trend_results):
        """Create data quality metrics table"""
        quality_data = []
        
        for fraction, result in trend_results.items():
            if result.get('error', False):
                continue
            
            quality = result.get('quality_metrics', {})
            
            quality_data.append({
                'Fraction': result['label'],
                'Data_Completeness': quality.get('completeness', np.nan),
                'Mean_Value': quality.get('mean_value', np.nan),
                'Standard_Deviation': quality.get('std_value', np.nan),
                'Coefficient_of_Variation': quality.get('coefficient_of_variation', np.nan),
                'Min_Value': quality.get('min_value', np.nan),
                'Max_Value': quality.get('max_value', np.nan),
                'Data_Range_Years': result['data_range']['years'],
                'Observations_Count': result['n_obs']
            })
        
        return pd.DataFrame(quality_data)
    
    def _convert_results_to_json_format(self, trend_results):
        """Convert results to JSON-serializable format"""
        json_results = {}
        
        for fraction, result in trend_results.items():
            # Convert numpy types to Python types for JSON serialization
            json_result = {}
            for key, value in result.items():
                if isinstance(value, dict):
                    json_result[key] = {k: float(v) if isinstance(v, np.floating) else 
                                       int(v) if isinstance(v, np.integer) else v 
                                       for k, v in value.items()}
                elif isinstance(value, (np.floating, np.integer)):
                    json_result[key] = float(value) if isinstance(value, np.floating) else int(value)
                else:
                    json_result[key] = value
            
            json_results[fraction] = json_result
        
        return json_results
    
    def _get_methodology_info(self):
        """Get methodology information"""
        return {
            'statistical_tests': {
                'mann_kendall': 'Non-parametric trend detection',
                'sen_slope': 'Robust trend magnitude estimation',
                'bootstrap': 'Resampling-based confidence intervals'
            },
            'significance_levels': ANALYSIS_CONFIG['significance_levels'],
            'autocorrelation_thresholds': ANALYSIS_CONFIG['autocorr_thresholds'],
            'bootstrap_iterations': ANALYSIS_CONFIG.get('bootstrap_iterations', 1000)
        }
    
    def _generate_methodology_report(self, trend_results, seasonal_results, dataset_name, variable):
        """Generate comprehensive methodology report"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""# Statistical Analysis Report: {dataset_name} {variable.title()} Albedo

**Analysis Date:** {timestamp}
**Dataset:** {dataset_name}
**Variable:** {variable.title()} albedo

## Executive Summary

This report presents a comprehensive statistical analysis of albedo trends for the Saskatchewan Glacier using {dataset_name} data. The analysis employs robust non-parametric statistical methods to detect and quantify temporal trends in albedo across different ice coverage fractions.

## Methodology

### Statistical Methods

1. **Mann-Kendall Trend Test**
   - Non-parametric test for monotonic trends
   - Robust to outliers and non-normal distributions
   - Null hypothesis: No monotonic trend exists

2. **Sen's Slope Estimator**
   - Robust estimate of trend magnitude
   - Median of all possible pairwise slopes
   - Less sensitive to outliers than linear regression

3. **Bootstrap Confidence Intervals**
   - Resampling-based uncertainty quantification
   - {ANALYSIS_CONFIG.get('bootstrap_iterations', 1000)} iterations
   - 95% confidence intervals for trend estimates

4. **Autocorrelation Analysis**
   - Assessment of temporal correlation in residuals
   - Lag-1 autocorrelation coefficient
   - Significance threshold: |r| > 0.1

### Data Processing

- **Quality Control:** Applied MODIS quality flags
- **Temporal Coverage:** {min([r['data_range']['start'] for r in trend_results.values() if not r.get('error', False)])} to {max([r['data_range']['end'] for r in trend_results.values() if not r.get('error', False)])}
- **Fraction Classes:** Ice coverage percentages (0-25%, 25-50%, 50-75%, 75-90%, 90-100%)

## Results Summary

"""
        
        # Add results summary
        valid_results = [r for r in trend_results.values() if not r.get('error', False)]
        significant_results = [r for r in valid_results if r['mann_kendall']['p_value'] < 0.05]
        
        report += f"""
### Key Findings

- **Total Fractions Analyzed:** {len(valid_results)}
- **Significant Trends (p < 0.05):** {len(significant_results)}
- **Data Quality:** Mean completeness across fractions

### Trend Directions

"""
        
        trends = [r['mann_kendall']['trend'] for r in valid_results]
        report += f"- **Increasing Trends:** {trends.count('increasing')}\n"
        report += f"- **Decreasing Trends:** {trends.count('decreasing')}\n"
        report += f"- **No Significant Trend:** {trends.count('no trend')}\n\n"
        
        # Add detailed results for significant trends
        if significant_results:
            report += "### Significant Trends (p < 0.05)\n\n"
            for result in significant_results:
                mk = result['mann_kendall']
                sen = result['sen_slope']
                report += f"**{result['label']}:**\n"
                report += f"- Trend: {mk['trend']} ({get_significance_marker(mk['p_value'])})\n"
                report += f"- p-value: {format_pvalue(mk['p_value'])}\n"
                report += f"- Sen's slope: {sen['slope_per_decade']:.6f} per decade\n"
                report += f"- Kendall's τ: {mk['tau']:.4f}\n\n"
        
        report += """
## Statistical Interpretation

### Significance Levels
- *** p < 0.001 (highly significant)
- ** p < 0.01 (very significant)
- * p < 0.05 (significant)
- ns p ≥ 0.05 (not significant)

### Data Quality Considerations
- Autocorrelation assessment for temporal independence
- Bootstrap confidence intervals for robust uncertainty estimation
- Quality flags applied for data reliability

## Citation
Please cite this analysis as:
Saskatchewan Glacier Albedo Trend Analysis using {dataset_name} data, generated on {timestamp}.

## References
- Mann, H. K. (1945). Nonparametric tests against trend. Econometrica, 13(3), 245-259.
- Sen, P. K. (1968). Estimates of the regression coefficient based on Kendall's tau. Journal of the American Statistical Association, 63(324), 1379-1389.
- Kendall, M. G. (1975). Rank Correlation Methods. Griffin, London.
"""
        
        return report
    
    def _generate_citation_documentation(self, dataset_name, analysis_summary):
        """Generate citation-ready documentation"""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        citation = f"""Saskatchewan Glacier Albedo Analysis - Citation Information
============================================================

Dataset: {dataset_name}
Analysis Date: {timestamp}
Method: Mann-Kendall trend analysis with Sen's slope estimation

Suggested Citation:
Saskatchewan Glacier Albedo Trend Analysis. {dataset_name} dataset processed with 
Mann-Kendall trend detection and Sen's slope estimation. Analysis conducted on {timestamp}.

Data Source:
- MODIS/Terra Surface Reflectance data
- NASA/USGS Land Processes DAAC
- Processed using Google Earth Engine

Statistical Methods:
- Mann-Kendall trend test (Mann, 1945; Kendall, 1975)
- Sen's slope estimator (Sen, 1968)
- Bootstrap confidence intervals (Efron, 1979)

Software:
- Python statistical analysis
- Plotly visualization
- Pandas data processing

Analysis Parameters:
- Significance levels: α = 0.001, 0.01, 0.05
- Bootstrap iterations: {ANALYSIS_CONFIG.get('bootstrap_iterations', 1000)}
- Temporal coverage: 2010-2024
- Spatial resolution: 500m

Quality Assurance:
- MODIS quality flags applied
- Autocorrelation assessment performed
- Bootstrap uncertainty quantification

Contact:
Generated by Saskatchewan Glacier Albedo Analysis Dashboard
For questions about methodology or data processing, please refer to the 
methodology documentation.
"""
        
        return citation