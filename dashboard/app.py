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
from data.handler import AlbedoDataHandler
from config import MCD43A3_CONFIG, FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS

# Load data with correct path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(project_root, MCD43A3_CONFIG['csv_path'])
data_handler = AlbedoDataHandler(csv_path)
data_handler.load_data()

app_ui = ui.page_fluid(
    ui.h1("Saskatchewan Glacier Albedo Analysis Dashboard"),
    ui.p("Interactive exploration of MODIS albedo data (2010-2024)"),
    
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.h3("Controls"),
            ui.input_selectize(
                "fraction_class",
                "Select Fraction Class:",
                choices={fc: CLASS_LABELS[fc] for fc in FRACTION_CLASSES},
                selected="pure_ice"
            ),
            ui.p(f"Dataset: {MCD43A3_CONFIG['name']} ({MCD43A3_CONFIG['description']})"),
            ui.p(f"Period: 2010-2024"),
            width=3
        ),
        ui.panel_main(
            ui.h3("Time Series - Mean Albedo"),
            ui.output_ui("timeseries_plot"),
            ui.h4("Data Summary"),
            ui.output_table("data_summary")
        )
    )
)

def server(input, output, session):
    
    @reactive.calc
    def filtered_data():
        """Filter data based on selected fraction class"""
        fraction = input.fraction_class()
        df = data_handler.data.copy()
        
        # Convert date column to datetime if it's not already
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
    
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
        df = filtered_data()
        fraction = input.fraction_class()
        mean_col = f"{fraction}_mean"
        
        if mean_col not in df.columns:
            return pd.DataFrame({"Error": ["No data available"]})
        
        # Calculate summary statistics
        stats = df[mean_col].describe()
        summary_df = pd.DataFrame({
            'Statistic': ['Count', 'Mean', 'Std Dev', 'Min', '25%', '50%', '75%', 'Max'],
            'Value': [
                f"{stats['count']:.0f}",
                f"{stats['mean']:.4f}",
                f"{stats['std']:.4f}",
                f"{stats['min']:.4f}",
                f"{stats['25%']:.4f}",
                f"{stats['50%']:.4f}",
                f"{stats['75%']:.4f}",
                f"{stats['max']:.4f}"
            ]
        })
        
        return summary_df

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()