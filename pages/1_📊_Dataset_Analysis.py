"""
Dataset Analysis Page
====================

Analyze individual MODIS datasets (MCD43A3 or MOD10A1) with interactive visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
import numpy as np
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import project modules
from config import (
    OUTPUT_DIR, 
    FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS,
    MCD43A3_CONFIG, MOD10A1_CONFIG, ANALYSIS_CONFIG
)
from data.handler import AlbedoDataHandler
from data.dataset_manager import DatasetManager
from analysis.trends import TrendCalculator
from analysis.seasonal import SeasonalAnalyzer

# Page config
st.set_page_config(
    page_title="Dataset Analysis - Saskatchewan Glacier",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Dataset Analysis")
st.markdown("Analyze individual MODIS datasets with interactive visualizations")

# Initialize session state
if 'current_dataset' not in st.session_state:
    st.session_state.current_dataset = 'MCD43A3'
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Analysis Settings")
    
    # Dataset selection
    dataset = st.selectbox(
        "Select Dataset",
        options=['MCD43A3', 'MOD10A1'],
        index=0 if st.session_state.current_dataset == 'MCD43A3' else 1,
        help="Choose between general albedo (MCD43A3) or snow albedo (MOD10A1)"
    )
    
    # Update session state if dataset changed
    if dataset != st.session_state.current_dataset:
        st.session_state.current_dataset = dataset
        st.session_state.data_loaded = False
    
    # Fraction selection
    selected_fractions = st.multiselect(
        "Select Fraction Classes",
        options=FRACTION_CLASSES,
        default=['pure_ice', 'mostly_ice'],
        format_func=lambda x: CLASS_LABELS[x],
        help="Choose which ice fraction classes to analyze"
    )
    
    # Date range
    st.subheader("📅 Date Range")
    col1, col2 = st.columns(2)
    with col1:
        start_year = st.number_input(
            "Start Year",
            min_value=2010,
            max_value=2024,
            value=2010
        )
    with col2:
        end_year = st.number_input(
            "End Year",
            min_value=2010,
            max_value=2024,
            value=2024
        )
    
    # Analysis options
    st.subheader("📈 Analysis Options")
    show_trend = st.checkbox("Show Trend Line", value=True)
    show_confidence = st.checkbox("Show Confidence Interval", value=True)
    smoothing_window = st.slider(
        "Smoothing Window (days)",
        min_value=0,
        max_value=30,
        value=0,
        help="Apply moving average smoothing (0 = no smoothing)"
    )

# Load data with caching
@st.cache_data
def load_dataset_data(dataset_name, start_year, end_year):
    """Load and prepare dataset with caching"""
    try:
        manager = DatasetManager()
        
        # Load the appropriate dataset
        if dataset_name == 'MCD43A3':
            data_handler = manager.load_mcd43a3()
        else:
            data_handler = manager.load_mod10a1()
        
        if data_handler is None:
            return None, "Failed to load dataset"
        
        # Filter by date range
        data_handler.data = data_handler.data[
            (data_handler.data['year'] >= start_year) & 
            (data_handler.data['year'] <= end_year)
        ]
        
        return data_handler, None
    except Exception as e:
        return None, str(e)

# Main content area
main_container = st.container()

with main_container:
    # Load data
    if st.button("🔄 Load/Refresh Data", type="primary"):
        with st.spinner(f"Loading {dataset} data..."):
            data_handler, error = load_dataset_data(dataset, start_year, end_year)
            if error:
                st.error(f"Error loading data: {error}")
            else:
                st.session_state.data_handler = data_handler
                st.session_state.data_loaded = True
                st.success(f"✅ {dataset} data loaded successfully!")
    
    # Display analysis if data is loaded
    if st.session_state.data_loaded and hasattr(st.session_state, 'data_handler'):
        data_handler = st.session_state.data_handler
        
        # Data overview
        st.header("📊 Data Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", f"{len(data_handler.data):,}")
        with col2:
            st.metric("Date Range", f"{data_handler.data['date'].min()} to {data_handler.data['date'].max()}")
        with col3:
            unique_fractions = [f for f in FRACTION_CLASSES if f"{f}_mean" in data_handler.data.columns]
            st.metric("Available Fractions", len(unique_fractions))
        with col4:
            st.metric("Dataset", dataset)
        
        # Time series visualization
        st.header("📈 Time Series Analysis")
        
        # Create tabs for different visualizations
        tab1, tab2, tab3, tab4 = st.tabs(["Time Series", "Seasonal Patterns", "Trend Analysis", "Statistics"])
        
        with tab1:
            st.subheader("Albedo Time Series")
            
            # Prepare data for plotting
            fig = go.Figure()
            
            for fraction in selected_fractions:
                col_name = f"{fraction}_mean"
                if col_name in data_handler.data.columns:
                    y_data = data_handler.data[col_name]
                    
                    # Apply smoothing if requested
                    if smoothing_window > 0:
                        y_data = y_data.rolling(window=smoothing_window, center=True).mean()
                    
                    # Add main trace
                    fig.add_trace(go.Scatter(
                        x=data_handler.data['date'],
                        y=y_data,
                        mode='lines',
                        name=CLASS_LABELS[fraction],
                        line=dict(color=FRACTION_COLORS.get(fraction, '#000000')),
                        opacity=0.8
                    ))
                    
                    # Add trend line if requested
                    if show_trend:
                        # Calculate trend using TrendCalculator
                        trend_calc = TrendCalculator(data_handler)
                        trends = trend_calc.calculate_basic_trends(fraction)
                        
                        if trends and 'slope' in trends:
                            # Create trend line
                            x_numeric = pd.to_numeric(data_handler.data['date']).values
                            x_normalized = (x_numeric - x_numeric.min()) / (365.25 * 24 * 3600 * 1e9)  # Convert to years
                            trend_line = trends['intercept'] + trends['slope'] * x_normalized
                            
                            fig.add_trace(go.Scatter(
                                x=data_handler.data['date'],
                                y=trend_line,
                                mode='lines',
                                name=f"{CLASS_LABELS[fraction]} Trend",
                                line=dict(color=CLASS_COLORS.get(fraction, '#000000'), dash='dash'),
                                opacity=0.6
                            ))
            
            fig.update_layout(
                title=f"{dataset} Albedo Time Series ({start_year}-{end_year})",
                xaxis_title="Date",
                yaxis_title="Albedo",
                height=500,
                hovermode='x unified',
                showlegend=True,
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Download button for the plot
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("📥 Download Plot", key="download_timeseries"):
                    fig.write_html(f"{dataset}_timeseries.html")
                    st.success("Plot saved as HTML!")
        
        with tab2:
            st.subheader("Seasonal Patterns")
            
            # Calculate monthly averages
            seasonal_analyzer = SeasonalAnalyzer(data_handler)
            
            # Create seasonal pattern plot
            fig_seasonal = go.Figure()
            
            for fraction in selected_fractions:
                monthly_stats = seasonal_analyzer.calculate_monthly_statistics(fraction)
                if monthly_stats is not None:
                    fig_seasonal.add_trace(go.Scatter(
                        x=list(range(1, 13)),
                        y=monthly_stats['mean'],
                        mode='lines+markers',
                        name=CLASS_LABELS[fraction],
                        line=dict(color=FRACTION_COLORS.get(fraction, '#000000')),
                        error_y=dict(
                            type='data',
                            array=monthly_stats['std'],
                            visible=show_confidence
                        )
                    ))
            
            fig_seasonal.update_layout(
                title=f"Monthly Average Albedo - {dataset}",
                xaxis_title="Month",
                yaxis_title="Average Albedo",
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(1, 13)),
                    ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                ),
                height=400,
                template="plotly_white"
            )
            
            st.plotly_chart(fig_seasonal, use_container_width=True)
        
        with tab3:
            st.subheader("Trend Analysis Results")
            
            # Calculate trends for selected fractions
            trend_calc = TrendCalculator(data_handler)
            
            # Create results dataframe
            results = []
            for fraction in selected_fractions:
                trends = trend_calc.calculate_basic_trends(fraction)
                if trends:
                    results.append({
                        'Fraction': CLASS_LABELS[fraction],
                        'Slope (per year)': f"{trends['slope']:.4f}",
                        'P-value': f"{trends['p_value']:.4f}",
                        'Significant': '✅ Yes' if trends['p_value'] < 0.05 else '❌ No',
                        'Trend': '📈 Increasing' if trends['slope'] > 0 else '📉 Decreasing'
                    })
            
            if results:
                df_results = pd.DataFrame(results)
                st.dataframe(df_results, use_container_width=True, hide_index=True)
                
                # Visualize slopes
                st.subheader("Trend Comparison")
                
                slopes = [float(r['Slope (per year)']) for r in results]
                fractions = [r['Fraction'] for r in results]
                
                fig_bars = go.Figure(data=[
                    go.Bar(
                        x=fractions,
                        y=slopes,
                        marker_color=['green' if s > 0 else 'red' for s in slopes]
                    )
                ])
                
                fig_bars.update_layout(
                    title="Albedo Trends by Fraction Class",
                    xaxis_title="Fraction Class",
                    yaxis_title="Trend (per year)",
                    height=400,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_bars, use_container_width=True)
            else:
                st.warning("No trend results available for selected fractions")
        
        with tab4:
            st.subheader("Statistical Summary")
            
            # Calculate statistics for each fraction
            stats_data = []
            for fraction in selected_fractions:
                col_name = f"{fraction}_mean"
                if col_name in data_handler.data.columns:
                    data = data_handler.data[col_name].dropna()
                    stats_data.append({
                        'Fraction': CLASS_LABELS[fraction],
                        'Mean': f"{data.mean():.4f}",
                        'Median': f"{data.median():.4f}",
                        'Std Dev': f"{data.std():.4f}",
                        'Min': f"{data.min():.4f}",
                        'Max': f"{data.max():.4f}",
                        'Count': len(data)
                    })
            
            if stats_data:
                df_stats = pd.DataFrame(stats_data)
                st.dataframe(df_stats, use_container_width=True, hide_index=True)
                
                # Distribution plot
                st.subheader("Albedo Distribution")
                
                fig_dist = go.Figure()
                
                for fraction in selected_fractions:
                    col_name = f"{fraction}_mean"
                    if col_name in data_handler.data.columns:
                        data = data_handler.data[col_name].dropna()
                        fig_dist.add_trace(go.Histogram(
                            x=data,
                            name=CLASS_LABELS[fraction],
                            opacity=0.7,
                            nbinsx=50
                        ))
                
                fig_dist.update_layout(
                    title=f"Albedo Distribution - {dataset}",
                    xaxis_title="Albedo",
                    yaxis_title="Frequency",
                    barmode='overlay',
                    height=400,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_dist, use_container_width=True)
    
    else:
        # Show instructions if no data loaded
        st.info("""
        👈 **Getting Started:**
        1. Select a dataset from the sidebar
        2. Choose fraction classes to analyze
        3. Set your date range
        4. Click "Load/Refresh Data" to begin analysis
        """)
        
        # Show available datasets info
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🌍 MCD43A3
            - **Type**: General Albedo
            - **Resolution**: 16-day composite
            - **Best for**: Long-term trend analysis
            """)
        
        with col2:
            st.markdown("""
            ### ❄️ MOD10A1
            - **Type**: Snow Albedo
            - **Resolution**: Daily
            - **Best for**: High-resolution seasonal analysis
            """)