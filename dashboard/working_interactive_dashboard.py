"""
Working Interactive Saskatchewan Glacier Albedo Analysis Dashboard
=================================================================

Version corrigée avec les couleurs et le chargement des données.
"""

from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    MCD43A3_CONFIG, MOD10A1_CONFIG,
    FRACTION_CLASSES, CLASS_LABELS
)

# Couleurs fixes en format hex pour éviter les erreurs
FIXED_COLORS = {
    'border': '#ff0000',          # red
    'mixed_low': '#ffa500',       # orange
    'mixed_high': '#ffd700',      # gold
    'mostly_ice': '#add8e6',      # lightblue
    'pure_ice': '#0000ff'         # blue
}

# ==========================================
# DATA LOADING
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
    ui.tags.head(ui.tags.style(academic_css)),
    
    # Academic header
    ui.div(
        ui.div("Saskatchewan Glacier Albedo Analysis", class_="academic-title"),
        ui.div("Interactive MODIS Data Dashboard (2010-2024)", class_="academic-subtitle"),
        ui.div("Zoom • Pan • Hover • Select", class_="academic-subtitle", 
               style="margin-top: 5px; font-size: 14px;"),
        class_="academic-header"
    ),
    
    # Main layout
    ui.layout_sidebar(
        ui.sidebar(
            ui.div(
                ui.div("📊 Dataset", class_="control-title"),
                ui.input_radio_buttons(
                    "dataset",
                    "",
                    choices={
                        "MCD43A3": "🛰️ MCD43A3 (General)",
                        "MOD10A1": "❄️ MOD10A1 (Snow)",
                        "COMPARISON": "📈 Comparison"
                    },
                    selected="MCD43A3"
                ),
                class_="sidebar-control"
            ),
            
            ui.div(
                ui.div("🎯 Parameters", class_="control-title"),
                ui.input_checkbox_group(
                    "fractions",
                    "Glacier Fractions:",
                    choices={k: v for k, v in CLASS_LABELS.items()},
                    selected=["pure_ice", "mostly_ice"]
                ),
                ui.input_select(
                    "analysis_variable",
                    "Variable:",
                    choices={"mean": "📊 Mean", "median": "📊 Median"},
                    selected="mean"
                ),
                class_="sidebar-control"
            ),
            
            ui.div(
                ui.div("📅 Time Filter", class_="control-title"),
                ui.input_date_range(
                    "date_range",
                    "Period:",
                    start="2010-01-01",
                    end="2024-12-31",
                    min="2010-01-01",
                    max="2024-12-31"
                ),
                ui.input_select(
                    "season_filter",
                    "Season:",
                    choices={
                        "all": "🌍 All",
                        "summer": "☀️ Summer",
                        "melt_season": "🌊 Melt Season"
                    },
                    selected="all"
                ),
                class_="sidebar-control"
            ),
            
            ui.div(
                ui.div("🔬 Options", class_="control-title"),
                ui.input_checkbox("show_trends", "📈 Trends", value=True),
                ui.input_checkbox("show_confidence", "📊 Confidence", value=False),
                class_="sidebar-control"
            ),
            
            ui.div(
                "💡 Interactive Controls",
                ui.br(),
                "• Zoom: Mouse wheel",
                ui.br(),
                "• Pan: Click & drag",
                ui.br(), 
                "• Hover: Rich tooltips",
                ui.br(),
                "• Reset: Double-click",
                class_="interactive-note"
            ),
            
            width=320
        ),
        
        # Main content
        ui.div(
            # Summary stats
            ui.div(
                ui.div("📊 Summary Statistics", class_="academic-section-title"),
                ui.output_ui("summary_statistics"),
                class_="academic-panel"
            ),
            
            # Tabs
            ui.navset_tab(
                ui.nav_panel(
                    "📈 Time Series",
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
                                ui.div("Seasonal Patterns", class_="academic-section-title"),
                                output_widget("seasonal_analysis"),
                                class_="academic-panel"
                            )
                        )
                    )
                ),
                
                ui.nav_panel(
                    "📊 Statistics",
                    ui.row(
                        ui.column(6,
                            ui.div(
                                ui.div("Distribution Analysis", class_="academic-section-title"),
                                output_widget("distribution_plot"),
                                class_="academic-panel"
                            )
                        ),
                        ui.column(6,
                            ui.div(
                                ui.div("Correlation Matrix", class_="academic-section-title"),
                                output_widget("correlation_plot"),
                                class_="academic-panel"
                            )
                        )
                    )
                ),
                
                ui.nav_panel(
                    "🔄 Comparison",
                    ui.div(
                        ui.div("Dataset Comparison", class_="academic-section-title"),
                        output_widget("comparison_analysis"),
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
        """Get filtered data"""
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
        
        return data
    
    @output
    @render.ui
    def summary_statistics():
        """Display summary statistics"""
        data = filtered_data()
        if data is None or input.dataset() == "COMPARISON":
            return ui.div("Select a dataset to view statistics")
        
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
            return go.Figure().add_annotation(
                text="Select a dataset for time series analysis",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=16)
            )
        
        fig = go.Figure()
        
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                color = FIXED_COLORS.get(fraction, '#1f77b4')
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
                    name=f'{label} ({len(plot_data)} points)',
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
        
        # Layout
        fig.update_layout(
            title=dict(
                text=f"Interactive Time Series - {input.dataset()}",
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
            template="plotly_white",
            font=dict(family="Georgia, serif")
        )
        
        # Add range selector
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
        """Create seasonal analysis plot"""
        data = filtered_data()
        if data is None or input.dataset() == "COMPARISON":
            return go.Figure().add_annotation(
                text="Select a dataset for seasonal analysis",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        data['month'] = data['date'].dt.month
        fig = go.Figure()
        
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                monthly_avg = data.groupby('month')[col_name].mean()
                color = FIXED_COLORS.get(fraction, '#1f77b4')
                label = CLASS_LABELS.get(fraction, fraction)
                
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
        
        fig.update_layout(
            title="Seasonal Patterns",
            xaxis=dict(
                title="Month",
                tickmode='array',
                tickvals=list(range(1, 13)),
                ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            ),
            yaxis=dict(title=f"{input.analysis_variable().title()} Albedo"),
            height=400,
            template="plotly_white",
            font=dict(family="Georgia, serif")
        )
        
        return fig
    
    @output
    @render.table
    def trend_statistics():
        """Generate trend analysis table"""
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
                    
                    results.append({
                        'Fraction': CLASS_LABELS.get(fraction, fraction),
                        'Slope': f"{slope:.6f}",
                        'R²': f"{r_value**2:.4f}",
                        'P-value': f"{p_value:.4f}",
                        'Significance': '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns',
                        'N': len(values)
                    })
        
        return pd.DataFrame(results)
    
    @render_widget
    def distribution_plot():
        """Create distribution analysis"""
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
                color = FIXED_COLORS.get(fraction, '#1f77b4')
                label = CLASS_LABELS.get(fraction, fraction)
                
                fig.add_trace(go.Histogram(
                    x=values,
                    name=label,
                    opacity=0.7,
                    marker_color=color,
                    nbinsx=30
                ))
        
        fig.update_layout(
            title="Distribution Analysis",
            xaxis_title=f"{input.analysis_variable().title()} Albedo",
            yaxis_title="Frequency",
            barmode='overlay',
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    @render_widget
    def correlation_plot():
        """Create correlation matrix"""
        data = filtered_data()
        if data is None or input.dataset() == "COMPARISON":
            return go.Figure().add_annotation(
                text="Select a dataset for correlation analysis",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        # Create correlation matrix
        correlation_data = []
        labels = []
        
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                correlation_data.append(data[col_name].dropna())
                labels.append(CLASS_LABELS.get(fraction, fraction))
        
        if len(correlation_data) < 2:
            return go.Figure().add_annotation(
                text="Select at least 2 fractions for correlation",
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
            textfont={"size": 12}
        ))
        
        fig.update_layout(
            title="Correlation Matrix",
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    @render_widget
    def comparison_analysis():
        """Create comparison analysis"""
        if input.dataset() != "COMPARISON":
            return go.Figure().add_annotation(
                text="Switch to 'Comparison' mode",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        datasets = filtered_data()
        if not datasets or 'MCD43A3' not in datasets or 'MOD10A1' not in datasets:
            return go.Figure().add_annotation(
                text="Both datasets required",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        fig = go.Figure()
        
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
                    color = FIXED_COLORS.get(fraction, '#1f77b4')
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
    app.run(host="127.0.0.1", port=8002)