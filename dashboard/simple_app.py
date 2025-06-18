"""
Simplified Saskatchewan Glacier Albedo Analysis Dashboard
========================================================

A simplified version that focuses on core functionality without complex dependencies.
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
    MCD43A3_CONFIG, MOD10A1_CONFIG,
    FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS
)

# ==========================================
# DATA LOADING FUNCTIONS
# ==========================================

def load_csv_safely(csv_path):
    """Safely load CSV data"""
    try:
        if os.path.exists(csv_path):
            data = pd.read_csv(csv_path)
            # Ensure date column is datetime
            if 'date' in data.columns:
                data['date'] = pd.to_datetime(data['date'])
            return data
        else:
            print(f"Warning: File not found: {csv_path}")
            return None
    except Exception as e:
        print(f"Error loading {csv_path}: {e}")
        return None

@reactive.Calc
def load_datasets():
    """Load available datasets"""
    datasets = {}
    
    # Try to load MCD43A3
    mcd43a3_data = load_csv_safely(MCD43A3_CONFIG['csv_path'])
    if mcd43a3_data is not None:
        datasets['MCD43A3'] = mcd43a3_data
    
    # Try to load MOD10A1
    mod10a1_data = load_csv_safely(MOD10A1_CONFIG['csv_path'])
    if mod10a1_data is not None:
        datasets['MOD10A1'] = mod10a1_data
    
    return datasets

# ==========================================
# UI DEFINITION
# ==========================================

app_ui = ui.page_fluid(
    # Custom CSS
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
        ui.p("Interactive exploration of MODIS satellite albedo data (2010-2024)", 
             style="margin: 10px 0 0 0; opacity: 0.9;"),
        class_="main-header"
    ),
    
    # Main layout
    ui.layout_sidebar(
        # Sidebar
        ui.sidebar(
            ui.div(
                ui.h4("📊 Dataset Selection"),
                ui.input_radio_buttons(
                    "dataset",
                    "Choose Dataset:",
                    choices={
                        "MCD43A3": "MCD43A3 (General Albedo)",
                        "MOD10A1": "MOD10A1 (Snow Albedo)",
                        "COMPARISON": "📊 Compare Datasets"
                    },
                    selected="MCD43A3"
                ),
                class_="sidebar-panel"
            ),
            
            ui.div(
                ui.h4("🎯 Filters"),
                ui.input_checkbox_group(
                    "fractions",
                    "Glacier Fraction Classes:",
                    choices={k: v for k, v in CLASS_LABELS.items()},
                    selected=["pure_ice", "mostly_ice"]
                ),
                ui.input_date_range(
                    "date_range",
                    "Date Range:",
                    start="2010-01-01",
                    end="2024-12-31",
                    min="2010-01-01",
                    max="2024-12-31"
                ),
                class_="sidebar-panel"
            ),
            
            ui.div(
                ui.h4("📈 Options"),
                ui.input_select(
                    "analysis_variable",
                    "Variable:",
                    choices={"mean": "Mean Albedo", "median": "Median Albedo"},
                    selected="mean"
                ),
                ui.input_checkbox(
                    "show_trends", 
                    "Show Trends", 
                    value=True
                ),
                class_="sidebar-panel"
            ),
            
            width=300
        ),
        
        # Main content
        ui.div(
            # Summary stats
            ui.div(
                ui.output_ui("summary_stats"),
                class_="metric-card"
            ),
            
            # Tabs
            ui.navset_tab(
                ui.nav_panel(
                    "📈 Time Series",
                    ui.div(
                        ui.output_plot("timeseries_plot"),
                        class_="plot-container"
                    )
                ),
                
                ui.nav_panel(
                    "📊 Statistics",
                    ui.div(
                        ui.output_plot("stats_plot"),
                        class_="plot-container"
                    )
                ),
                
                ui.nav_panel(
                    "🔄 Comparison",
                    ui.div(
                        ui.output_plot("comparison_plot"),
                        class_="plot-container"
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
    
    @reactive.Calc
    def filtered_data():
        """Get filtered data based on user selections"""
        datasets = load_datasets()
        dataset_name = input.dataset()
        
        if dataset_name == "COMPARISON":
            return datasets
        
        if dataset_name not in datasets:
            return None
            
        data = datasets[dataset_name].copy()
        
        # Filter by date range
        start_date = pd.to_datetime(input.date_range()[0])
        end_date = pd.to_datetime(input.date_range()[1])
        
        mask = (data['date'] >= start_date) & (data['date'] <= end_date)
        return data[mask]
    
    @output
    @render.ui
    def summary_stats():
        """Display summary statistics"""
        data = filtered_data()
        if data is None:
            return ui.div("No data available")
        
        stats = []
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                values = data[col_name].dropna()
                if len(values) > 0:
                    stats.append(
                        ui.div(
                            ui.h5(CLASS_LABELS.get(fraction, fraction)),
                            ui.p(f"Mean: {values.mean():.3f}"),
                            ui.p(f"Std: {values.std():.3f}"),
                            ui.p(f"Count: {len(values):,}"),
                            style="display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px;"
                        )
                    )
        
        return ui.div(*stats) if stats else ui.div("No data for selected fractions")
    
    @output
    @render.plot
    def timeseries_plot():
        """Create time series plot"""
        data = filtered_data()
        if data is None or input.dataset() == "COMPARISON":
            return go.Figure().add_annotation(
                text="Select a dataset to view time series",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        fig = go.Figure()
        
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                color = FRACTION_COLORS.get(fraction, 'blue')
                label = CLASS_LABELS.get(fraction, fraction)
                
                # Plot data
                fig.add_trace(go.Scatter(
                    x=data['date'],
                    y=data[col_name],
                    mode='lines+markers',
                    name=label,
                    line=dict(color=color, width=2),
                    marker=dict(size=4)
                ))
        
        fig.update_layout(
            title=f"Albedo Time Series - {input.dataset()}",
            xaxis_title="Date",
            yaxis_title=f"{input.analysis_variable().title()} Albedo",
            height=500,
            hovermode='x unified',
            template="plotly_white"
        )
        
        return fig
    
    @output
    @render.plot
    def stats_plot():
        """Create statistics plot"""
        data = filtered_data()
        if data is None or input.dataset() == "COMPARISON":
            return go.Figure().add_annotation(
                text="Select a dataset to view statistics",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        # Create monthly statistics
        data['month'] = data['date'].dt.month
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=['Monthly Averages', 'Data Distribution']
        )
        
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                color = FRACTION_COLORS.get(fraction, 'blue')
                label = CLASS_LABELS.get(fraction, fraction)
                
                # Monthly averages
                monthly_avg = data.groupby('month')[col_name].mean()
                fig.add_trace(
                    go.Scatter(
                        x=monthly_avg.index,
                        y=monthly_avg.values,
                        mode='lines+markers',
                        name=label,
                        line=dict(color=color)
                    ),
                    row=1, col=1
                )
                
                # Box plot
                fig.add_trace(
                    go.Box(
                        y=data[col_name].dropna(),
                        name=label,
                        marker_color=color
                    ),
                    row=2, col=1
                )
        
        fig.update_layout(
            height=600,
            title_text="Statistical Analysis",
            template="plotly_white"
        )
        
        return fig
    
    @output
    @render.plot
    def comparison_plot():
        """Create comparison plot"""
        if input.dataset() != "COMPARISON":
            return go.Figure().add_annotation(
                text="Switch to 'Compare Datasets' mode to view comparison",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        datasets = filtered_data()
        if not datasets or 'MCD43A3' not in datasets or 'MOD10A1' not in datasets:
            return go.Figure().add_annotation(
                text="Both datasets required for comparison",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        # Simple scatter plot comparison
        fig = go.Figure()
        
        mcd43a3_data = datasets['MCD43A3']
        mod10a1_data = datasets['MOD10A1']
        
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            
            if col_name in mcd43a3_data.columns and col_name in mod10a1_data.columns:
                # Merge on date
                merged = pd.merge(
                    mcd43a3_data[['date', col_name]].rename(columns={col_name: 'mcd43a3'}),
                    mod10a1_data[['date', col_name]].rename(columns={col_name: 'mod10a1'}),
                    on='date'
                )
                
                if len(merged) > 0:
                    color = FRACTION_COLORS.get(fraction, 'blue')
                    label = CLASS_LABELS.get(fraction, fraction)
                    
                    correlation = merged['mcd43a3'].corr(merged['mod10a1'])
                    
                    fig.add_trace(go.Scatter(
                        x=merged['mcd43a3'],
                        y=merged['mod10a1'],
                        mode='markers',
                        name=f'{label} (r={correlation:.3f})',
                        marker=dict(color=color, size=5, opacity=0.6)
                    ))
        
        # Add 1:1 line
        if len(fig.data) > 0:
            all_x = []
            all_y = []
            for trace in fig.data:
                all_x.extend(trace.x)
                all_y.extend(trace.y)
            
            min_val = min(min(all_x), min(all_y))
            max_val = max(max(all_x), max(all_y))
            
            fig.add_trace(go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                name='1:1 Line',
                line=dict(color='red', dash='dash')
            ))
        
        fig.update_layout(
            title="Dataset Comparison",
            xaxis_title="MCD43A3 Albedo",
            yaxis_title="MOD10A1 Albedo",
            height=500,
            template="plotly_white"
        )
        
        return fig

# ==========================================
# APP CREATION
# ==========================================

app = App(app_ui, server)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)