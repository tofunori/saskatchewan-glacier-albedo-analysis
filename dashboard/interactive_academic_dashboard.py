"""
Interactive Saskatchewan Glacier Albedo Analysis - Academic Dashboard
====================================================================

Professional academic-style dashboard with full Plotly interactivity.
Includes zoom, pan, hover, selection, and linked brushing capabilities.
"""

from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from scipy import stats
import sys
import os
from pathlib import Path
from datetime import datetime

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
    
    # Load MCD43A3
    mcd43a3_data = load_csv_safely(MCD43A3_CONFIG['csv_path'])
    if mcd43a3_data is not None:
        datasets['MCD43A3'] = mcd43a3_data
    
    # Load MOD10A1
    mod10a1_data = load_csv_safely(MOD10A1_CONFIG['csv_path'])
    if mod10a1_data is not None:
        datasets['MOD10A1'] = mod10a1_data
    
    return datasets

# ==========================================
# ACADEMIC STYLING
# ==========================================

academic_css = """
.academic-header {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: white;
    padding: 25px;
    margin: -15px -15px 25px -15px;
    border-radius: 0 0 15px 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    font-family: 'Georgia', serif;
}

.academic-title {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 8px;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
}

.academic-subtitle {
    font-size: 16px;
    opacity: 0.9;
    font-style: italic;
    margin: 0;
}

.academic-panel {
    background: white;
    border: 2px solid #e8e9ea;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    font-family: 'Georgia', serif;
}

.academic-section-title {
    color: #1e3c72;
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 15px;
    border-bottom: 2px solid #e8e9ea;
    padding-bottom: 8px;
}

.metric-box {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 15px;
    margin: 8px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    min-width: 140px;
    display: inline-block;
}

.metric-title {
    font-size: 14px;
    color: #495057;
    margin-bottom: 5px;
    font-weight: bold;
}

.metric-value {
    font-size: 20px;
    color: #1e3c72;
    font-weight: bold;
    margin: 5px 0;
}

.metric-subtitle {
    font-size: 12px;
    color: #6c757d;
    margin: 0;
}

.sidebar-control {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 18px;
    font-family: 'Georgia', serif;
}

.control-title {
    color: #1e3c72;
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 12px;
    text-align: center;
}

.interactive-note {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    border: 1px solid #2196f3;
    border-radius: 8px;
    padding: 10px;
    margin: 10px 0;
    font-size: 12px;
    color: #1565c0;
    text-align: center;
}
"""

# ==========================================
# UI DEFINITION
# ==========================================

app_ui = ui.page_fluid(
    # Academic CSS styling
    ui.tags.head(ui.tags.style(academic_css)),
    
    # Academic header
    ui.div(
        ui.div("Interactive Saskatchewan Glacier Albedo Analysis", class_="academic-title"),
        ui.div("Comprehensive MODIS Satellite Data Analysis (2010-2024)", class_="academic-subtitle"),
        ui.div("Interactive Research Dashboard • Zoom • Pan • Hover • Select", class_="academic-subtitle", 
               style="margin-top: 5px; font-size: 14px;"),
        class_="academic-header"
    ),
    
    # Main layout
    ui.layout_sidebar(
        # Academic sidebar
        ui.sidebar(
            ui.div(
                ui.div("📊 Dataset Selection", class_="control-title"),
                ui.input_radio_buttons(
                    "dataset",
                    "",
                    choices={
                        "MCD43A3": "🛰️ MCD43A3 (General Albedo)",
                        "MOD10A1": "❄️ MOD10A1 (Snow Albedo)",
                        "COMPARISON": "📈 Comparative Analysis"
                    },
                    selected="MCD43A3"
                ),
                ui.tags.small("MCD43A3: 16-day composite • MOD10A1: Daily observations", 
                             style="color: #6c757d; font-style: italic;"),
                class_="sidebar-control"
            ),
            
            ui.div(
                ui.div("🎯 Analysis Parameters", class_="control-title"),
                ui.input_checkbox_group(
                    "fractions",
                    "Glacier Coverage Fractions:",
                    choices={k: v for k, v in CLASS_LABELS.items()},
                    selected=["pure_ice", "mostly_ice"]
                ),
                ui.input_select(
                    "analysis_variable",
                    "Statistical Measure:",
                    choices={"mean": "📊 Mean Albedo", "median": "📊 Median Albedo"},
                    selected="mean"
                ),
                class_="sidebar-control"
            ),
            
            ui.div(
                ui.div("📅 Temporal Filtering", class_="control-title"),
                ui.input_date_range(
                    "date_range",
                    "Analysis Period:",
                    start="2010-01-01",
                    end="2024-12-31",
                    min="2010-01-01",
                    max="2024-12-31"
                ),
                ui.input_select(
                    "season_filter",
                    "Seasonal Focus:",
                    choices={
                        "all": "🌍 All Seasons",
                        "summer": "☀️ Summer (JJA)",
                        "melt_season": "🌊 Melt Season (May-Sep)",
                        "winter": "❄️ Winter (Oct-Apr)"
                    },
                    selected="all"
                ),
                class_="sidebar-control"
            ),
            
            ui.div(
                ui.div("🔬 Interactive Options", class_="control-title"),
                ui.input_checkbox("show_trends", "📈 Display Trend Lines", value=True),
                ui.input_checkbox("show_confidence", "📊 Confidence Intervals", value=False),
                ui.input_checkbox("crossfilter", "🔗 Linked Selection", value=True),
                ui.input_select(
                    "plot_theme",
                    "Visualization Theme:",
                    choices={
                        "plotly_white": "🎓 Academic Clean",
                        "simple_white": "📰 Publication",
                        "presentation": "📽️ Presentation"
                    },
                    selected="plotly_white"
                ),
                class_="sidebar-control"
            ),
            
            ui.div(
                "💡 Interactive Features",
                ui.br(),
                "• Zoom: Mouse wheel or zoom tool",
                ui.br(),
                "• Pan: Click and drag",
                ui.br(), 
                "• Hover: Rich data tooltips",
                ui.br(),
                "• Select: Lasso or box selection",
                ui.br(),
                "• Reset: Double-click to reset view",
                class_="interactive-note"
            ),
            
            width=340
        ),
        
        # Main content area
        ui.div(
            # Summary statistics panel
            ui.div(
                ui.div("📊 Dataset Summary Statistics", class_="academic-section-title"),
                ui.output_ui("summary_statistics"),
                class_="academic-panel"
            ),
            
            # Analysis tabs
            ui.navset_tab(
                ui.nav_panel(
                    "📈 Temporal Analysis",
                    ui.div(
                        ui.div("Interactive Time Series Analysis", class_="academic-section-title"),
                        output_widget("timeseries_plot"),
                        class_="academic-panel"
                    ),
                    ui.row(
                        ui.column(6,
                            ui.div(
                                ui.div("Trend Statistics", class_="academic-section-title"),
                                ui.output_table("trend_statistics"),
                                class_="academic-panel"
                            )
                        ),
                        ui.column(6,
                            ui.div(
                                ui.div("Interactive Seasonal Patterns", class_="academic-section-title"),
                                output_widget("seasonal_analysis"),
                                class_="academic-panel"
                            )
                        )
                    )
                ),
                
                ui.nav_panel(
                    "📊 Statistical Analysis",
                    ui.row(
                        ui.column(6,
                            ui.div(
                                ui.div("Interactive Distribution Analysis", class_="academic-section-title"),
                                output_widget("distribution_plot"),
                                class_="academic-panel"
                            )
                        ),
                        ui.column(6,
                            ui.div(
                                ui.div("Interactive Correlation Matrix", class_="academic-section-title"),
                                output_widget("correlation_plot"),
                                class_="academic-panel"
                            )
                        )
                    ),
                    ui.div(
                        ui.div("Interactive Monthly Climatology", class_="academic-section-title"),
                        output_widget("monthly_climatology"),
                        class_="academic-panel"
                    )
                ),
                
                ui.nav_panel(
                    "🔄 Comparative Analysis",
                    ui.div(
                        ui.div("Interactive Multi-Dataset Comparison", class_="academic-section-title"),
                        output_widget("comparison_analysis"),
                        class_="academic-panel"
                    ),
                    ui.row(
                        ui.column(6,
                            ui.div(
                                ui.div("Correlation Analysis", class_="academic-section-title"),
                                ui.output_table("correlation_stats"),
                                class_="academic-panel"
                            )
                        ),
                        ui.column(6,
                            ui.div(
                                ui.div("Interactive Difference Analysis", class_="academic-section-title"),
                                output_widget("difference_plot"),
                                class_="academic-panel"
                            )
                        )
                    )
                ),
                
                ui.nav_panel(
                    "📋 Data Quality",
                    ui.row(
                        ui.column(6,
                            ui.div(
                                ui.div("Interactive Coverage Assessment", class_="academic-section-title"),
                                output_widget("coverage_plot"),
                                class_="academic-panel"
                            )
                        ),
                        ui.column(6,
                            ui.div(
                                ui.div("Quality Metrics", class_="academic-section-title"),
                                ui.output_table("quality_metrics"),
                                class_="academic-panel"
                            )
                        )
                    ),
                    ui.div(
                        ui.div("Interactive Quality Timeline", class_="academic-section-title"),
                        output_widget("quality_timeline"),
                        class_="academic-panel"
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
        data = data[mask]
        
        # Apply seasonal filter
        if input.season_filter() != "all":
            data['month'] = data['date'].dt.month
            if input.season_filter() == "summer":
                data = data[data['month'].isin([6, 7, 8])]
            elif input.season_filter() == "melt_season":
                data = data[data['month'].isin([5, 6, 7, 8, 9])]
            elif input.season_filter() == "winter":
                data = data[data['month'].isin([10, 11, 12, 1, 2, 3, 4])]
        
        return data
    
    @output
    @render.ui
    def summary_statistics():
        """Generate academic-style summary statistics"""
        data = filtered_data()
        if data is None or input.dataset() == "COMPARISON":
            return ui.div("Select a dataset to view summary statistics")
        
        metrics = []
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                values = data[col_name].dropna()
                if len(values) > 0:
                    metrics.append(
                        ui.div(
                            ui.div(CLASS_LABELS.get(fraction, fraction), class_="metric-title"),
                            ui.div(f"{values.mean():.4f}", class_="metric-value"),
                            ui.div(f"σ = {values.std():.4f}", class_="metric-subtitle"),
                            ui.div(f"n = {len(values):,}", class_="metric-subtitle"),
                            class_="metric-box"
                        )
                    )
        
        return ui.div(*metrics, style="text-align: center;") if metrics else ui.div("No data available")
    
    @render_widget
    def timeseries_plot():
        """Create interactive time series plot"""
        data = filtered_data()
        if data is None or input.dataset() == "COMPARISON":
            fig = go.Figure()
            fig.add_annotation(
                text="Select a dataset to view interactive time series analysis",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        fig = go.Figure()
        
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                color = FRACTION_COLORS.get(fraction, '#1f77b4')
                label = CLASS_LABELS.get(fraction, fraction)
                
                # Filter out NaN values
                mask = data[col_name].notna()
                plot_data = data[mask]
                
                if len(plot_data) == 0:
                    continue
                
                # Main time series
                fig.add_trace(go.Scatter(
                    x=plot_data['date'],
                    y=plot_data[col_name],
                    mode='lines+markers',
                    name=label,
                    line=dict(color=color, width=2),
                    marker=dict(size=4, opacity=0.8),
                    hovertemplate=f'<b>{label}</b><br>' +
                                 'Date: %{x}<br>' +
                                 f'{input.analysis_variable().title()}: %{{y:.4f}}<br>' +
                                 '<extra></extra>'
                ))
                
                # Add trend line if requested
                if input.show_trends() and len(plot_data) > 10:
                    try:
                        x_numeric = (plot_data['date'] - plot_data['date'].min()).dt.days
                        slope, intercept, r_value, p_value, std_err = stats.linregress(
                            x_numeric, plot_data[col_name]
                        )
                        
                        trend_y = slope * x_numeric + intercept
                        
                        fig.add_trace(go.Scatter(
                            x=plot_data['date'],
                            y=trend_y,
                            mode='lines',
                            name=f'{label} Trend',
                            line=dict(color=color, width=3, dash='dash'),
                            hovertemplate=f'<b>{label} Trend</b><br>' +
                                         f'Slope: {slope:.6f}/day<br>' +
                                         f'R²: {r_value**2:.3f}<br>' +
                                         f'p-value: {p_value:.4f}<br>' +
                                         '<extra></extra>'
                        ))
                    except Exception as e:
                        print(f"Could not calculate trend for {fraction}: {e}")
        
        # Academic styling with interactivity
        fig.update_layout(
            title=dict(
                text=f"Interactive Time Series Analysis - {input.dataset()} Dataset<br><sub>{input.season_filter().replace('_', ' ').title()} Season</sub>",
                x=0.5,
                font=dict(size=18, family="Georgia, serif")
            ),
            xaxis=dict(
                title="Date",
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            yaxis=dict(
                title=f"{input.analysis_variable().title()} Albedo",
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=600,
            template=input.plot_theme(),
            font=dict(family="Georgia, serif")
        )
        
        # Add range selector and zoom tools
        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(count=5, label="5Y", step="year", stepmode="backward"),
                        dict(count=10, label="10Y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(visible=True),
                type="date"
            )
        )
        
        return fig
    
    @render_widget
    def seasonal_analysis():
        """Create interactive seasonal analysis plot"""
        data = filtered_data()
        if data is None or input.dataset() == "COMPARISON":
            fig = go.Figure()
            fig.add_annotation(
                text="Select a dataset for seasonal analysis",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
            return fig
        
        data['month'] = data['date'].dt.month
        fig = go.Figure()
        
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                monthly_avg = data.groupby('month')[col_name].mean()
                monthly_std = data.groupby('month')[col_name].std()
                color = FRACTION_COLORS.get(fraction, '#1f77b4')
                label = CLASS_LABELS.get(fraction, fraction)
                
                # Main seasonal pattern
                fig.add_trace(go.Scatter(
                    x=monthly_avg.index,
                    y=monthly_avg.values,
                    mode='lines+markers',
                    name=label,
                    line=dict(color=color, width=3),
                    marker=dict(size=8),
                    hovertemplate=f'<b>{label}</b><br>' +
                                 'Month: %{x}<br>' +
                                 f'Mean {input.analysis_variable()}: %{{y:.4f}}<br>' +
                                 '<extra></extra>'
                ))
                
                # Add confidence intervals if requested
                if input.show_confidence():
                    # Convert color name to rgba format
                    if color.startswith('#'):
                        rgb = px.colors.hex_to_rgb(color)
                        fillcolor = f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.2)'
                    else:
                        # Use a simple fallback for named colors
                        fillcolor = f'{color}' if 'rgba' in color else f'rgba(100, 100, 200, 0.2)'
                    
                    fig.add_trace(go.Scatter(
                        x=list(monthly_avg.index) + list(monthly_avg.index[::-1]),
                        y=list(monthly_avg.values + monthly_std.values) + list((monthly_avg.values - monthly_std.values)[::-1]),
                        fill='toself',
                        fillcolor=fillcolor,
                        line=dict(color='rgba(255,255,255,0)'),
                        hoverinfo="skip",
                        showlegend=False,
                        name=f'{label} ±1σ'
                    ))
        
        fig.update_layout(
            title=dict(
                text="Interactive Seasonal Patterns",
                x=0.5,
                font=dict(size=16, family="Georgia, serif")
            ),
            xaxis=dict(
                title="Month",
                tickmode='array',
                tickvals=list(range(1, 13)),
                ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            ),
            yaxis=dict(
                title=f"{input.analysis_variable().title()} Albedo"
            ),
            height=400,
            template=input.plot_theme(),
            font=dict(family="Georgia, serif")
        )
        
        return fig
    
    @output
    @render.table
    def trend_statistics():
        """Generate interactive trend analysis table"""
        data = filtered_data()
        if data is None or input.dataset() == "COMPARISON":
            return pd.DataFrame()
        
        results = []
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                values = data[col_name].dropna()
                if len(values) > 2:
                    x_numeric = np.arange(len(values))
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, values)
                    
                    # Calculate annual trend (assuming daily data)
                    annual_trend = slope * 365.25
                    
                    results.append({
                        'Fraction Class': CLASS_LABELS.get(fraction, fraction),
                        'Annual Trend': f"{annual_trend:.6f}",
                        'R-squared': f"{r_value**2:.4f}",
                        'P-value': f"{p_value:.4f}",
                        'Significance': '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns',
                        'Observations': len(values)
                    })
        
        return pd.DataFrame(results)
    
    @render_widget
    def distribution_plot():
        """Create interactive distribution analysis"""
        data = filtered_data()
        if data is None or input.dataset() == "COMPARISON":
            return go.Figure().add_annotation(
                text="Select a dataset for distribution analysis",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        fig = go.Figure()
        
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                values = data[col_name].dropna()
                color = FRACTION_COLORS.get(fraction, '#1f77b4')
                label = CLASS_LABELS.get(fraction, fraction)
                
                fig.add_trace(go.Histogram(
                    x=values,
                    name=label,
                    opacity=0.7,
                    marker_color=color,
                    nbinsx=30,
                    hovertemplate=f'<b>{label}</b><br>' +
                                 'Range: %{x}<br>' +
                                 'Count: %{y}<br>' +
                                 '<extra></extra>'
                ))
        
        fig.update_layout(
            title="Interactive Distribution Analysis",
            xaxis_title=f"{input.analysis_variable().title()} Albedo",
            yaxis_title="Frequency",
            barmode='overlay',
            height=400,
            template=input.plot_theme(),
            font=dict(family="Georgia, serif")
        )
        
        return fig
    
    @render_widget
    def correlation_plot():
        """Create interactive correlation matrix"""
        data = filtered_data()
        if data is None or input.dataset() == "COMPARISON":
            return go.Figure().add_annotation(
                text="Select a dataset for correlation analysis",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        # Create correlation matrix for selected fractions
        correlation_data = []
        labels = []
        
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                correlation_data.append(data[col_name].dropna())
                labels.append(CLASS_LABELS.get(fraction, fraction))
        
        if len(correlation_data) < 2:
            return go.Figure().add_annotation(
                text="Select at least 2 fraction classes for correlation analysis",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        # Calculate correlation matrix
        correlation_df = pd.DataFrame(dict(zip(labels, correlation_data)))
        corr_matrix = correlation_df.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 3),
            texttemplate="%{text}",
            textfont={"size": 12},
            hovertemplate='%{y} vs %{x}<br>Correlation: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Interactive Correlation Matrix",
            height=400,
            template=input.plot_theme(),
            font=dict(family="Georgia, serif")
        )
        
        return fig
    
    @render_widget
    def monthly_climatology():
        """Create interactive monthly climatology"""
        data = filtered_data()
        if data is None or input.dataset() == "COMPARISON":
            return go.Figure().add_annotation(
                text="Select a dataset for climatology analysis",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        data['month'] = data['date'].dt.month
        data['year'] = data['date'].dt.year
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=['Monthly Box Plots', 'Monthly Time Series'],
            vertical_spacing=0.12
        )
        
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                color = FRACTION_COLORS.get(fraction, '#1f77b4')
                label = CLASS_LABELS.get(fraction, fraction)
                
                # Box plots by month
                for month in range(1, 13):
                    month_data = data[data['month'] == month][col_name].dropna()
                    if len(month_data) > 0:
                        fig.add_trace(
                            go.Box(
                                y=month_data,
                                name=label if month == 1 else "",
                                x=[month] * len(month_data),
                                marker_color=color,
                                showlegend=(month == 1),
                                legendgroup=label,
                                boxpoints='outliers'
                            ),
                            row=1, col=1
                        )
                
                # Monthly time series
                monthly_ts = data.groupby(['year', 'month'])[col_name].mean().reset_index()
                monthly_ts['date'] = pd.to_datetime(monthly_ts[['year', 'month']].assign(day=1))
                
                fig.add_trace(
                    go.Scatter(
                        x=monthly_ts['date'],
                        y=monthly_ts[col_name],
                        mode='lines+markers',
                        name=label,
                        line=dict(color=color),
                        showlegend=False,
                        legendgroup=label
                    ),
                    row=2, col=1
                )
        
        fig.update_layout(
            title="Interactive Monthly Climatology",
            height=600,
            template=input.plot_theme(),
            font=dict(family="Georgia, serif")
        )
        
        fig.update_xaxes(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            row=1, col=1
        )
        
        return fig
    
    # Comparison analysis and other interactive plots
    @render_widget
    def comparison_analysis():
        """Create interactive comparison analysis"""
        if input.dataset() != "COMPARISON":
            return go.Figure().add_annotation(
                text="Switch to 'Comparative Analysis' mode to view comparison",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        datasets = filtered_data()
        if not datasets or 'MCD43A3' not in datasets or 'MOD10A1' not in datasets:
            return go.Figure().add_annotation(
                text="Both MCD43A3 and MOD10A1 datasets required for comparison",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Scatter Comparison', 'Time Series Overlay',
                           'Difference Analysis', 'Correlation by Year'],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
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
                    color = FRACTION_COLORS.get(fraction, '#1f77b4')
                    label = CLASS_LABELS.get(fraction, fraction)
                    
                    correlation = merged['mcd43a3'].corr(merged['mod10a1'])
                    
                    # Scatter plot
                    fig.add_trace(go.Scatter(
                        x=merged['mcd43a3'],
                        y=merged['mod10a1'],
                        mode='markers',
                        name=f'{label} (r={correlation:.3f})',
                        marker=dict(color=color, size=5, opacity=0.6),
                        hovertemplate=f'<b>{label}</b><br>' +
                                     'MCD43A3: %{x:.4f}<br>' +
                                     'MOD10A1: %{y:.4f}<br>' +
                                     f'Correlation: {correlation:.3f}<br>' +
                                     '<extra></extra>'
                    ), row=1, col=1)
                    
                    # Time series overlay
                    fig.add_trace(go.Scatter(
                        x=merged['date'],
                        y=merged['mcd43a3'],
                        mode='lines',
                        name=f'{label} MCD43A3',
                        line=dict(color=color, width=2),
                        showlegend=False
                    ), row=1, col=2)
                    
                    fig.add_trace(go.Scatter(
                        x=merged['date'],
                        y=merged['mod10a1'],
                        mode='lines',
                        name=f'{label} MOD10A1',
                        line=dict(color=color, width=2, dash='dash'),
                        showlegend=False
                    ), row=1, col=2)
                    
                    # Difference analysis
                    difference = merged['mcd43a3'] - merged['mod10a1']
                    fig.add_trace(go.Scatter(
                        x=merged['date'],
                        y=difference,
                        mode='lines+markers',
                        name=f'{label} Diff',
                        line=dict(color=color, width=2),
                        marker=dict(size=3),
                        showlegend=False,
                        hovertemplate=f'<b>{label} Difference</b><br>' +
                                     'Date: %{x}<br>' +
                                     'MCD43A3 - MOD10A1: %{y:.4f}<br>' +
                                     '<extra></extra>'
                    ), row=2, col=1)
        
        # Add 1:1 line to scatter plot
        if len(merged) > 0:
            all_values = list(merged['mcd43a3']) + list(merged['mod10a1'])
            min_val, max_val = min(all_values), max(all_values)
            
            fig.add_trace(go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                name='1:1 Line',
                line=dict(color='red', dash='dash', width=2),
                showlegend=False
            ), row=1, col=1)
        
        # Add zero line to difference plot
        fig.add_hline(y=0, line_dash="dash", line_color="red", row=2, col=1)
        
        fig.update_layout(
            title="Interactive Multi-Dataset Comparison Analysis",
            height=700,
            template=input.plot_theme(),
            font=dict(family="Georgia, serif")
        )
        
        return fig
    
    @output
    @render.table
    def correlation_stats():
        """Generate correlation statistics table"""
        if input.dataset() != "COMPARISON":
            return pd.DataFrame()
        
        datasets = filtered_data()
        if not datasets or 'MCD43A3' not in datasets or 'MOD10A1' not in datasets:
            return pd.DataFrame()
        
        results = []
        mcd43a3_data = datasets['MCD43A3']
        mod10a1_data = datasets['MOD10A1']
        
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            
            if col_name in mcd43a3_data.columns and col_name in mod10a1_data.columns:
                merged = pd.merge(
                    mcd43a3_data[['date', col_name]].rename(columns={col_name: 'mcd43a3'}),
                    mod10a1_data[['date', col_name]].rename(columns={col_name: 'mod10a1'}),
                    on='date'
                )
                
                if len(merged) > 0:
                    correlation = merged['mcd43a3'].corr(merged['mod10a1'])
                    rmse = np.sqrt(((merged['mcd43a3'] - merged['mod10a1']) ** 2).mean())
                    bias = (merged['mcd43a3'] - merged['mod10a1']).mean()
                    
                    results.append({
                        'Fraction Class': CLASS_LABELS.get(fraction, fraction),
                        'Correlation': f"{correlation:.4f}",
                        'RMSE': f"{rmse:.4f}",
                        'Bias': f"{bias:.4f}",
                        'N Observations': len(merged)
                    })
        
        return pd.DataFrame(results)
    
    # Additional interactive widgets (simplified for space)
    @render_widget
    def difference_plot():
        return go.Figure().add_annotation(
            text="Difference analysis integrated in comparison view",
            xref="paper", yref="paper", x=0.5, y=0.5
        )
    
    @render_widget
    def coverage_plot():
        return go.Figure().add_annotation(
            text="Interactive coverage analysis coming soon",
            xref="paper", yref="paper", x=0.5, y=0.5
        )
    
    @render_widget
    def quality_timeline():
        return go.Figure().add_annotation(
            text="Interactive quality timeline coming soon",
            xref="paper", yref="paper", x=0.5, y=0.5
        )
    
    @output
    @render.table
    def quality_metrics():
        return pd.DataFrame()

# ==========================================
# APP CREATION
# ==========================================

app = App(app_ui, server)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)