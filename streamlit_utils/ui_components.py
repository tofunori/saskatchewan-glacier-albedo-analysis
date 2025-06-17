"""
Streamlit UI Components
=======================

Reusable UI components for the Streamlit interface.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import FRACTION_CLASSES, CLASS_LABELS


def create_dataset_selector(
    label: str = "Select Dataset",
    options: List[str] = ['MCD43A3', 'MOD10A1'],
    default: str = 'MCD43A3',
    key: str = None,
    help_text: str = None
) -> str:
    """
    Create a standardized dataset selector.
    
    Parameters:
    -----------
    label : str
        Label for the selector
    options : list
        Available dataset options
    default : str
        Default selection
    key : str
        Unique key for the widget
    help_text : str
        Help text to display
    
    Returns:
    --------
    str
        Selected dataset name
    """
    if help_text is None:
        help_text = "Choose between general albedo (MCD43A3) or snow albedo (MOD10A1)"
    
    return st.selectbox(
        label,
        options=options,
        index=options.index(default) if default in options else 0,
        key=key,
        help=help_text
    )


def create_fraction_selector(
    label: str = "Select Fraction Classes",
    default: List[str] = None,
    multi: bool = True,
    key: str = None,
    help_text: str = None
) -> List[str] or str:
    """
    Create a standardized fraction class selector.
    
    Parameters:
    -----------
    label : str
        Label for the selector
    default : list or str
        Default selection(s)
    multi : bool
        Whether to allow multiple selections
    key : str
        Unique key for the widget
    help_text : str
        Help text to display
    
    Returns:
    --------
    list or str
        Selected fraction class(es)
    """
    if default is None:
        default = ['pure_ice', 'mostly_ice'] if multi else 'pure_ice'
    
    if help_text is None:
        help_text = "Choose which ice fraction classes to analyze"
    
    if multi:
        return st.multiselect(
            label,
            options=FRACTION_CLASSES,
            default=default,
            format_func=lambda x: CLASS_LABELS[x],
            key=key,
            help=help_text
        )
    else:
        return st.selectbox(
            label,
            options=FRACTION_CLASSES,
            index=FRACTION_CLASSES.index(default) if default in FRACTION_CLASSES else 0,
            format_func=lambda x: CLASS_LABELS[x],
            key=key,
            help=help_text
        )


def create_date_range_selector(
    label: str = "Date Range",
    mode: str = "year_range",
    key_prefix: str = "date",
    help_text: str = None
) -> Dict[str, Any]:
    """
    Create a flexible date range selector.
    
    Parameters:
    -----------
    label : str
        Label for the date range section
    mode : str
        Date selection mode ('year_range', 'custom_range', 'full_range')
    key_prefix : str
        Prefix for widget keys
    help_text : str
        Help text to display
    
    Returns:
    --------
    dict
        Dictionary with date range parameters
    """
    st.subheader(label)
    
    if mode == "year_range":
        col1, col2 = st.columns(2)
        
        with col1:
            start_year = st.number_input(
                "Start Year",
                min_value=2010,
                max_value=2024,
                value=2010,
                key=f"{key_prefix}_start_year",
                help="Starting year for analysis"
            )
        
        with col2:
            end_year = st.number_input(
                "End Year",
                min_value=2010,
                max_value=2024,
                value=2024,
                key=f"{key_prefix}_end_year",
                help="Ending year for analysis"
            )
        
        return {
            'mode': 'year_range',
            'start_year': start_year,
            'end_year': end_year
        }
    
    elif mode == "custom_range":
        from datetime import datetime
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime(2010, 1, 1),
                key=f"{key_prefix}_start_date",
                help="Starting date for analysis"
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime(2024, 12, 31),
                key=f"{key_prefix}_end_date",
                help="Ending date for analysis"
            )
        
        return {
            'mode': 'custom_range',
            'start_date': start_date,
            'end_date': end_date
        }
    
    else:  # full_range
        st.info(f"Using full available date range ({2010}-{2024})")
        return {
            'mode': 'full_range',
            'start_year': 2010,
            'end_year': 2024
        }


def create_analysis_options_panel(
    key_prefix: str = "analysis",
    include_trends: bool = True,
    include_seasonal: bool = True,
    include_quality: bool = True,
    include_visualization: bool = True
) -> Dict[str, Any]:
    """
    Create a comprehensive analysis options panel.
    
    Parameters:
    -----------
    key_prefix : str
        Prefix for widget keys
    include_trends : bool
        Include trend analysis options
    include_seasonal : bool
        Include seasonal analysis options
    include_quality : bool
        Include quality filtering options
    include_visualization : bool
        Include visualization options
    
    Returns:
    --------
    dict
        Dictionary with analysis options
    """
    options = {}
    
    st.subheader("📊 Analysis Options")
    
    if include_trends:
        st.markdown("**Trend Analysis**")
        options['show_trends'] = st.checkbox(
            "Calculate Trends", 
            value=True, 
            key=f"{key_prefix}_show_trends",
            help="Calculate Mann-Kendall trends"
        )
        
        if options['show_trends']:
            options['trend_method'] = st.selectbox(
                "Trend Method",
                options=['Mann-Kendall', 'Linear Regression', 'Theil-Sen'],
                index=0,
                key=f"{key_prefix}_trend_method",
                help="Statistical method for trend calculation"
            )
    
    if include_seasonal:
        st.markdown("**Seasonal Analysis**")
        options['show_seasonality'] = st.checkbox(
            "Seasonal Decomposition", 
            value=False, 
            key=f"{key_prefix}_show_seasonality",
            help="Decompose time series into trend, seasonal, and residual components"
        )
        
        if options.get('show_seasonality', False):
            options['seasonal_period'] = st.selectbox(
                "Seasonal Period",
                options=['Monthly', 'Quarterly', 'Annual'],
                index=0,
                key=f"{key_prefix}_seasonal_period"
            )
    
    if include_quality:
        st.markdown("**Quality Control**")
        options['apply_quality_filter'] = st.checkbox(
            "Apply Quality Filter", 
            value=True, 
            key=f"{key_prefix}_quality_filter",
            help="Filter data based on quality scores"
        )
        
        if options.get('apply_quality_filter', False):
            options['quality_threshold'] = st.slider(
                "Quality Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.05,
                key=f"{key_prefix}_quality_threshold",
                help="Minimum quality score for data inclusion"
            )
    
    if include_visualization:
        st.markdown("**Visualization**")
        options['show_confidence'] = st.checkbox(
            "Show Confidence Intervals", 
            value=True, 
            key=f"{key_prefix}_confidence",
            help="Display uncertainty bands on plots"
        )
        
        options['color_scheme'] = st.selectbox(
            "Color Scheme",
            options=['Default', 'Viridis', 'Plasma', 'Set1', 'Pastel'],
            index=0,
            key=f"{key_prefix}_color_scheme",
            help="Color palette for plots"
        )
    
    return options


def create_export_panel(
    key_prefix: str = "export"
) -> Dict[str, Any]:
    """
    Create an export options panel.
    
    Parameters:
    -----------
    key_prefix : str
        Prefix for widget keys
    
    Returns:
    --------
    dict
        Dictionary with export options
    """
    st.subheader("💾 Export Options")
    
    export_options = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_options['format'] = st.selectbox(
            "Export Format",
            options=['PNG', 'HTML', 'PDF', 'SVG'],
            index=0,
            key=f"{key_prefix}_format",
            help="File format for exported plots"
        )
        
        export_options['include_data'] = st.checkbox(
            "Include Raw Data",
            value=False,
            key=f"{key_prefix}_include_data",
            help="Export raw data along with plots"
        )
    
    with col2:
        export_options['dpi'] = st.number_input(
            "Export DPI",
            min_value=72,
            max_value=300,
            value=150,
            step=10,
            key=f"{key_prefix}_dpi",
            help="Resolution for exported images"
        )
        
        export_options['include_metadata'] = st.checkbox(
            "Include Metadata",
            value=True,
            key=f"{key_prefix}_include_metadata",
            help="Include analysis parameters in export"
        )
    
    return export_options


def display_data_summary(
    data_dict: Dict[str, Any],
    title: str = "Data Overview"
) -> None:
    """
    Display a standardized data summary.
    
    Parameters:
    -----------
    data_dict : dict
        Dictionary with dataset names as keys and data handlers as values
    title : str
        Title for the summary section
    """
    st.header(title)
    
    if not data_dict:
        st.warning("No data available to display.")
        return
    
    # Calculate overall statistics
    total_records = sum(len(handler.data) for handler in data_dict.values())
    
    # Display metrics
    cols = st.columns(len(data_dict) + 1)
    
    for idx, (dataset_name, data_handler) in enumerate(data_dict.items()):
        with cols[idx]:
            st.metric(
                f"{dataset_name} Records",
                f"{len(data_handler.data):,}"
            )
            
            if hasattr(data_handler.data, 'date') and 'date' in data_handler.data.columns:
                date_range = f"{data_handler.data['date'].min().date()} to {data_handler.data['date'].max().date()}"
                st.caption(f"Range: {date_range}")
    
    with cols[-1]:
        st.metric("Total Records", f"{total_records:,}")
        st.caption(f"Datasets: {len(data_dict)}")


def display_statistics_table(
    stats_data: List[Dict],
    title: str = "Statistical Summary",
    precision: int = 4
) -> None:
    """
    Display a standardized statistics table.
    
    Parameters:
    -----------
    stats_data : list
        List of dictionaries with statistical data
    title : str
        Title for the table
    precision : int
        Number of decimal places for formatting
    """
    if not stats_data:
        st.warning("No statistics to display.")
        return
    
    st.subheader(title)
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(stats_data)
    
    # Format numerical columns
    numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
    for col in numerical_cols:
        if col != 'Count':  # Don't format count columns
            df[col] = df[col].apply(lambda x: f"{x:.{precision}f}" if pd.notnull(x) else "N/A")
    
    st.dataframe(df, use_container_width=True, hide_index=True)


def create_progress_tracker(
    steps: List[str],
    current_step: int = 0,
    title: str = "Analysis Progress"
) -> None:
    """
    Create a progress tracker for multi-step analysis.
    
    Parameters:
    -----------
    steps : list
        List of step descriptions
    current_step : int
        Current step index (0-based)
    title : str
        Title for the progress tracker
    """
    st.subheader(title)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, step in enumerate(steps):
        if i <= current_step:
            status = "✅" if i < current_step else "🔄"
            progress_bar.progress((i + 1) / len(steps))
        else:
            status = "⏳"
        
        st.write(f"{status} {step}")
    
    if current_step < len(steps):
        status_text.text(f"Current: {steps[current_step]}")
    else:
        status_text.text("✅ Analysis Complete!")


def create_warning_panel(
    warnings: List[str],
    title: str = "⚠️ Warnings"
) -> None:
    """
    Create a warning panel for data quality issues.
    
    Parameters:
    -----------
    warnings : list
        List of warning messages
    title : str
        Title for the warning panel
    """
    if not warnings:
        return
    
    with st.expander(title, expanded=True):
        for warning in warnings:
            st.warning(warning)


def create_info_panel(
    info_items: Dict[str, str],
    title: str = "ℹ️ Information"
) -> None:
    """
    Create an information panel.
    
    Parameters:
    -----------
    info_items : dict
        Dictionary with information items
    title : str
        Title for the information panel
    """
    with st.expander(title):
        for key, value in info_items.items():
            st.markdown(f"**{key}:** {value}")


def create_help_panel(
    help_text: str,
    title: str = "❓ Help"
) -> None:
    """
    Create a help panel with usage instructions.
    
    Parameters:
    -----------
    help_text : str
        Help text content (markdown supported)
    title : str
        Title for the help panel
    """
    with st.expander(title):
        st.markdown(help_text)


def create_parameter_summary(
    parameters: Dict[str, Any],
    title: str = "📋 Current Configuration"
) -> None:
    """
    Create a summary of current analysis parameters.
    
    Parameters:
    -----------
    parameters : dict
        Dictionary with parameter values
    title : str
        Title for the summary
    """
    with st.expander(title):
        col1, col2 = st.columns(2)
        
        items = list(parameters.items())
        mid_point = len(items) // 2
        
        with col1:
            for key, value in items[:mid_point]:
                st.markdown(f"**{key}:** {value}")
        
        with col2:
            for key, value in items[mid_point:]:
                st.markdown(f"**{key}:** {value}")


def display_download_buttons(
    download_data: Dict[str, Any],
    title: str = "📥 Download Results"
) -> None:
    """
    Create download buttons for various file types.
    
    Parameters:
    -----------
    download_data : dict
        Dictionary with download options and data
    title : str
        Title for the download section
    """
    st.subheader(title)
    
    cols = st.columns(len(download_data))
    
    for idx, (label, data) in enumerate(download_data.items()):
        with cols[idx]:
            if isinstance(data, dict):
                st.download_button(
                    label=f"📄 {label}",
                    data=data.get('content', ''),
                    file_name=data.get('filename', f"{label.lower()}.txt"),
                    mime=data.get('mime', 'text/plain')
                )
            else:
                st.download_button(
                    label=f"📄 {label}",
                    data=str(data),
                    file_name=f"{label.lower()}.txt",
                    mime='text/plain'
                )