"""
Saskatchewan Glacier Albedo Analysis Dashboard
=============================================

Interactive dashboard for exploring 15 years of MODIS albedo data using Python Shiny.
Provides comprehensive analysis tools, visualizations, and statistical insights.
"""

from shiny import App, ui, render, reactive
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    MCD43A3_CONFIG, MOD10A1_CONFIG, ELEVATION_CONFIG,
    FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS,
    ANALYSIS_CONFIG, get_dataset_config
)
from data.handler import AlbedoDataHandler
from data.dataset_manager import DatasetManager
from analysis.trends import TrendAnalyzer
from analysis.seasonal import SeasonalAnalyzer
from analysis.comparison import ComparisonAnalyzer
from visualization.charts import ChartGenerator

# Import dashboard components
from dashboard.components import (
    create_dataset_selector, create_filter_panel, create_analysis_options,
    create_summary_card, create_plot_card, create_data_table_card,
    create_export_panel, create_info_panel, create_advanced_filters
)
from dashboard.plots import (
    create_timeseries_plot, create_seasonal_plot, create_comparison_plot,
    create_trend_analysis_plot
)

# ==========================================
# DATA LOADING AND PREPARATION
# ==========================================

@reactive.Calc
def get_data_manager():
    """Initialize and return the dataset manager"""
    return DatasetManager()

@reactive.Calc  
def load_dataset_data():
    """Load data for all available datasets"""
    manager = get_data_manager()
    data = {}
    
    # Load MCD43A3 data
    try:
        mcd43a3_handler = AlbedoDataHandler(MCD43A3_CONFIG['csv_path'])
        mcd43a3_handler.load_data()
        data['MCD43A3'] = mcd43a3_handler.data
    except Exception as e:
        print(f"Warning: Could not load MCD43A3 data: {e}")
        data['MCD43A3'] = None
    
    # Load MOD10A1 data
    try:
        mod10a1_handler = AlbedoDataHandler(MOD10A1_CONFIG['csv_path'])
        mod10a1_handler.load_data()
        data['MOD10A1'] = mod10a1_handler.data
    except Exception as e:
        print(f"Warning: Could not load MOD10A1 data: {e}")
        data['MOD10A1'] = None
    
    return data

# ==========================================
# UI DEFINITION
# ==========================================

app_ui = ui.page_fluid(
    # Custom CSS for styling
    ui.tags.head(
        ui.tags.style("""
            .main-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                margin: -15px -15px 20px -15px;
                border-radius: 0 0 10px 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .metric-card {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .sidebar-panel {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
            }
            .plot-container {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                margin: 10px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        """)
    ),
    
    # Main header
    ui.div(
        ui.h1("🏔️ Saskatchewan Glacier Albedo Analysis Dashboard", class_="main-header"),
        ui.p("Interactive exploration of 15 years (2010-2024) of MODIS satellite albedo data", 
             style="margin: 10px 0 0 0; opacity: 0.9;"),
        class_="main-header"
    ),
    
    # Main layout with sidebar and content
    ui.layout_sidebar(
        # Sidebar with controls
        ui.sidebar(
            create_dataset_selector(),
            create_filter_panel(),
            create_analysis_options(),
            create_advanced_filters(),
            create_export_panel(),
            create_info_panel(),
            width=320
        ),
        
        # Main content area
        ui.div(
            # Summary statistics row
            ui.div(
                ui.output_ui("summary_metrics"),
                class_="metric-card"
            ),
            
            # Tabs for different visualizations
            ui.navset_tab(
                ui.nav_panel(
                    "📈 Time Series",
                    ui.row(
                        ui.column(12,
                            create_plot_card("Interactive Time Series Analysis", "timeseries_plot", "600px")
                        )
                    ),
                    ui.row(
                        ui.column(4,
                            ui.output_ui("timeseries_stats")
                        ),
                        ui.column(8,
                            create_plot_card("Trend Analysis", "trend_analysis_plot", "400px")
                        )
                    )
                ),
                
                ui.nav_panel(
                    "📊 Statistical Analysis", 
                    ui.row(
                        ui.column(6, 
                            create_data_table_card("Detailed Trend Results", "trend_table")
                        ),
                        ui.column(6,
                            create_plot_card("Statistical Summary", "stats_summary_plot", "400px")
                        )
                    ),
                    ui.row(
                        ui.column(12,
                            create_plot_card("Comprehensive Seasonal Analysis", "seasonal_plot", "600px")
                        )
                    )
                ),
                
                ui.nav_panel(
                    "🔄 Dataset Comparison",
                    ui.row(
                        ui.column(12,
                            create_plot_card("Multi-Dataset Comparison Analysis", "comparison_plot", "700px")
                        )
                    ),
                    ui.row(
                        ui.column(6,
                            create_data_table_card("Correlation Statistics", "correlation_table")
                        ),
                        ui.column(6,
                            ui.output_ui("comparison_stats")
                        )
                    )
                ),
                
                ui.nav_panel(
                    "🏔️ Elevation Analysis",
                    ui.row(
                        ui.column(12,
                            create_plot_card("Elevation Stratified Analysis", "elevation_plot", "600px")
                        )
                    ),
                    ui.row(
                        ui.column(6,
                            create_data_table_card("Elevation Zone Statistics", "elevation_table")
                        ),
                        ui.column(6,
                            ui.output_ui("elevation_summary")
                        )
                    )
                ),
                
                ui.nav_panel(
                    "📋 Data Quality & Coverage",
                    ui.row(
                        ui.column(6,
                            create_plot_card("Quality Distribution", "quality_plot", "400px")
                        ),
                        ui.column(6,
                            create_plot_card("Data Coverage", "coverage_plot", "400px")
                        )
                    ),
                    ui.row(
                        ui.column(12,
                            create_data_table_card("Quality Metrics Summary", "quality_table")
                        )
                    )
                )
            )
        )
    )
)

# ==========================================
# SERVER LOGIC
# ==========================================

def server(input, output, session):
    
    # Reactive data filtering
    @reactive.Calc
    def filtered_data():
        """Filter data based on user selections"""
        all_data = load_dataset_data()
        dataset_name = input.dataset()
        
        if dataset_name == "COMPARISON":
            return all_data
        
        data = all_data.get(dataset_name)
        if data is None:
            return None
            
        # Filter by selected fractions
        fraction_cols = [f"{frac}_{input.analysis_variable()}" for frac in input.fractions()]
        available_cols = [col for col in fraction_cols if col in data.columns]
        
        if not available_cols:
            return None
            
        # Filter by date range
        data['date'] = pd.to_datetime(data['date'])
        start_date = pd.to_datetime(input.date_range()[0])
        end_date = pd.to_datetime(input.date_range()[1])
        
        mask = (data['date'] >= start_date) & (data['date'] <= end_date)
        filtered = data[mask].copy()
        
        return filtered
    
    # Summary metrics
    @output
    @render.ui
    def summary_metrics():
        data = filtered_data()
        if data is None:
            return ui.div("No data available for current selection")
        
        # Calculate basic statistics
        fraction_cols = [f"{frac}_{input.analysis_variable()}" for frac in input.fractions()]
        available_cols = [col for col in fraction_cols if col in data.columns]
        
        if not available_cols:
            return ui.div("No data columns available")
        
        stats = []
        for col in available_cols:
            fraction_name = col.replace(f"_{input.analysis_variable()}", "")
            values = data[col].dropna()
            if len(values) > 0:
                stats.append(
                    ui.div(
                        ui.h5(CLASS_LABELS.get(fraction_name, fraction_name)),
                        ui.p(f"📊 Mean: {values.mean():.3f}"),
                        ui.p(f"📊 Std: {values.std():.3f}"),
                        ui.p(f"📊 Observations: {len(values):,}"),
                        style="display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px;"
                    )
                )
        
        return ui.div(*stats)
    
    # Time series plot
    @output
    @render.plot  
    def timeseries_plot():
        data = filtered_data()
        if data is None:
            return go.Figure().add_annotation(
                text="No data available for current selection",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        return create_timeseries_plot(
            data=data,
            fractions=input.fractions(),
            variable=input.analysis_variable(),
            show_trends=input.show_trends(),
            show_seasonal=input.show_seasonal()
        )
    
    # Trend analysis table
    @output
    @render.table
    def trend_table():
        data = filtered_data()
        if data is None:
            return pd.DataFrame()
        
        # Perform trend analysis
        analyzer = TrendAnalyzer(data)
        
        fraction_cols = [f"{frac}_{input.analysis_variable()}" for frac in input.fractions()]
        available_cols = [col for col in fraction_cols if col in data.columns]
        
        results = []
        for col in available_cols:
            fraction_name = col.replace(f"_{input.analysis_variable()}", "")
            try:
                trend_result = analyzer.analyze_single_fraction(fraction_name, input.analysis_variable())
                results.append({
                    'Fraction': CLASS_LABELS.get(fraction_name, fraction_name),
                    'Trend': trend_result.get('trend', 'N/A'),
                    'Slope': f"{trend_result.get('slope', 0):.6f}",
                    'P-value': f"{trend_result.get('p_value', 1):.4f}",
                    'Significance': trend_result.get('significance', 'ns')
                })
            except Exception as e:
                results.append({
                    'Fraction': CLASS_LABELS.get(fraction_name, fraction_name),
                    'Trend': 'Error',
                    'Slope': 'N/A',
                    'P-value': 'N/A', 
                    'Significance': 'N/A'
                })
        
        return pd.DataFrame(results) if results else pd.DataFrame()
    
    # Seasonal patterns plot
    @output
    @render.plot
    def seasonal_plot():
        data = filtered_data()
        if data is None:
            return go.Figure().add_annotation(
                text="No data available for seasonal analysis",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        return create_seasonal_plot(
            data=data,
            fractions=input.fractions(),
            variable=input.analysis_variable()
        )
    
    # Comparison plot  
    @output
    @render.plot
    def comparison_plot():
        if input.dataset() != "COMPARISON":
            return go.Figure().add_annotation(
                text="Switch to 'Compare Datasets' to view comparison analysis",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        all_data = load_dataset_data()
        mcd43a3_data = all_data.get('MCD43A3')
        mod10a1_data = all_data.get('MOD10A1')
        
        if mcd43a3_data is None or mod10a1_data is None:
            return go.Figure().add_annotation(
                text="Both MCD43A3 and MOD10A1 datasets required for comparison",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        return create_comparison_plot(
            data1=mcd43a3_data,
            data2=mod10a1_data,
            fractions=input.fractions(),
            variable=input.analysis_variable(),
            dataset1_name="MCD43A3",
            dataset2_name="MOD10A1"
        )
    
    # Trend analysis plot
    @output
    @render.plot
    def trend_analysis_plot():
        data = filtered_data()
        if data is None:
            return go.Figure().add_annotation(
                text="No data available for trend analysis",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        return create_trend_analysis_plot(
            data=data,
            fractions=input.fractions(),
            variable=input.analysis_variable()
        )
    
    # Time series statistics
    @output
    @render.ui
    def timeseries_stats():
        data = filtered_data()
        if data is None:
            return ui.div("No statistics available")
        
        stats_cards = []
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                values = data[col_name].dropna()
                if len(values) > 0:
                    stats_cards.append(
                        create_summary_card(
                            title=CLASS_LABELS.get(fraction, fraction),
                            value=f"{values.mean():.3f}",
                            subtitle=f"σ={values.std():.3f}, n={len(values):,}",
                            color="primary"
                        )
                    )
        
        return ui.div(*stats_cards)
    
    # Statistics summary plot
    @output
    @render.plot
    def stats_summary_plot():
        data = filtered_data()
        if data is None:
            return go.Figure().add_annotation(
                text="No data for statistics",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        # Create summary statistics visualization
        fig = go.Figure()
        
        stats_data = []
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                values = data[col_name].dropna()
                if len(values) > 0:
                    stats_data.append({
                        'fraction': CLASS_LABELS.get(fraction, fraction),
                        'mean': values.mean(),
                        'std': values.std(),
                        'min': values.min(),
                        'max': values.max()
                    })
        
        if stats_data:
            stats_df = pd.DataFrame(stats_data)
            
            fig.add_trace(go.Bar(
                x=stats_df['fraction'],
                y=stats_df['mean'],
                error_y=dict(type='data', array=stats_df['std']),
                name='Mean ± Std',
                marker_color=[FRACTION_COLORS.get(f, 'blue') for f in input.fractions() if f in [k for k, v in CLASS_LABELS.items() if v in stats_df['fraction'].values]]
            ))
            
            fig.update_layout(
                title="Statistical Summary",
                xaxis_title="Fraction Class",
                yaxis_title=f"{input.analysis_variable().title()} Albedo",
                template="plotly_white",
                height=400
            )
        
        return fig
    
    # Placeholder plots for elevation and quality
    @output
    @render.plot
    def elevation_plot():
        return go.Figure().add_annotation(text="Elevation analysis implementation in progress...", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    @output
    @render.plot  
    def quality_plot():
        return go.Figure().add_annotation(text="Quality analysis implementation in progress...",
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    @output
    @render.plot
    def coverage_plot():
        return go.Figure().add_annotation(text="Coverage analysis implementation in progress...",
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Placeholder tables
    @output
    @render.table
    def correlation_table():
        return pd.DataFrame()
    
    @output
    @render.table
    def elevation_table():
        return pd.DataFrame()
    
    @output
    @render.table
    def quality_table():
        return pd.DataFrame()
    
    # Placeholder UI outputs
    @output
    @render.ui
    def comparison_stats():
        return ui.div("Comparison statistics coming soon...")
    
    @output
    @render.ui
    def elevation_summary():
        return ui.div("Elevation summary coming soon...")
    
    # Export functionality
    @output
    @render.text
    def export_status():
        return "Export functionality coming soon..."

# ==========================================
# APP CREATION
# ==========================================

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()