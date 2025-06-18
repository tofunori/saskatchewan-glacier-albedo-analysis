"""
Saskatchewan Glacier Albedo Analysis - Academic Dashboard
========================================================

Professional academic-style dashboard for comprehensive albedo analysis.
Uses matplotlib for Shiny compatibility and academic publication standards.
"""

from shiny import App, ui, render, reactive
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
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

# Set academic plotting style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

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

.plot-panel {
    background: white;
    border: 2px solid #e8e9ea;
    border-radius: 12px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.nav-link {
    color: #1e3c72;
    font-weight: bold;
    font-family: 'Georgia', serif;
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
"""

# ==========================================
# UI DEFINITION
# ==========================================

app_ui = ui.page_fluid(
    # Academic CSS styling
    ui.tags.head(ui.tags.style(academic_css)),
    
    # Academic header
    ui.div(
        ui.div("Saskatchewan Glacier Albedo Analysis", class_="academic-title"),
        ui.div("Comprehensive MODIS Satellite Data Analysis (2010-2024)", class_="academic-subtitle"),
        ui.div("Interactive Research Dashboard for Glaciological Studies", class_="academic-subtitle", 
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
                ui.div("🔬 Analysis Options", class_="control-title"),
                ui.input_checkbox("show_trends", "📈 Display Trend Lines", value=True),
                ui.input_checkbox("show_confidence", "📊 Confidence Intervals", value=False),
                ui.input_checkbox("show_statistics", "📋 Statistical Annotations", value=True),
                ui.input_select(
                    "plot_style",
                    "Visualization Style:",
                    choices={
                        "academic": "🎓 Academic Publication",
                        "presentation": "📽️ Presentation Mode",
                        "detailed": "🔍 Detailed Analysis"
                    },
                    selected="academic"
                ),
                class_="sidebar-control"
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
                        ui.div("Time Series Analysis", class_="academic-section-title"),
                        ui.output_plot("timeseries_plot", height="500px"),
                        class_="plot-panel"
                    ),
                    ui.row(
                        ui.column(6,
                            ui.div(
                                ui.div("Trend Statistics", class_="academic-section-title"),
                                ui.output_table("trend_statistics"),
                                class_="plot-panel"
                            )
                        ),
                        ui.column(6,
                            ui.div(
                                ui.div("Temporal Patterns", class_="academic-section-title"),
                                ui.output_plot("seasonal_analysis", height="400px"),
                                class_="plot-panel"
                            )
                        )
                    )
                ),
                
                ui.nav_panel(
                    "📊 Statistical Analysis",
                    ui.row(
                        ui.column(6,
                            ui.div(
                                ui.div("Distribution Analysis", class_="academic-section-title"),
                                ui.output_plot("distribution_plot", height="400px"),
                                class_="plot-panel"
                            )
                        ),
                        ui.column(6,
                            ui.div(
                                ui.div("Correlation Matrix", class_="academic-section-title"),
                                ui.output_plot("correlation_plot", height="400px"),
                                class_="plot-panel"
                            )
                        )
                    ),
                    ui.div(
                        ui.div("Monthly Climatology", class_="academic-section-title"),
                        ui.output_plot("monthly_climatology", height="400px"),
                        class_="plot-panel"
                    )
                ),
                
                ui.nav_panel(
                    "🔄 Comparative Analysis",
                    ui.div(
                        ui.div("Multi-Dataset Comparison", class_="academic-section-title"),
                        ui.output_plot("comparison_analysis", height="500px"),
                        class_="plot-panel"
                    ),
                    ui.row(
                        ui.column(6,
                            ui.div(
                                ui.div("Correlation Analysis", class_="academic-section-title"),
                                ui.output_table("correlation_stats"),
                                class_="plot-panel"
                            )
                        ),
                        ui.column(6,
                            ui.div(
                                ui.div("Difference Analysis", class_="academic-section-title"),
                                ui.output_plot("difference_plot", height="400px"),
                                class_="plot-panel"
                            )
                        )
                    )
                ),
                
                ui.nav_panel(
                    "📋 Data Quality",
                    ui.row(
                        ui.column(6,
                            ui.div(
                                ui.div("Data Coverage Assessment", class_="academic-section-title"),
                                ui.output_plot("coverage_plot", height="400px"),
                                class_="plot-panel"
                            )
                        ),
                        ui.column(6,
                            ui.div(
                                ui.div("Quality Metrics", class_="academic-section-title"),
                                ui.output_table("quality_metrics"),
                                class_="plot-panel"
                            )
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
    
    @output
    @render.plot
    def timeseries_plot():
        """Create academic-style time series plot"""
        data = filtered_data()
        if data is None or input.dataset() == "COMPARISON":
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, 'Select a dataset to view time series analysis', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                color = FRACTION_COLORS.get(fraction, 'blue')
                label = CLASS_LABELS.get(fraction, fraction)
                
                # Plot time series
                ax.plot(data['date'], data[col_name], 
                       color=color, linewidth=2, alpha=0.8, label=label, marker='o', markersize=3)
                
                # Add trend line if requested
                if input.show_trends():
                    x_numeric = mdates.date2num(data['date'])
                    y_values = data[col_name].dropna()
                    x_clean = x_numeric[data[col_name].notna()]
                    
                    if len(y_values) > 1:
                        slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_values)
                        trend_line = slope * x_numeric + intercept
                        ax.plot(data['date'], trend_line, 
                               color=color, linestyle='--', linewidth=2, alpha=0.7)
                        
                        # Add statistics if requested
                        if input.show_statistics():
                            ax.text(0.02, 0.95 - 0.05 * list(input.fractions()).index(fraction), 
                                   f'{label}: slope={slope:.6f}, R²={r_value**2:.3f}, p={p_value:.3f}',
                                   transform=ax.transAxes, fontsize=10, 
                                   bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.2))
        
        # Academic styling
        ax.set_xlabel('Date', fontsize=14, fontweight='bold')
        ax.set_ylabel(f'{input.analysis_variable().title()} Albedo', fontsize=14, fontweight='bold')
        ax.set_title(f'Temporal Analysis - {input.dataset()} Dataset\n{input.season_filter().replace("_", " ").title()} Season', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.3)
        
        # Format dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
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
                        'Fraction Class': CLASS_LABELS.get(fraction, fraction),
                        'Slope (per year)': f"{slope * 365.25:.6f}",
                        'R-squared': f"{r_value**2:.4f}",
                        'P-value': f"{p_value:.4f}",
                        'Significance': '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns'
                    })
        
        return pd.DataFrame(results)
    
    @output
    @render.plot
    def seasonal_analysis():
        """Create seasonal analysis plot"""
        data = filtered_data()
        if data is None or input.dataset() == "COMPARISON":
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, 'Select a dataset for seasonal analysis', 
                   ha='center', va='center', transform=ax.transAxes)
            return fig
        
        data['month'] = data['date'].dt.month
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                monthly_avg = data.groupby('month')[col_name].mean()
                color = FRACTION_COLORS.get(fraction, 'blue')
                label = CLASS_LABELS.get(fraction, fraction)
                
                ax.plot(monthly_avg.index, monthly_avg.values, 
                       color=color, marker='o', linewidth=3, markersize=8, label=label)
        
        ax.set_xlabel('Month', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'{input.analysis_variable().title()} Albedo', fontsize=12, fontweight='bold')
        ax.set_title('Seasonal Patterns', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        
        plt.tight_layout()
        return fig
    
    @output
    @render.plot
    def distribution_plot():
        """Create distribution analysis plot"""
        data = filtered_data()
        if data is None or input.dataset() == "COMPARISON":
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, 'Select a dataset for distribution analysis', 
                   ha='center', va='center', transform=ax.transAxes)
            return fig
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                values = data[col_name].dropna()
                color = FRACTION_COLORS.get(fraction, 'blue')
                label = CLASS_LABELS.get(fraction, fraction)
                
                ax.hist(values, bins=30, alpha=0.6, color=color, label=label, density=True)
        
        ax.set_xlabel(f'{input.analysis_variable().title()} Albedo', fontsize=12, fontweight='bold')
        ax.set_ylabel('Density', fontsize=12, fontweight='bold')
        ax.set_title('Distribution Analysis', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    # Placeholder implementations for other plots
    @output
    @render.plot
    def correlation_plot():
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'Correlation analysis coming soon', 
               ha='center', va='center', transform=ax.transAxes)
        return fig
    
    @output
    @render.plot
    def monthly_climatology():
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, 'Monthly climatology analysis coming soon', 
               ha='center', va='center', transform=ax.transAxes)
        return fig
    
    @output
    @render.plot
    def comparison_analysis():
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, 'Comparative analysis coming soon', 
               ha='center', va='center', transform=ax.transAxes)
        return fig
    
    @output
    @render.plot
    def difference_plot():
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'Difference analysis coming soon', 
               ha='center', va='center', transform=ax.transAxes)
        return fig
    
    @output
    @render.plot
    def coverage_plot():
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'Coverage analysis coming soon', 
               ha='center', va='center', transform=ax.transAxes)
        return fig
    
    @output
    @render.table
    def correlation_stats():
        return pd.DataFrame()
    
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