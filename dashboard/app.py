"""
Saskatchewan Glacier Albedo Analysis Dashboard
=============================================

Simple Shiny dashboard for interactive exploration of albedo data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shiny import App, render, ui, reactive
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Global variable to store data (loaded on demand)
global_data = None

def load_dashboard_data():
    """Load data with proper error handling for dashboard use"""
    global global_data
    
    if global_data is not None:
        return global_data
    
    try:
        # Import here to avoid circular imports
        from data.handler import AlbedoDataHandler
        from config import MCD43A3_CONFIG
        
        # Load data with correct path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(project_root, MCD43A3_CONFIG['csv_path'])
        
        print(f"Loading data from: {csv_path}")
        
        # Simple CSV loading for dashboard (avoid complex aggregations)
        df = pd.read_csv(csv_path)
        
        # Basic data preparation
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Convert numeric columns and handle mixed types
        for col in df.columns:
            if col.endswith('_mean') or col.endswith('_median'):
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with invalid dates
        df = df.dropna(subset=['date'])
        
        print(f"✓ Data loaded successfully: {len(df)} rows, {len(df.columns)} columns")
        global_data = df
        return df
        
    except Exception as e:
        print(f"Error loading data: {e}")
        # Return empty dataframe with expected structure
        return pd.DataFrame({
            'date': pd.to_datetime([]),
            'pure_ice_mean': [],
            'mostly_ice_mean': [],
            'mixed_high_mean': [],
            'mixed_low_mean': [],
            'border_mean': []
        })

# Load configuration
try:
    from config import FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS
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

# Try to get config info safely
try:
    from config import MCD43A3_CONFIG
    dataset_info = f"Dataset: {MCD43A3_CONFIG['name']} ({MCD43A3_CONFIG['description']})"
except:
    dataset_info = "Dataset: MCD43A3 (MODIS Combined Albedo)"

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Controls"),
        ui.input_selectize(
            "fraction_class",
            "Select Fraction Class:",
            choices={fc: CLASS_LABELS[fc] for fc in FRACTION_CLASSES},
            selected="pure_ice"
        ),
        ui.p(dataset_info),
        ui.p("Period: 2010-2024"),
        width=300
    ),
    ui.h1("Saskatchewan Glacier Albedo Analysis Dashboard"),
    ui.p("Interactive exploration of MODIS albedo data (2010-2024)"),
    ui.h3("Time Series - Mean Albedo"),
    ui.output_ui("timeseries_plot"),
    ui.h4("Data Summary"),
    ui.output_table("data_summary"),
    title="Saskatchewan Glacier Albedo Dashboard"
)

def server(input, output, session):
    
    @reactive.calc
    def filtered_data():
        """Filter data based on selected fraction class"""
        try:
            df = load_dashboard_data()
            return df
        except Exception as e:
            print(f"Error in filtered_data: {e}")
            return pd.DataFrame({
                'date': pd.to_datetime([]),
                'pure_ice_mean': [],
                'mostly_ice_mean': [],
                'mixed_high_mean': [],
                'mixed_low_mean': [],
                'border_mean': []
            })
    
    @render.ui
    def timeseries_plot():
        """Render the time series plot"""
        df = filtered_data()
        fraction = input.fraction_class()
        
        # Get the column name for the selected fraction
        mean_col = f"{fraction}_mean"
        
        if mean_col not in df.columns:
            return ui.p(f"No data available for {CLASS_LABELS[fraction]}")
        
        # Create the plot
        fig = px.line(
            df, 
            x='date', 
            y=mean_col,
            title=f"Mean Albedo Trend - {CLASS_LABELS[fraction]}",
            labels={
                'date': 'Date',
                mean_col: 'Mean Albedo',
                'x': 'Date',
                'y': 'Mean Albedo'
            }
        )
        
        # Update traces with fraction color
        color = FRACTION_COLORS.get(fraction, 'blue')
        fig.update_traces(line_color=color)
        
        # Update layout
        fig.update_layout(
            height=500,
            showlegend=False,
            hovermode='x unified'
        )
        
        return ui.HTML(fig.to_html(include_plotlyjs="cdn"))
    
    @render.table
    def data_summary():
        """Render summary statistics table"""
        try:
            df = filtered_data()
            fraction = input.fraction_class()
            mean_col = f"{fraction}_mean"
            
            if mean_col not in df.columns or df.empty:
                return pd.DataFrame({
                    "Statistic": ["Error"], 
                    "Value": [f"No data available for {CLASS_LABELS.get(fraction, fraction)}"]
                })
            
            # Calculate summary statistics with error handling
            series = df[mean_col].dropna()
            if len(series) == 0:
                return pd.DataFrame({
                    "Statistic": ["Error"], 
                    "Value": ["No valid data points"]
                })
            
            stats = series.describe()
            summary_df = pd.DataFrame({
                'Statistic': ['Count', 'Mean', 'Std Dev', 'Min', '25%', '50%', '75%', 'Max'],
                'Value': [
                    f"{stats['count']:.0f}",
                    f"{stats['mean']:.4f}" if pd.notna(stats['mean']) else "N/A",
                    f"{stats['std']:.4f}" if pd.notna(stats['std']) else "N/A",
                    f"{stats['min']:.4f}" if pd.notna(stats['min']) else "N/A",
                    f"{stats['25%']:.4f}" if pd.notna(stats['25%']) else "N/A",
                    f"{stats['50%']:.4f}" if pd.notna(stats['50%']) else "N/A",
                    f"{stats['75%']:.4f}" if pd.notna(stats['75%']) else "N/A",
                    f"{stats['max']:.4f}" if pd.notna(stats['max']) else "N/A"
                ]
            })
            
            return summary_df
            
        except Exception as e:
            print(f"Error in data_summary: {e}")
            return pd.DataFrame({
                "Statistic": ["Error"], 
                "Value": [f"Error calculating summary: {str(e)}"]
            })

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()