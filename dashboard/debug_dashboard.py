"""
Debug version of the Interactive Academic Dashboard
=================================================

This version includes debug information to help identify data loading issues.
"""

from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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
# DATA LOADING WITH DEBUG
# ==========================================

def load_csv_with_debug(csv_path, dataset_name):
    """Load CSV data with debug information"""
    try:
        if os.path.exists(csv_path):
            print(f"📁 Loading {dataset_name} from: {csv_path}")
            data = pd.read_csv(csv_path)
            print(f"📊 Loaded {len(data)} rows for {dataset_name}")
            print(f"📋 Columns: {list(data.columns)}")
            
            if 'date' in data.columns:
                data['date'] = pd.to_datetime(data['date'])
                print(f"📅 Date range: {data['date'].min()} to {data['date'].max()}")
            
            # Check for data in fraction columns
            for fraction in FRACTION_CLASSES:
                col_mean = f"{fraction}_mean"
                col_median = f"{fraction}_median"
                if col_mean in data.columns:
                    non_null_count = data[col_mean].notna().sum()
                    print(f"   {fraction}_mean: {non_null_count} non-null values")
                    if non_null_count > 0:
                        print(f"     Range: {data[col_mean].min():.4f} to {data[col_mean].max():.4f}")
            
            return data
        else:
            print(f"❌ File not found: {csv_path}")
            return None
    except Exception as e:
        print(f"❌ Error loading {dataset_name}: {e}")
        return None

@reactive.Calc
def load_datasets():
    """Load available datasets with debug info"""
    print("🔄 Loading datasets...")
    datasets = {}
    
    # Load MCD43A3
    mcd43a3_data = load_csv_with_debug(MCD43A3_CONFIG['csv_path'], 'MCD43A3')
    if mcd43a3_data is not None:
        datasets['MCD43A3'] = mcd43a3_data
    
    # Load MOD10A1
    mod10a1_data = load_csv_with_debug(MOD10A1_CONFIG['csv_path'], 'MOD10A1')
    if mod10a1_data is not None:
        datasets['MOD10A1'] = mod10a1_data
    
    print(f"✅ Loaded {len(datasets)} datasets")
    return datasets

# ==========================================
# SIMPLIFIED UI FOR DEBUGGING
# ==========================================

app_ui = ui.page_fluid(
    ui.h1("🔍 Debug Dashboard - Saskatchewan Glacier Analysis"),
    ui.p("Cette version affiche des informations de debug pour identifier les problèmes de données."),
    
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_radio_buttons(
                "dataset",
                "Dataset:",
                choices={
                    "MCD43A3": "MCD43A3",
                    "MOD10A1": "MOD10A1"
                },
                selected="MCD43A3"
            ),
            
            ui.input_checkbox_group(
                "fractions",
                "Fractions:",
                choices={k: v for k, v in CLASS_LABELS.items()},
                selected=["pure_ice", "mostly_ice"]
            ),
            
            ui.input_select(
                "analysis_variable",
                "Variable:",
                choices={"mean": "Mean", "median": "Median"},
                selected="mean"
            ),
            
            width=300
        ),
        
        ui.div(
            ui.h3("📊 Debug Information"),
            ui.output_text_verbatim("debug_info"),
            
            ui.h3("📈 Sample Data"),
            ui.output_table("sample_data"),
            
            ui.h3("📉 Interactive Plot"),
            output_widget("debug_plot"),
            
            ui.h3("📋 Summary Stats"),
            ui.output_ui("summary_stats")
        )
    )
)

# ==========================================
# SERVER LOGIC WITH DEBUG
# ==========================================

def server(input, output, session):
    
    @reactive.Calc
    def filtered_data():
        """Get filtered data with debug"""
        datasets = load_datasets()
        dataset_name = input.dataset()
        
        if dataset_name not in datasets:
            print(f"❌ Dataset {dataset_name} not found")
            return None
            
        data = datasets[dataset_name].copy()
        print(f"🔄 Filtering {dataset_name}: {len(data)} rows")
        
        return data
    
    @output
    @render.text
    def debug_info():
        """Display debug information"""
        data = filtered_data()
        if data is None:
            return "❌ No data loaded"
        
        info = []
        info.append(f"Dataset: {input.dataset()}")
        info.append(f"Total rows: {len(data):,}")
        info.append(f"Date range: {data['date'].min()} to {data['date'].max()}")
        info.append(f"Selected fractions: {', '.join(input.fractions())}")
        info.append(f"Variable: {input.analysis_variable()}")
        
        info.append("\n📊 Data availability by fraction:")
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                non_null = data[col_name].notna().sum()
                info.append(f"  {fraction}: {non_null:,} values")
                if non_null > 0:
                    info.append(f"    Range: {data[col_name].min():.4f} - {data[col_name].max():.4f}")
                    info.append(f"    Mean: {data[col_name].mean():.4f}")
            else:
                info.append(f"  {fraction}: ❌ Column not found")
        
        return "\n".join(info)
    
    @output
    @render.table
    def sample_data():
        """Display sample of the data"""
        data = filtered_data()
        if data is None:
            return pd.DataFrame()
        
        # Show relevant columns only
        cols_to_show = ['date']
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                cols_to_show.append(col_name)
        
        return data[cols_to_show].head(10)
    
    @render_widget
    def debug_plot():
        """Create debug plot"""
        data = filtered_data()
        if data is None:
            return go.Figure().add_annotation(
                text="❌ No data to plot",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        fig = go.Figure()
        
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                # Filter non-null data
                mask = data[col_name].notna()
                plot_data = data[mask]
                
                if len(plot_data) > 0:
                    color = FRACTION_COLORS.get(fraction, 'blue')
                    label = CLASS_LABELS.get(fraction, fraction)
                    
                    fig.add_trace(go.Scatter(
                        x=plot_data['date'],
                        y=plot_data[col_name],
                        mode='lines+markers',
                        name=f'{label} ({len(plot_data)} points)',
                        line=dict(color=color, width=2),
                        marker=dict(size=4)
                    ))
                else:
                    print(f"⚠️ No data points for {fraction}")
        
        fig.update_layout(
            title=f"Debug Plot - {input.dataset()}",
            xaxis_title="Date",
            yaxis_title=f"{input.analysis_variable().title()} Albedo",
            height=500
        )
        
        if len(fig.data) == 0:
            fig.add_annotation(
                text="⚠️ No data points to display\nCheck date filters and fraction selection",
                xref="paper", yref="paper", x=0.5, y=0.5
            )
        
        return fig
    
    @output
    @render.ui
    def summary_stats():
        """Summary statistics"""
        data = filtered_data()
        if data is None:
            return ui.div("❌ No data")
        
        stats = []
        for fraction in input.fractions():
            col_name = f"{fraction}_{input.analysis_variable()}"
            if col_name in data.columns:
                values = data[col_name].dropna()
                if len(values) > 0:
                    stats.append(
                        ui.div(
                            ui.h5(CLASS_LABELS.get(fraction, fraction)),
                            ui.p(f"Count: {len(values):,}"),
                            ui.p(f"Mean: {values.mean():.4f}"),
                            ui.p(f"Std: {values.std():.4f}"),
                            ui.p(f"Min: {values.min():.4f}"),
                            ui.p(f"Max: {values.max():.4f}"),
                            style="border: 1px solid #ccc; padding: 10px; margin: 5px; border-radius: 5px;"
                        )
                    )
        
        return ui.div(*stats) if stats else ui.div("❌ No valid data found")

# ==========================================
# APP CREATION
# ==========================================

app = App(app_ui, server)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001)  # Different port to avoid conflict