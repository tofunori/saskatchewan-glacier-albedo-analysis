"""
Saskatchewan Glacier Albedo Analysis - Academic Dashboard
=========================================================

Enhanced academic dashboard with comprehensive statistical analysis integration
providing publication-quality results and visualizations.

Features:
- Comprehensive Mann-Kendall trend analysis
- Sen's slope estimation with bootstrap confidence intervals
- Academic-quality visualizations
- Statistical results export
- Publication-ready outputs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shiny import App, render, ui, reactive
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import our new academic modules
from dashboard.statistical_analysis import DashboardStatisticalAnalyzer
from dashboard.academic_plots import AcademicPlotGenerator
from dashboard.export_manager import AcademicExportManager

# Configuration imports
try:
    from config import (FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS, 
                       MCD43A3_CONFIG, MOD10A1_CONFIG, ELEVATION_CONFIG,
                       ANALYSIS_CONFIG)
except ImportError:
    # Fallback configuration
    FRACTION_CLASSES = ['pure_ice', 'mostly_ice', 'mixed_high', 'mixed_low', 'border']
    CLASS_LABELS = {
        'pure_ice': '90-100% (Pure Ice)',
        'mostly_ice': '75-90% (Mostly Ice)', 
        'mixed_high': '50-75% (Mixed High)',
        'mixed_low': '25-50% (Mixed Low)',
        'border': '0-25% (Border)'
    }
    FRACTION_COLORS = {
        'pure_ice': 'blue',
        'mostly_ice': 'lightblue',
        'mixed_high': 'gold',
        'mixed_low': 'orange',
        'border': 'red'
    }
    ANALYSIS_CONFIG = {
        'bootstrap_iterations': 1000,
        'significance_levels': [0.001, 0.01, 0.05]
    }

# Global cache for data and analysis results
global_cache = {
    'data': {},
    'analysis': {},
    'plots': {}
}

def load_dashboard_data(dataset_type='MCD43A3'):
    """Load data with proper error handling for dashboard use"""
    if dataset_type in global_cache['data']:
        return global_cache['data'][dataset_type]
    
    try:
        # Select dataset configuration
        if dataset_type == 'MOD10A1':
            config = MOD10A1_CONFIG
        elif dataset_type == 'MOD10A1_Elevation':
            config = ELEVATION_CONFIG
        else:
            config = MCD43A3_CONFIG
        
        # Load data with correct path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(project_root, config['csv_path'])
        
        print(f"Loading {dataset_type} data from: {csv_path}")
        
        # Simple CSV loading for dashboard
        df = pd.read_csv(csv_path)
        
        # Basic data preparation
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Convert numeric columns
        for col in df.columns:
            if col.endswith('_mean') or col.endswith('_median'):
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with invalid dates
        df = df.dropna(subset=['date'])
        
        # Add temporal columns
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['decimal_year'] = df['year'] + (df['date'].dt.dayofyear - 1) / 365.25
        
        # Add dataset type for reference
        df['dataset'] = dataset_type
        
        print(f"✓ {dataset_type} data loaded successfully: {len(df)} rows, {len(df.columns)} columns")
        global_cache['data'][dataset_type] = df
        return df
        
    except Exception as e:
        print(f"Error loading {dataset_type} data: {e}")
        # Return empty dataframe
        empty_df = pd.DataFrame({
            'date': pd.to_datetime([]),
            'dataset': [],
            'year': [],
            'month': [],
            'decimal_year': []
        })
        global_cache['data'][dataset_type] = empty_df
        return empty_df

# UI Definition with Academic Layout
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("📊 Dataset Selection"),
        ui.input_radio_buttons(
            "dataset_type",
            "Choose MODIS Dataset:",
            choices={
                "MCD43A3": "General Albedo (16-day composite)",
                "MOD10A1": "Snow Albedo (Daily)",
                "MOD10A1_Elevation": "Snow Albedo by Elevation"
            },
            selected="MCD43A3"
        ),
        
        ui.h3("📈 Analysis Parameters"),
        ui.input_selectize(
            "variable",
            "Statistical Variable:",
            choices={
                "mean": "Mean Albedo",
                "median": "Median Albedo"
            },
            selected="mean"
        ),
        
        ui.input_selectize(
            "fraction_class",
            "Fraction Class:",
            choices={fc: CLASS_LABELS[fc] for fc in FRACTION_CLASSES},
            selected="pure_ice"
        ),
        
        ui.input_numeric(
            "bootstrap_n",
            "Bootstrap Iterations:",
            value=1000,
            min=100,
            max=2000,
            step=100
        ),
        
        ui.input_selectize(
            "significance_level",
            "Significance Level:",
            choices={
                "0.05": "α = 0.05 (95% confidence)",
                "0.01": "α = 0.01 (99% confidence)", 
                "0.001": "α = 0.001 (99.9% confidence)"
            },
            selected="0.05"
        ),
        
        ui.h3("📤 Export Options"),
        ui.input_action_button("export_results", "Export Statistical Results", class_="btn-primary"),
        ui.input_action_button("export_figures", "Export All Figures", class_="btn-secondary"),
        ui.input_action_button("export_report", "Generate Report", class_="btn-info"),
        
        ui.br(),
        ui.p("📅 Period: 2010-2024", style="font-size: 12px; color: gray;"),
        ui.p("🔬 Academic-Grade Analysis", style="font-size: 12px; color: gray;"),
        width=320
    ),
    
    # Main content area
    ui.div(
        ui.h1("🏔️ Saskatchewan Glacier Albedo Analysis", style="text-align: center;"),
        ui.p("Academic Dashboard for MODIS Albedo Trend Analysis (2010-2024)", 
             style="text-align: center; font-size: 18px; color: #666;"),
        
        # Navigation tabs for different analysis sections
        ui.navset_tab(
            ui.nav_panel(
                "📊 Overview",
                ui.output_ui("dataset_info"),
                ui.h3("Data Summary"),
                ui.output_table("data_summary")
            ),
            
            ui.nav_panel(
                "📈 Trend Analysis", 
                ui.h3("Mann-Kendall Trend Analysis with Sen's Slope"),
                ui.output_ui("trend_analysis_results"),
                ui.h4("Comprehensive Trends Visualization"),
                ui.output_ui("comprehensive_trends_plot")
            ),
            
            ui.nav_panel(
                "🔄 Bootstrap Analysis",
                ui.h3("Bootstrap Confidence Intervals"),
                ui.output_ui("bootstrap_analysis_results"),
                ui.h4("Bootstrap Distributions"),
                ui.output_ui("bootstrap_plots")
            ),
            
            ui.nav_panel(
                "📅 Seasonal Patterns",
                ui.h3("Monthly and Seasonal Trend Analysis"),
                ui.output_ui("seasonal_analysis_results"),
                ui.h4("Seasonal Patterns Visualization"),
                ui.output_ui("seasonal_plots")
            ),
            
            ui.nav_panel(
                "🔗 Correlation Analysis",
                ui.h3("Inter-Fraction Correlation Matrix"),
                ui.output_ui("correlation_results"),
                ui.h4("Correlation Matrix Visualization"),
                ui.output_ui("correlation_plot")
            ),
            
            ui.nav_panel(
                "📋 Statistical Tables",
                ui.h3("Comprehensive Statistical Results"),
                ui.output_ui("export_status"),
                ui.h4("Detailed Results Table"),
                ui.output_table("comprehensive_results_table"),
                ui.h4("Summary Statistics"),
                ui.output_table("summary_statistics_table")
            )
        )
    ),
    
    title="Saskatchewan Glacier Albedo - Academic Dashboard"
)

def server(input, output, session):
    
    # Reactive data loading
    @reactive.calc
    def current_data():
        """Get current dataset based on selection"""
        dataset_type = input.dataset_type()
        return load_dashboard_data(dataset_type)
    
    # Reactive statistical analysis
    @reactive.calc
    def statistical_analysis():
        """Perform comprehensive statistical analysis"""
        cache_key = f"{input.dataset_type()}_{input.variable()}_{input.bootstrap_n()}"
        
        if cache_key in global_cache['analysis']:
            return global_cache['analysis'][cache_key]
        
        df = current_data()
        if df.empty:
            return None
        
        # Create analyzer
        analyzer = DashboardStatisticalAnalyzer(df, input.dataset_type())
        
        # Perform comprehensive analysis
        trend_results = analyzer.calculate_comprehensive_trends(
            variable=input.variable(),
            bootstrap_n=input.bootstrap_n()
        )
        
        # Seasonal analysis
        seasonal_results = analyzer.calculate_seasonal_trends(
            variable=input.variable()
        )
        
        analysis_results = {
            'trend_results': trend_results,
            'seasonal_results': seasonal_results,
            'analyzer': analyzer
        }
        
        global_cache['analysis'][cache_key] = analysis_results
        return analysis_results
    
    # Dataset info
    @render.ui
    def dataset_info():
        """Display current dataset information"""
        df = current_data()
        dataset_type = input.dataset_type()
        
        if df.empty:
            return ui.div(
                ui.div("❌ No data available", class_="alert alert-danger")
            )
        
        try:
            # Get dataset configuration
            if dataset_type == 'MOD10A1':
                config = MOD10A1_CONFIG
            elif dataset_type == 'MOD10A1_Elevation':
                config = ELEVATION_CONFIG
            else:
                config = MCD43A3_CONFIG
            
            return ui.div(
                ui.div(
                    ui.h4(f"📊 {config['name']}: {config['description']}", class_="text-primary"),
                    ui.p(f"⏱️ Temporal Resolution: {config.get('temporal_resolution', 'Unknown')}"),
                    ui.p(f"📈 Total Observations: {len(df):,}"),
                    ui.p(f"📅 Date Range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"),
                    ui.p(f"🗓️ Years Covered: {len(df['year'].unique())} years"),
                    ui.p(f"📊 Analysis Variable: {input.variable().title()}"),
                    class_="alert alert-info"
                )
            )
        except Exception as e:
            return ui.div(
                ui.div(f"⚠️ Error loading dataset info: {e}", class_="alert alert-warning")
            )
    
    # Data summary table
    @render.table
    def data_summary():
        """Basic data summary table"""
        df = current_data()
        if df.empty:
            return pd.DataFrame({"Message": ["No data available"]})
        
        try:
            summary_data = []
            for fraction in FRACTION_CLASSES:
                col_name = f"{fraction}_{input.variable()}"
                if col_name in df.columns:
                    series = df[col_name].dropna()
                    if len(series) > 0:
                        summary_data.append({
                            'Fraction': CLASS_LABELS[fraction],
                            'Count': len(series),
                            'Mean': f"{series.mean():.4f}",
                            'Std': f"{series.std():.4f}",
                            'Min': f"{series.min():.4f}",
                            'Max': f"{series.max():.4f}"
                        })
            
            return pd.DataFrame(summary_data) if summary_data else pd.DataFrame({"Message": ["No valid data"]})
        except Exception as e:
            return pd.DataFrame({"Error": [str(e)]})
    
    # Trend analysis results
    @render.ui
    def trend_analysis_results():
        """Display trend analysis results"""
        analysis = statistical_analysis()
        if not analysis:
            return ui.div("⏳ Running statistical analysis...", class_="alert alert-info")
        
        trend_results = analysis['trend_results']
        
        # Create summary cards
        summary_cards = []
        
        for fraction, result in trend_results.items():
            if result.get('error', False):
                continue
            
            mk = result['mann_kendall']
            sen = result['sen_slope']
            autocorr = result['autocorrelation']
            
            # Determine card color based on significance
            p_value = mk['p_value']
            if p_value < 0.001:
                card_class = "border-danger"
                sig_badge = "badge bg-danger"
                sig_text = "***"
            elif p_value < 0.01:
                card_class = "border-warning" 
                sig_badge = "badge bg-warning"
                sig_text = "**"
            elif p_value < 0.05:
                card_class = "border-success"
                sig_badge = "badge bg-success"
                sig_text = "*"
            else:
                card_class = "border-secondary"
                sig_badge = "badge bg-secondary"
                sig_text = "ns"
            
            # Trend direction emoji
            trend_emoji = {"increasing": "📈", "decreasing": "📉", "no trend": "➡️"}
            
            card_content = ui.div(
                ui.div(
                    ui.h5(f"{result['label']}", class_="card-title"),
                    ui.p(f"{trend_emoji.get(mk['trend'], '❓')} {mk['trend'].title()}", class_="card-text"),
                    ui.p(f"p-value: {p_value:.2e} ", ui.span(sig_text, class_=sig_badge)),
                    ui.p(f"Kendall's τ: {mk['tau']:.4f}"),
                    ui.p(f"Sen's slope: {sen['slope_per_decade']:.6f}/decade"),
                    ui.p(f"Autocorr (lag-1): {autocorr['lag1']:.3f} {autocorr['status']}"),
                    ui.small(f"n = {result['n_obs']} observations", class_="text-muted"),
                    class_="card-body"
                ),
                class_=f"card {card_class}",
                style_="margin: 10px; width: 18rem; display: inline-block; vertical-align: top;"
            )
            
            summary_cards.append(card_content)
        
        return ui.div(*summary_cards) if summary_cards else ui.div("No valid results", class_="alert alert-warning")
    
    # Comprehensive trends plot
    @render.ui  
    def comprehensive_trends_plot():
        """Generate comprehensive trends visualization"""
        analysis = statistical_analysis()
        if not analysis:
            return ui.div("⏳ Generating plots...", class_="alert alert-info")
        
        try:
            plot_generator = AcademicPlotGenerator()
            fig = plot_generator.create_comprehensive_trends_plot(
                analysis['trend_results'], 
                input.variable()
            )
            
            return ui.HTML(fig.to_html(include_plotlyjs="cdn", div_id="trends_plot"))
        except Exception as e:
            return ui.div(f"Error creating plot: {e}", class_="alert alert-danger")
    
    # Bootstrap analysis results
    @render.ui
    def bootstrap_analysis_results():
        """Display bootstrap analysis summary"""
        analysis = statistical_analysis()
        if not analysis:
            return ui.div("⏳ Computing bootstrap intervals...", class_="alert alert-info")
        
        trend_results = analysis['trend_results']
        bootstrap_summary = []
        
        for fraction, result in trend_results.items():
            if result.get('error', False) or result['bootstrap'].get('error', False):
                continue
            
            bootstrap = result['bootstrap']
            
            bootstrap_summary.append(ui.div(
                ui.h5(f"🎯 {result['label']}"),
                ui.p(f"Successful iterations: {bootstrap['n_successful']}/{input.bootstrap_n()}"),
                ui.p(f"Median slope: {bootstrap['slope_median']:.6f}/decade"),
                ui.p(f"95% CI: [{bootstrap['slope_ci_95_low']:.6f}, {bootstrap['slope_ci_95_high']:.6f}]"),
                ui.p(f"Statistical power: {bootstrap['significant_proportion']:.1%}"),
                class_="alert alert-light border-left-primary"
            ))
        
        return ui.div(*bootstrap_summary) if bootstrap_summary else ui.div("No bootstrap results", class_="alert alert-warning")
    
    # Bootstrap plots
    @render.ui
    def bootstrap_plots():
        """Generate bootstrap analysis plots"""
        analysis = statistical_analysis()
        if not analysis:
            return ui.div("⏳ Generating bootstrap plots...", class_="alert alert-info")
        
        try:
            plot_generator = AcademicPlotGenerator()
            fig = plot_generator.create_bootstrap_analysis_plot(
                analysis['trend_results'],
                input.variable()
            )
            
            return ui.HTML(fig.to_html(include_plotlyjs="cdn", div_id="bootstrap_plot"))
        except Exception as e:
            return ui.div(f"Error creating bootstrap plot: {e}", class_="alert alert-danger")
    
    # Seasonal analysis results
    @render.ui
    def seasonal_analysis_results():
        """Display seasonal analysis summary"""
        analysis = statistical_analysis()
        if not analysis:
            return ui.div("⏳ Analyzing seasonal patterns...", class_="alert alert-info")
        
        seasonal_results = analysis['seasonal_results']
        if not seasonal_results:
            return ui.div("No seasonal data available", class_="alert alert-warning")
        
        month_cards = []
        month_names = {6: 'June', 7: 'July', 8: 'August', 9: 'September'}
        
        for month, month_data in seasonal_results.items():
            sig_trends = []
            for fraction, fraction_data in month_data['fractions'].items():
                if fraction_data['mann_kendall']['p_value'] < 0.05:
                    trend = fraction_data['mann_kendall']['trend']
                    slope = fraction_data['sen_slope']['slope_per_decade']
                    sig_trends.append(f"{CLASS_LABELS[fraction]}: {trend} ({slope:.6f}/decade)")
            
            card_content = ui.div(
                ui.h5(f"📅 {month_names[month]}", class_="card-title"),
                ui.p(f"Significant trends: {len(sig_trends)}"),
                *[ui.small(f"• {trend}", class_="d-block") for trend in sig_trends[:3]],
                class_="card-body"
            )
            
            month_cards.append(ui.div(card_content, class_="card border-info", 
                                    style_="margin: 10px; width: 15rem; display: inline-block;"))
        
        return ui.div(*month_cards)
    
    # Seasonal plots
    @render.ui
    def seasonal_plots():
        """Generate seasonal analysis plots"""
        analysis = statistical_analysis()
        if not analysis:
            return ui.div("⏳ Generating seasonal plots...", class_="alert alert-info")
        
        try:
            plot_generator = AcademicPlotGenerator()
            fig = plot_generator.create_seasonal_analysis_plot(
                analysis['seasonal_results'],
                input.variable()
            )
            
            return ui.HTML(fig.to_html(include_plotlyjs="cdn", div_id="seasonal_plot"))
        except Exception as e:
            return ui.div(f"Error creating seasonal plot: {e}", class_="alert alert-danger")
    
    # Correlation results
    @render.ui
    def correlation_results():
        """Display correlation analysis summary"""
        df = current_data()
        if df.empty:
            return ui.div("No data for correlation analysis", class_="alert alert-warning")
        
        try:
            # Calculate correlations between fractions
            correlation_data = {}
            for fraction in FRACTION_CLASSES:
                col_name = f"{fraction}_{input.variable()}"
                if col_name in df.columns:
                    correlation_data[CLASS_LABELS[fraction]] = df[col_name].dropna()
            
            if len(correlation_data) < 2:
                return ui.div("Insufficient fractions for correlation analysis", class_="alert alert-warning")
            
            corr_df = pd.DataFrame(correlation_data)
            correlation_matrix = corr_df.corr()
            
            # Find strongest correlations
            correlations = []
            for i in range(len(correlation_matrix)):
                for j in range(i+1, len(correlation_matrix)):
                    corr_val = correlation_matrix.iloc[i, j]
                    correlations.append({
                        'pair': f"{correlation_matrix.index[i]} ↔ {correlation_matrix.columns[j]}",
                        'correlation': corr_val,
                        'strength': 'Strong' if abs(corr_val) > 0.7 else 'Moderate' if abs(corr_val) > 0.5 else 'Weak'
                    })
            
            # Sort by absolute correlation
            correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
            
            corr_items = []
            for corr in correlations[:5]:  # Top 5 correlations
                corr_items.append(
                    ui.p(f"• {corr['pair']}: {corr['correlation']:.3f} ({corr['strength']})")
                )
            
            return ui.div(
                ui.h5("🔗 Strongest Inter-Fraction Correlations"),
                *corr_items,
                class_="alert alert-info"
            )
            
        except Exception as e:
            return ui.div(f"Error in correlation analysis: {e}", class_="alert alert-danger")
    
    # Correlation plot
    @render.ui
    def correlation_plot():
        """Generate correlation matrix plot"""
        df = current_data()
        if df.empty:
            return ui.div("No data for correlation plot", class_="alert alert-warning")
        
        try:
            plot_generator = AcademicPlotGenerator()
            fig = plot_generator.create_correlation_matrix_plot(df, input.variable())
            
            return ui.HTML(fig.to_html(include_plotlyjs="cdn", div_id="correlation_plot"))
        except Exception as e:
            return ui.div(f"Error creating correlation plot: {e}", class_="alert alert-danger")
    
    # Export status
    @render.ui
    def export_status():
        """Display export status and controls"""
        return ui.div(
            ui.h5("📤 Export Options"),
            ui.p("Use the sidebar buttons to export:"),
            ui.ul(
                ui.li("📊 Statistical Results: Comprehensive tables (CSV, Excel, JSON)"),
                ui.li("📈 Figures: Publication-quality plots (PNG, SVG, PDF)"),
                ui.li("📋 Report: Complete methodology and results document")
            ),
            class_="alert alert-info"
        )
    
    # Comprehensive results table
    @render.table
    def comprehensive_results_table():
        """Display comprehensive statistical results table"""
        analysis = statistical_analysis()
        if not analysis:
            return pd.DataFrame({"Message": ["Analysis in progress..."]})
        
        try:
            analyzer = analysis['analyzer']
            results_table = analyzer.create_results_table(
                analysis['trend_results'], 
                include_bootstrap=True
            )
            
            return results_table
        except Exception as e:
            return pd.DataFrame({"Error": [str(e)]})
    
    # Summary statistics table
    @render.table
    def summary_statistics_table():
        """Display summary statistics"""
        analysis = statistical_analysis()
        if not analysis:
            return pd.DataFrame({"Message": ["Analysis in progress..."]})
        
        try:
            analyzer = analysis['analyzer']
            summary_stats = analyzer.get_summary_statistics(analysis['trend_results'])
            
            return pd.DataFrame([summary_stats]).T.reset_index()
        except Exception as e:
            return pd.DataFrame({"Error": [str(e)]})
    
    # Export button handlers
    @reactive.effect
    @reactive.event(input.export_results)
    def handle_export_results():
        """Handle statistical results export"""
        analysis = statistical_analysis()
        if not analysis:
            return
        
        try:
            export_manager = AcademicExportManager()
            exported_files = export_manager.export_statistical_results(
                analysis['trend_results'],
                input.dataset_type(),
                input.variable(),
                include_bootstrap=True,
                format='all'
            )
            
            print(f"✓ Statistical results exported: {exported_files}")
        except Exception as e:
            print(f"Error exporting results: {e}")
    
    @reactive.effect
    @reactive.event(input.export_figures)
    def handle_export_figures():
        """Handle figure export"""
        analysis = statistical_analysis()
        if not analysis:
            return
        
        try:
            plot_generator = AcademicPlotGenerator()
            export_manager = AcademicExportManager()
            
            # Export main figures
            figures = {
                'trends': plot_generator.create_comprehensive_trends_plot(analysis['trend_results'], input.variable()),
                'bootstrap': plot_generator.create_bootstrap_analysis_plot(analysis['trend_results'], input.variable()),
                'seasonal': plot_generator.create_seasonal_analysis_plot(analysis['seasonal_results'], input.variable()),
                'correlation': plot_generator.create_correlation_matrix_plot(current_data(), input.variable())
            }
            
            for name, fig in figures.items():
                if fig:
                    export_manager.export_figure(
                        fig, 
                        f"{input.dataset_type()}_{input.variable()}_{name}",
                        formats=['png', 'svg']
                    )
            
            print("✓ All figures exported successfully")
        except Exception as e:
            print(f"Error exporting figures: {e}")
    
    @reactive.effect
    @reactive.event(input.export_report)
    def handle_export_report():
        """Handle methodology report export"""
        analysis = statistical_analysis()
        if not analysis:
            return
        
        try:
            export_manager = AcademicExportManager()
            report_path = export_manager.export_methodology_report(
                analysis['trend_results'],
                analysis['seasonal_results'],
                input.dataset_type(),
                input.variable()
            )
            
            print(f"✓ Methodology report exported: {report_path}")
        except Exception as e:
            print(f"Error exporting report: {e}")

app = App(app_ui, server)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)