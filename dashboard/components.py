"""
Dashboard UI Components
======================

Modular UI components for the Saskatchewan Glacier Albedo Dashboard.
"""

from shiny import ui
import plotly.graph_objects as go
import pandas as pd
from config import CLASS_LABELS, FRACTION_COLORS, ANALYSIS_CONFIG

def create_dataset_selector():
    """Create dataset selection component"""
    return ui.div(
        ui.h4("📊 Dataset Selection"),
        ui.input_radio_buttons(
            "dataset",
            "Choose Dataset:",
            choices={
                "MCD43A3": "MCD43A3 (General Albedo, 16-day)",
                "MOD10A1": "MOD10A1 (Snow Albedo, Daily)",
                "COMPARISON": "📊 Compare Datasets"
            },
            selected="MCD43A3"
        ),
        ui.p("🔍 MCD43A3: MODIS Combined Terra+Aqua, 16-day composite"),
        ui.p("❄️ MOD10A1: Terra Snow Cover, daily observations"),
        class_="sidebar-panel"
    )

def create_filter_panel():
    """Create filtering controls"""
    return ui.div(
        ui.h4("🎯 Data Filters"),
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
        ui.input_slider(
            "quality_threshold",
            "Minimum Data Quality (%):",
            min=0,
            max=100,
            value=60,
            step=5
        ),
        class_="sidebar-panel"
    )

def create_analysis_options():
    """Create analysis configuration panel"""
    return ui.div(
        ui.h4("📈 Analysis Options"),
        ui.input_select(
            "analysis_variable",
            "Variable to Analyze:",
            choices={"mean": "Mean Albedo", "median": "Median Albedo"},
            selected="mean"
        ),
        ui.input_checkbox(
            "show_trends", 
            "Show Trend Lines", 
            value=True
        ),
        ui.input_checkbox(
            "show_seasonal", 
            "Highlight Seasonal Patterns", 
            value=False
        ),
        ui.input_checkbox(
            "show_confidence",
            "Show Confidence Intervals",
            value=False
        ),
        ui.input_select(
            "trend_method",
            "Trend Analysis Method:",
            choices={
                "mann_kendall": "Mann-Kendall Test",
                "linear": "Linear Regression",
                "theil_sen": "Theil-Sen Estimator"
            },
            selected="mann_kendall"
        ),
        class_="sidebar-panel"
    )

def create_summary_card(title, value, subtitle="", color="primary"):
    """Create a summary metric card"""
    color_map = {
        "primary": "#0d6efd",
        "success": "#198754", 
        "warning": "#ffc107",
        "danger": "#dc3545",
        "info": "#0dcaf0"
    }
    
    return ui.div(
        ui.h5(title, style=f"color: {color_map.get(color, '#0d6efd')}; margin-bottom: 5px;"),
        ui.h3(str(value), style="margin: 0; font-weight: bold;"),
        ui.p(subtitle, style="margin: 5px 0 0 0; color: #6c757d; font-size: 0.9em;"),
        style="""
            background: white;
            border: 1px solid #e0e0e0;
            border-left: 4px solid {color};
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        """.replace("{color}", color_map.get(color, '#0d6efd'))
    )

def create_plot_card(title, plot_id, height="500px"):
    """Create a standardized plot container"""
    return ui.div(
        ui.h4(title, style="margin-bottom: 15px; color: #333;"),
        ui.output_plot(plot_id),
        class_="plot-container",
        style=f"min-height: {height};"
    )

def create_data_table_card(title, table_id):
    """Create a data table container"""
    return ui.div(
        ui.h4(title, style="margin-bottom: 15px; color: #333;"),
        ui.output_table(table_id),
        class_="plot-container"
    )

def create_export_panel():
    """Create data export controls"""
    return ui.div(
        ui.h4("💾 Export Options"),
        ui.input_checkbox_group(
            "export_formats",
            "Export Formats:",
            choices={
                "csv": "📊 CSV Data",
                "excel": "📈 Excel Workbook", 
                "png": "🖼️ PNG Images",
                "pdf": "📄 PDF Report"
            },
            selected=["csv"]
        ),
        ui.input_text(
            "export_filename",
            "Filename Prefix:",
            value="saskatchewan_albedo_export"
        ),
        ui.input_action_button(
            "export_data",
            "📥 Export Data",
            class_="btn-primary"
        ),
        ui.output_text("export_status"),
        class_="sidebar-panel"
    )

def create_info_panel():
    """Create information panel with dataset details"""
    return ui.div(
        ui.h4("ℹ️ Dataset Information"),
        ui.div(
            ui.h5("📅 Temporal Coverage"),
            ui.p("2010-2024 (15 years)"),
            ui.h5("🗺️ Spatial Coverage"), 
            ui.p("Saskatchewan Glacier, Canada"),
            ui.h5("🛰️ Satellite Data"),
            ui.p("MODIS Terra & Aqua"),
            ui.h5("📊 Fraction Classes"),
            ui.tags.ul([
                ui.tags.li(f"{label} ({key})")
                for key, label in CLASS_LABELS.items()
            ])
        ),
        class_="sidebar-panel",
        style="font-size: 0.9em;"
    )

def create_advanced_filters():
    """Create advanced filtering options"""
    return ui.div(
        ui.h4("🔬 Advanced Filters"),
        ui.input_select(
            "season_filter",
            "Season Focus:",
            choices={
                "all": "All Seasons",
                "summer": "Summer (JJA)",
                "melt_season": "Melt Season (May-Sep)",
                "accumulation": "Accumulation (Oct-Apr)"
            },
            selected="all"
        ),
        ui.input_slider(
            "pixel_threshold",
            "Minimum Pixel Count:",
            min=0,
            max=1000,
            value=10,
            step=5
        ),
        ui.input_checkbox_group(
            "quality_classes",
            "Include Quality Classes:",
            choices={
                "best": "Best Quality",
                "good": "Good Quality", 
                "moderate": "Moderate Quality",
                "poor": "Poor Quality"
            },
            selected=["best", "good"]
        ),
        class_="sidebar-panel"
    )