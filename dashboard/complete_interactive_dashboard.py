"""
Complete Interactive Saskatchewan Glacier Albedo Dashboard
=========================================================

Final version incorporating all fixes and improvements.
This dashboard provides interactive analysis of MODIS albedo data with:
- Zoom, pan, hover functionality
- Time series visualization
- Statistical analysis
- Comparison capabilities
"""

from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import sys, os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import MCD43A3_CONFIG, MOD10A1_CONFIG, CLASS_LABELS

# Fixed colors in hex format to avoid conversion issues
COLORS = {
    'border': '#FF4444',
    'mixed_low': '#FF8800', 
    'mixed_high': '#FFDD00',
    'mostly_ice': '#4488FF',
    'pure_ice': '#0066CC'
}

# Academic CSS styling
academic_css = """
.header {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: white;
    padding: 25px;
    margin: -15px -15px 25px -15px;
    border-radius: 0 0 15px 15px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}

.panel {
    background: white;
    border: 2px solid #e8e9ea;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.sidebar-panel {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 18px;
}

.metric {
    display: inline-block;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 15px;
    margin: 8px;
    text-align: center;
    min-width: 140px;
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

.metric-sub {
    font-size: 12px;
    color: #6c757d;
    margin: 0;
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
    padding: 12px;
    margin: 15px 0;
    font-size: 12px;
    color: #1565c0;
    text-align: center;
}
"""

# UI Definition
app_ui = ui.page_fluid(
    ui.tags.head(ui.tags.style(academic_css)),
    
    # Header
    ui.div(
        ui.h1("🏔️ Saskatchewan Glacier Albedo Analysis"),
        ui.p("Interactive MODIS Data Dashboard • 15 Years (2010-2024)"),
        ui.p("🔍 Zoom • 🖱️ Pan • 💬 Hover • 📊 Select • 📅 Range Navigation"),
        class_="header"
    ),
    
    ui.layout_sidebar(
        ui.sidebar(
            ui.div(
                ui.div("📊 Dataset", class_="control-title"),
                ui.input_radio_buttons(
                    "dataset",
                    "",
                    choices={
                        "MCD43A3": "🛰️ MCD43A3 (General Albedo)",
                        "MOD10A1": "❄️ MOD10A1 (Snow Albedo)",
                        "COMPARISON": "📈 Compare Both"
                    },
                    selected="MOD10A1"
                ),
                class_="sidebar-panel"
            ),
            
            ui.div(
                ui.div("🎯 Glacier Fractions", class_="control-title"),
                ui.input_checkbox_group(
                    "fractions",
                    "",
                    choices={k: v for k, v in CLASS_LABELS.items()},
                    selected=["mostly_ice", "pure_ice"]
                ),
                class_="sidebar-panel"
            ),
            
            ui.div(
                ui.div("📊 Analysis Variable", class_="control-title"),
                ui.input_select(
                    "variable",
                    "",
                    choices={"mean": "Mean Albedo", "median": "Median Albedo"},
                    selected="mean"
                ),
                class_="sidebar-panel"
            ),
            
            ui.div(
                ui.div("📅 Time Period", class_="control-title"),
                ui.input_date_range(
                    "date_range",
                    "Period:",
                    start="2010-01-01",
                    end="2024-12-31",
                    min="2010-01-01",
                    max="2024-12-31"
                ),
                ui.input_select(
                    "season",
                    "Season:",
                    choices={
                        "all": "All Seasons",
                        "summer": "Summer (JJA)", 
                        "melt_season": "Melt Season (May-Sep)"
                    },
                    selected="all"
                ),
                class_="sidebar-panel"
            ),
            
            ui.div(
                ui.div("🔬 Display Options", class_="control-title"),
                ui.input_checkbox("trends", "Show Trend Lines", True),
                ui.input_checkbox("points", "Show Data Points", True),
                ui.input_checkbox("stats", "Show Statistics", True),
                class_="sidebar-panel"
            ),
            
            ui.div(
                "💡 Interactive Features",
                ui.br(),
                "• Zoom: Mouse wheel or box select",
                ui.br(),
                "• Pan: Click and drag",
                ui.br(), 
                "• Hover: Detailed data tooltips",
                ui.br(),
                "• Reset: Double-click chart",
                ui.br(),
                "• Range: Use slider below chart",
                class_="interactive-note"
            ),
            
            width=320
        ),
        
        # Main content
        ui.div(
            # Data status and summary
            ui.div(
                ui.h3("📊 Data Summary"),
                ui.output_ui("data_summary"),
                class_="panel"
            ),
            
            # Tabs for different analyses
            ui.navset_tab(
                ui.nav_panel(
                    "📈 Time Series",
                    ui.div(
                        ui.h4("Interactive Time Series Analysis"),
                        output_widget("main_timeseries"),
                        class_="panel"
                    ),
                    ui.row(
                        ui.column(6,
                            ui.div(
                                ui.h4("📊 Trend Statistics"),
                                ui.output_table("trend_table"),
                                class_="panel"
                            )
                        ),
                        ui.column(6,
                            ui.div(
                                ui.h4("📅 Seasonal Patterns"),
                                output_widget("seasonal_plot"),
                                class_="panel"
                            )
                        )
                    )
                ),
                
                ui.nav_panel(
                    "📊 Statistical Analysis",
                    ui.row(
                        ui.column(6,
                            ui.div(
                                ui.h4("📈 Distributions"),
                                output_widget("distribution_plot"),
                                class_="panel"
                            )
                        ),
                        ui.column(6,
                            ui.div(
                                ui.h4("🔗 Correlations"),
                                output_widget("correlation_plot"),
                                class_="panel"
                            )
                        )
                    )
                ),
                
                ui.nav_panel(
                    "🔄 Dataset Comparison", 
                    ui.div(
                        ui.h4("MCD43A3 vs MOD10A1 Comparison"),
                        output_widget("comparison_plot"),
                        class_="panel"
                    )
                )
            )
        )
    )
)

def server(input, output, session):
    
    @reactive.Calc
    def load_data():
        """Load and prepare data based on selected dataset"""
        dataset = input.dataset()
        
        try:
            if dataset == "COMPARISON":
                # Load both datasets for comparison
                data = {}
                try:
                    mcd = pd.read_csv(MCD43A3_CONFIG['csv_path'])
                    mcd['date'] = pd.to_datetime(mcd['date'])
                    data['MCD43A3'] = mcd
                    print(f"✅ Loaded MCD43A3: {len(mcd)} rows")
                except Exception as e:
                    print(f"❌ Error loading MCD43A3: {e}")
                    data['MCD43A3'] = None
                    
                try:
                    mod = pd.read_csv(MOD10A1_CONFIG['csv_path'])
                    mod['date'] = pd.to_datetime(mod['date'])
                    data['MOD10A1'] = mod
                    print(f"✅ Loaded MOD10A1: {len(mod)} rows")
                except Exception as e:
                    print(f"❌ Error loading MOD10A1: {e}")
                    data['MOD10A1'] = None
                    
                return data
            else:
                # Load single dataset
                if dataset == "MCD43A3":
                    data = pd.read_csv(MCD43A3_CONFIG['csv_path'])
                else:
                    data = pd.read_csv(MOD10A1_CONFIG['csv_path'])
                
                data['date'] = pd.to_datetime(data['date'])
                print(f"✅ Loaded {dataset}: {len(data)} rows")
                return data
                
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return None
    
    @reactive.Calc
    def filtered_data():
        """Apply filters to the loaded data"""
        data = load_data()
        
        if data is None:
            return None
            
        if input.dataset() == "COMPARISON":
            return data  # Return dict for comparison mode
            
        # Apply date filter
        start_date = pd.to_datetime(input.date_range()[0])
        end_date = pd.to_datetime(input.date_range()[1])
        mask = (data['date'] >= start_date) & (data['date'] <= end_date)
        filtered = data[mask].copy()
        
        # Apply seasonal filter
        if input.season() != "all":
            filtered['month'] = filtered['date'].dt.month
            if input.season() == "summer":
                filtered = filtered[filtered['month'].isin([6, 7, 8])]
            elif input.season() == "melt_season":
                filtered = filtered[filtered['month'].isin([5, 6, 7, 8, 9])]
        
        return filtered
    
    @output
    @render.ui
    def data_summary():
        """Display data summary and status"""
        data = filtered_data()
        
        if data is None or input.dataset() == "COMPARISON":
            return ui.div("Select a dataset to view summary statistics")
        
        metrics = []
        total_points = 0
        
        for fraction in input.fractions():
            col = f"{fraction}_{input.variable()}"
            if col in data.columns:
                values = data[col].dropna()
                if len(values) > 0:
                    total_points += len(values)
                    metrics.append(
                        ui.div(
                            ui.div(CLASS_LABELS.get(fraction, fraction), class_="metric-title"),
                            ui.div(f"{values.mean():.4f}", class_="metric-value"),
                            ui.div(f"σ={values.std():.4f}", class_="metric-sub"),
                            ui.div(f"n={len(values):,} points", class_="metric-sub"),
                            class_="metric"
                        )
                    )
        
        # Add total summary
        metrics.insert(0,
            ui.div(
                ui.div("Total Data Points", class_="metric-title"),
                ui.div(f"{total_points:,}", class_="metric-value"),
                ui.div(f"{input.dataset()}", class_="metric-sub"),
                ui.div(f"{len(input.fractions())} fractions", class_="metric-sub"),
                class_="metric"
            )
        )
        
        return ui.div(*metrics, style="text-align: center;") if metrics else ui.div("No data available")
    
    @render_widget
    def main_timeseries():
        """Create the main interactive time series plot"""
        data = filtered_data()
        
        if data is None or input.dataset() == "COMPARISON":
            return go.Figure().add_annotation(
                text="Select MCD43A3 or MOD10A1 for time series analysis",
                xref="paper", yref="paper", x=0.5, y=0.5,
                font=dict(size=16, color="orange")
            )
        
        fig = go.Figure()
        total_points = 0
        
        # Add each selected fraction
        for fraction in input.fractions():
            col = f"{fraction}_{input.variable()}"
            if col in data.columns:
                # Filter non-null values
                mask = data[col].notna()
                plot_data = data[mask].copy()
                
                if len(plot_data) == 0:
                    continue
                
                total_points += len(plot_data)
                color = COLORS.get(fraction, '#666666')
                name = CLASS_LABELS.get(fraction, fraction)
                
                print(f"📊 Adding {fraction}: {len(plot_data)} points")
                
                # Determine display mode
                mode = 'lines+markers' if input.points() else 'lines'
                marker_size = 4 if input.points() else 0
                
                # Main time series trace
                fig.add_trace(go.Scatter(
                    x=plot_data['date'],
                    y=plot_data[col],
                    mode=mode,
                    name=f'{name} ({len(plot_data)} pts)',
                    line=dict(color=color, width=2.5),
                    marker=dict(size=marker_size, opacity=0.8, color=color),
                    visible=True,  # Explicitly force visibility
                    hovertemplate=f'<b>{name}</b><br>' +
                                 'Date: %{x}<br>' +
                                 f'{input.variable().title()}: %{{y:.4f}}<br>' +
                                 '<extra></extra>'
                ))
                
                # Add trend line if requested
                if input.trends() and len(plot_data) > 10:
                    try:
                        # Calculate trend using numeric dates
                        x_num = (plot_data['date'] - plot_data['date'].min()).dt.days
                        slope, intercept, r_val, p_val, std_err = stats.linregress(x_num, plot_data[col])
                        trend_y = slope * x_num + intercept
                        
                        fig.add_trace(go.Scatter(
                            x=plot_data['date'],
                            y=trend_y,
                            mode='lines',
                            name=f'{name} Trend (R²={r_val**2:.3f})',
                            line=dict(color=color, width=2, dash='dash'),
                            visible=True,  # Explicitly force visibility
                            showlegend=True,
                            hovertemplate=f'<b>{name} Trend</b><br>' +
                                         f'Slope: {slope:.6f}/day<br>' +
                                         f'R²: {r_val**2:.3f}<br>' +
                                         f'p-value: {p_val:.4f}<br>' +
                                         '<extra></extra>'
                        ))
                        print(f"📈 Added trend line for {fraction}")
                    except Exception as e:
                        print(f"⚠️ Could not calculate trend for {fraction}: {e}")
        
        print(f"📊 FINAL TOTAL: {total_points} points in {len(fig.data)} traces")
        
        # Handle empty data case
        if total_points == 0:
            fig.add_annotation(
                text="⚠️ No data to display\\nCheck your fraction selection and date range",
                xref="paper", yref="paper", x=0.5, y=0.5,
                font=dict(size=16, color="orange")
            )
            return fig
        
        # Configure layout with all interactive features
        fig.update_layout(
            title=dict(
                text=f"Interactive Time Series - {input.dataset()} ({total_points:,} data points)",
                x=0.5,
                font=dict(size=18, color="#1e3c72")
            ),
            xaxis=dict(
                title="Date",
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)',
                type="date",
                # Enable range selector
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(count=5, label="5Y", step="year", stepmode="backward"),
                        dict(count=10, label="10Y", step="year", stepmode="backward"),
                        dict(step="all")
                    ]),
                    font=dict(size=10),
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                ),
                # Enable range slider
                rangeslider=dict(
                    visible=True,
                    thickness=0.05
                )
            ),
            yaxis=dict(
                title=f"{input.variable().title()} Albedo",
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            hovermode='x unified',
            height=650,
            template="plotly_white",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            # Enable all interactive features
            dragmode='zoom'  # Default to zoom mode
        )
        
        return fig
    
    @render_widget
    def seasonal_plot():
        """Create seasonal analysis plot"""
        data = filtered_data()
        
        if data is None or input.dataset() == "COMPARISON":
            return go.Figure().add_annotation(
                text="Select a dataset for seasonal analysis",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        # Calculate monthly averages
        data['month'] = data['date'].dt.month
        fig = go.Figure()
        
        for fraction in input.fractions():
            col = f"{fraction}_{input.variable()}"
            if col in data.columns:
                monthly_avg = data.groupby('month')[col].mean()
                color = COLORS.get(fraction, '#666666')
                name = CLASS_LABELS.get(fraction, fraction)
                
                fig.add_trace(go.Scatter(
                    x=monthly_avg.index,
                    y=monthly_avg.values,
                    mode='lines+markers',
                    name=name,
                    line=dict(color=color, width=3),
                    marker=dict(size=8),
                    hovertemplate=f'<b>{name}</b><br>' +
                                 'Month: %{x}<br>' +
                                 f'Mean {input.variable()}: %{{y:.4f}}<br>' +
                                 '<extra></extra>'
                ))
        
        fig.update_layout(
            title="Seasonal Patterns (Monthly Averages)",
            xaxis=dict(
                title="Month",
                tickmode='array',
                tickvals=list(range(1, 13)),
                ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            ),
            yaxis=dict(title=f"{input.variable().title()} Albedo"),
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    @output
    @render.table
    def trend_table():
        """Generate trend analysis table"""
        data = filtered_data()
        
        if data is None or input.dataset() == "COMPARISON":
            return pd.DataFrame()
        
        results = []
        for fraction in input.fractions():
            col = f"{fraction}_{input.variable()}"
            if col in data.columns:
                values = data[col].dropna()
                if len(values) > 2:
                    x = np.arange(len(values))
                    slope, intercept, r_val, p_val, std_err = stats.linregress(x, values)
                    
                    results.append({
                        'Fraction': CLASS_LABELS.get(fraction, fraction),
                        'Slope': f"{slope:.6f}",
                        'R²': f"{r_val**2:.4f}",
                        'P-value': f"{p_val:.4f}",
                        'Significance': '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else 'ns',
                        'Data Points': len(values)
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
            col = f"{fraction}_{input.variable()}"
            if col in data.columns:
                values = data[col].dropna()
                color = COLORS.get(fraction, '#666666')
                name = CLASS_LABELS.get(fraction, fraction)
                
                fig.add_trace(go.Histogram(
                    x=values,
                    name=name,
                    opacity=0.7,
                    marker_color=color,
                    nbinsx=30
                ))
        
        fig.update_layout(
            title="Distribution Analysis",
            xaxis_title=f"{input.variable().title()} Albedo",
            yaxis_title="Frequency",
            barmode='overlay',
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    @render_widget
    def correlation_plot():
        """Create correlation matrix heatmap"""
        data = filtered_data()
        
        if data is None or input.dataset() == "COMPARISON":
            return go.Figure().add_annotation(
                text="Select a dataset for correlation analysis",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        # Build correlation matrix
        corr_data = []
        labels = []
        
        for fraction in input.fractions():
            col = f"{fraction}_{input.variable()}"
            if col in data.columns:
                corr_data.append(data[col].dropna())
                labels.append(CLASS_LABELS.get(fraction, fraction))
        
        if len(corr_data) < 2:
            return go.Figure().add_annotation(
                text="Select at least 2 fractions for correlation analysis",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        # Calculate correlation matrix
        df_corr = pd.DataFrame(dict(zip(labels, corr_data)))
        corr_matrix = df_corr.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 3),
            texttemplate="%{text}",
            textfont={"size": 12},
            hovertemplate='<b>%{y} vs %{x}</b><br>Correlation: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Correlation Matrix",
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    @render_widget
    def comparison_plot():
        """Create dataset comparison scatter plot"""
        if input.dataset() != "COMPARISON":
            return go.Figure().add_annotation(
                text="Switch to 'Compare Both' mode for dataset comparison",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        data = filtered_data()
        if not data or 'MCD43A3' not in data or 'MOD10A1' not in data:
            return go.Figure().add_annotation(
                text="Both datasets required for comparison",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        fig = go.Figure()
        
        mcd = data['MCD43A3']
        mod = data['MOD10A1']
        
        for fraction in input.fractions():
            col = f"{fraction}_{input.variable()}"
            
            if col in mcd.columns and col in mod.columns:
                # Merge datasets on date
                merged = pd.merge(
                    mcd[['date', col]].rename(columns={col: 'mcd'}),
                    mod[['date', col]].rename(columns={col: 'mod'}),
                    on='date'
                )
                
                if len(merged) > 0:
                    color = COLORS.get(fraction, '#666666')
                    name = CLASS_LABELS.get(fraction, fraction)
                    corr = merged['mcd'].corr(merged['mod'])
                    
                    fig.add_trace(go.Scatter(
                        x=merged['mcd'],
                        y=merged['mod'],
                        mode='markers',
                        name=f'{name} (r={corr:.3f}, n={len(merged)})',
                        marker=dict(color=color, size=5, opacity=0.7),
                        hovertemplate=f'<b>{name}</b><br>' +
                                     'MCD43A3: %{x:.4f}<br>' +
                                     'MOD10A1: %{y:.4f}<br>' +
                                     f'Correlation: {corr:.3f}<br>' +
                                     '<extra></extra>'
                    ))
        
        # Add 1:1 reference line
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
                name='1:1 Reference Line',
                line=dict(color='red', dash='dash', width=2),
                hovertemplate='Perfect Agreement Line<extra></extra>'
            ))
        
        fig.update_layout(
            title="Dataset Comparison: MCD43A3 vs MOD10A1",
            xaxis_title="MCD43A3 Albedo",
            yaxis_title="MOD10A1 Albedo",
            height=500,
            template="plotly_white",
            # Ensure equal aspect ratio for comparison
            xaxis=dict(scaleanchor="y", scaleratio=1)
        )
        
        return fig

# Create the Shiny app
app = App(app_ui, server)

if __name__ == "__main__":
    print("🚀 Launching Complete Interactive Saskatchewan Glacier Dashboard...")
    print("📊 Features: Interactive time series, statistical analysis, dataset comparison")
    print("🔗 URL: http://127.0.0.1:8001")
    app.run(host="127.0.0.1", port=8001)