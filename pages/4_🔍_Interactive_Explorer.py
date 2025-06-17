"""
Interactive Explorer Page
========================

Custom analysis with flexible parameters, date ranges, and export capabilities.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
import sys
from datetime import datetime, timedelta
import io

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import project modules
from config import (
    FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS,
    ANALYSIS_CONFIG
)
from data.dataset_manager import DatasetManager
from analysis.trends import TrendCalculator
from analysis.seasonal import SeasonalAnalyzer
from utils.exports import ExportManager

# Page config
st.set_page_config(
    page_title="Interactive Explorer - Saskatchewan Glacier",
    page_icon="🔍",
    layout="wide"
)

# Title
st.title("🔍 Interactive Explorer")
st.markdown("Flexible analysis tool with custom parameters and export capabilities")

# Initialize session state
if 'explorer_data_loaded' not in st.session_state:
    st.session_state.explorer_data_loaded = False
if 'export_manager' not in st.session_state:
    st.session_state.export_manager = ExportManager()

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Analysis Configuration")
    
    # Dataset selection
    st.subheader("📊 Dataset Selection")
    datasets = st.multiselect(
        "Select Datasets",
        options=['MCD43A3', 'MOD10A1'],
        default=['MCD43A3'],
        help="Choose one or both datasets for analysis"
    )
    
    # Fraction selection
    st.subheader("🧊 Fraction Classes")
    selected_fractions = st.multiselect(
        "Select Fraction Classes",
        options=FRACTION_CLASSES,
        default=['pure_ice', 'mostly_ice'],
        format_func=lambda x: CLASS_LABELS[x]
    )
    
    # Date range with flexible options
    st.subheader("📅 Date Range")
    
    date_mode = st.radio(
        "Date Selection Mode",
        options=['Full Range', 'Year Range', 'Custom Range', 'Specific Seasons'],
        index=0
    )
    
    if date_mode == 'Year Range':
        col1, col2 = st.columns(2)
        with col1:
            start_year = st.number_input("Start Year", min_value=2010, max_value=2024, value=2010)
        with col2:
            end_year = st.number_input("End Year", min_value=2010, max_value=2024, value=2024)
    elif date_mode == 'Custom Range':
        start_date = st.date_input("Start Date", value=datetime(2010, 1, 1))
        end_date = st.date_input("End Date", value=datetime(2024, 12, 31))
    elif date_mode == 'Specific Seasons':
        selected_seasons = st.multiselect(
            "Select Seasons",
            options=['Spring (MAM)', 'Summer (JJA)', 'Autumn (SON)', 'Winter (DJF)'],
            default=['Summer (JJA)']
        )
        season_years = st.multiselect(
            "Select Years",
            options=list(range(2010, 2024 + 1)),
            default=[2024 - 2, 2024 - 1, 2024]
        )
    
    # Analysis parameters
    st.subheader("📈 Analysis Parameters")
    
    # Quality filtering
    quality_filter = st.checkbox("Apply Quality Filter", value=True)
    if quality_filter:
        quality_threshold = st.slider(
            "Quality Threshold",
            min_value=0.0,
            max_value=1.0,
            value=ANALYSIS_CONFIG['quality_threshold']/100.0,
            step=0.05,
            help="Minimum quality score for data inclusion"
        )
    
    # Temporal aggregation
    temporal_agg = st.selectbox(
        "Temporal Aggregation",
        options=['None', 'Daily', 'Weekly', 'Monthly', 'Seasonal', 'Annual'],
        index=0,
        help="Aggregate data over time periods"
    )
    
    # Statistical options
    st.subheader("📊 Statistical Options")
    
    show_trends = st.checkbox("Calculate Trends", value=True)
    show_seasonality = st.checkbox("Show Seasonal Decomposition", value=False)
    show_statistics = st.checkbox("Calculate Descriptive Statistics", value=True)
    
    # Visualization options
    st.subheader("🎨 Visualization Options")
    
    chart_type = st.selectbox(
        "Primary Chart Type",
        options=['Time Series', 'Scatter Matrix', 'Correlation Heatmap', 'Distribution', 'Box Plots'],
        index=0
    )
    
    color_scheme = st.selectbox(
        "Color Scheme",
        options=['Default', 'Viridis', 'Plasma', 'Inferno', 'Set1', 'Pastel'],
        index=0
    )
    
    show_confidence = st.checkbox("Show Confidence Intervals", value=True)
    show_annotations = st.checkbox("Show Data Annotations", value=False)
    
    # Export options
    st.subheader("💾 Export Options")
    
    export_format = st.selectbox(
        "Export Format",
        options=['PNG', 'HTML', 'PDF', 'SVG'],
        index=0
    )
    
    export_dpi = st.number_input(
        "Export DPI",
        min_value=72,
        max_value=300,
        value=150,
        step=10
    )

# Load data function
@st.cache_data
def load_explorer_data(datasets, start_year=None, end_year=None, start_date=None, end_date=None):
    """Load data based on flexible parameters"""
    try:
        manager = DatasetManager()
        loaded_data = {}
        
        for dataset in datasets:
            if dataset == 'MCD43A3':
                data_handler = manager.load_mcd43a3()
            else:
                data_handler = manager.load_mod10a1()
            
            if data_handler is not None:
                # Apply date filters
                if start_year is not None and end_year is not None:
                    data_handler.data = data_handler.data[
                        (data_handler.data['year'] >= start_year) & 
                        (data_handler.data['year'] <= end_year)
                    ]
                elif start_date is not None and end_date is not None:
                    data_handler.data = data_handler.data[
                        (data_handler.data['date'] >= pd.Timestamp(start_date)) & 
                        (data_handler.data['date'] <= pd.Timestamp(end_date))
                    ]
                
                loaded_data[dataset] = data_handler
        
        return loaded_data, None
        
    except Exception as e:
        return None, str(e)

# Helper function to apply seasonal filter
def apply_seasonal_filter(data, seasons, years):
    """Filter data for specific seasons and years"""
    season_months = {
        'Spring (MAM)': [3, 4, 5],
        'Summer (JJA)': [6, 7, 8],
        'Autumn (SON)': [9, 10, 11],
        'Winter (DJF)': [12, 1, 2]
    }
    
    filtered_data = data[
        (data['year'].isin(years)) & 
        (data['date'].dt.month.isin([month for season in seasons for month in season_months[season]]))
    ]
    
    return filtered_data

# Main content
main_container = st.container()

with main_container:
    # Configuration summary
    with st.expander("📋 Current Configuration", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Datasets:**")
            for dataset in datasets:
                st.markdown(f"- {dataset}")
            
            st.markdown("**Fractions:**")
            for fraction in selected_fractions:
                st.markdown(f"- {CLASS_LABELS[fraction]}")
        
        with col2:
            st.markdown("**Date Range:**")
            st.markdown(f"- Mode: {date_mode}")
            if date_mode == 'Year Range':
                st.markdown(f"- Years: {start_year}-{end_year}")
            elif date_mode == 'Custom Range':
                st.markdown(f"- From: {start_date}")
                st.markdown(f"- To: {end_date}")
            elif date_mode == 'Specific Seasons':
                st.markdown(f"- Seasons: {', '.join(selected_seasons)}")
                st.markdown(f"- Years: {', '.join(map(str, season_years))}")
        
        with col3:
            st.markdown("**Analysis:**")
            st.markdown(f"- Chart Type: {chart_type}")
            st.markdown(f"- Temporal Agg: {temporal_agg}")
            st.markdown(f"- Quality Filter: {'Yes' if quality_filter else 'No'}")
    
    # Load data button
    load_params = {}
    if date_mode == 'Year Range':
        load_params = {'start_year': start_year, 'end_year': end_year}
    elif date_mode == 'Custom Range':
        load_params = {'start_date': start_date, 'end_date': end_date}
    
    if st.button("🔄 Load/Refresh Data", type="primary"):
        with st.spinner("Loading data with custom parameters..."):
            data_dict, error = load_explorer_data(datasets, **load_params)
            
            if error:
                st.error(f"Error loading data: {error}")
            else:
                # Apply additional filters
                for dataset_name, data_handler in data_dict.items():
                    if date_mode == 'Specific Seasons':
                        data_handler.data = apply_seasonal_filter(
                            data_handler.data, selected_seasons, season_years
                        )
                    
                    # Apply quality filter
                    if quality_filter and 'quality_score' in data_handler.data.columns:
                        data_handler.data = data_handler.data[
                            data_handler.data['quality_score'] >= quality_threshold
                        ]
                
                st.session_state.explorer_data = data_dict
                st.session_state.explorer_data_loaded = True
                st.success(f"✅ Data loaded successfully! {len(datasets)} dataset(s), {sum(len(dh.data) for dh in data_dict.values()):,} total records")
    
    # Display analysis if data is loaded
    if st.session_state.explorer_data_loaded and hasattr(st.session_state, 'explorer_data'):
        data_dict = st.session_state.explorer_data
        
        # Data overview
        st.header("📊 Data Overview")
        
        overview_cols = st.columns(len(datasets) + 1)
        
        for idx, (dataset_name, data_handler) in enumerate(data_dict.items()):
            with overview_cols[idx]:
                st.metric(f"{dataset_name} Records", f"{len(data_handler.data):,}")
                st.metric(f"{dataset_name} Date Range", 
                         f"{data_handler.data['date'].min().date()} to {data_handler.data['date'].max().date()}")
        
        with overview_cols[-1]:
            total_records = sum(len(dh.data) for dh in data_dict.values())
            st.metric("Total Records", f"{total_records:,}")
            st.metric("Selected Fractions", len(selected_fractions))
        
        # Main visualization based on chart type
        st.header(f"📈 {chart_type} Analysis")
        
        if chart_type == 'Time Series':
            # Create comprehensive time series plot
            fig = go.Figure()
            
            for dataset_name, data_handler in data_dict.items():
                for fraction in selected_fractions:
                    col_name = f"{fraction}_mean"
                    if col_name in data_handler.data.columns:
                        # Apply temporal aggregation if requested
                        plot_data = data_handler.data.copy()
                        
                        if temporal_agg == 'Weekly':
                            plot_data = plot_data.groupby(plot_data['date'].dt.to_period('W')).mean().reset_index()
                            plot_data['date'] = plot_data['date'].dt.to_timestamp()
                        elif temporal_agg == 'Monthly':
                            plot_data = plot_data.groupby(plot_data['date'].dt.to_period('M')).mean().reset_index()
                            plot_data['date'] = plot_data['date'].dt.to_timestamp()
                        elif temporal_agg == 'Seasonal':
                            plot_data['season'] = plot_data['date'].dt.month.map(
                                lambda x: 'Winter' if x in [12, 1, 2] else
                                         'Spring' if x in [3, 4, 5] else
                                         'Summer' if x in [6, 7, 8] else 'Autumn'
                            )
                            plot_data = plot_data.groupby(['year', 'season']).mean().reset_index()
                            plot_data['date'] = pd.to_datetime(plot_data['year'].astype(str) + '-' + 
                                                             plot_data['season'].map({
                                                                 'Winter': '01-01', 'Spring': '04-01',
                                                                 'Summer': '07-01', 'Autumn': '10-01'
                                                             }))
                        elif temporal_agg == 'Annual':
                            plot_data = plot_data.groupby('year').mean().reset_index()
                            plot_data['date'] = pd.to_datetime(plot_data['year'].astype(str) + '-01-01')
                        
                        # Determine color
                        if color_scheme == 'Default':
                            color = FRACTION_COLORS.get(fraction, '#000000')
                        else:
                            # Use plotly color scales
                            import plotly.colors as pc
                            colors = getattr(pc.qualitative, color_scheme, pc.qualitative.Set1)
                            color_idx = (list(selected_fractions).index(fraction) + 
                                       len(selected_fractions) * list(datasets).index(dataset_name)) % len(colors)
                            color = colors[color_idx]
                        
                        # Add trace
                        line_style = 'solid' if dataset_name == 'MCD43A3' else 'dash'
                        
                        fig.add_trace(go.Scatter(
                            x=plot_data['date'],
                            y=plot_data[col_name],
                            mode='lines' + ('+markers' if temporal_agg in ['Seasonal', 'Annual'] else ''),
                            name=f"{dataset_name} - {CLASS_LABELS[fraction]}",
                            line=dict(color=color, width=2, dash=line_style),
                            opacity=0.8
                        ))
                        
                        # Add confidence intervals if requested
                        if show_confidence and f"{fraction}_std" in plot_data.columns:
                            upper = plot_data[col_name] + plot_data[f"{fraction}_std"]
                            lower = plot_data[col_name] - plot_data[f"{fraction}_std"]
                            
                            fig.add_trace(go.Scatter(
                                x=plot_data['date'],
                                y=upper,
                                mode='lines',
                                line=dict(width=0),
                                showlegend=False,
                                hoverinfo='skip'
                            ))
                            
                            fig.add_trace(go.Scatter(
                                x=plot_data['date'],
                                y=lower,
                                mode='lines',
                                line=dict(width=0),
                                fill='tonexty',
                                fillcolor=f'rgba{tuple(list(px.colors.hex_to_rgb(color)) + [0.2])}',
                                showlegend=False,
                                hoverinfo='skip'
                            ))
            
            fig.update_layout(
                title=f"Albedo Time Series - {temporal_agg if temporal_agg != 'None' else 'Raw'} Data",
                xaxis_title="Date",
                yaxis_title="Albedo",
                height=600,
                hovermode='x unified',
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == 'Scatter Matrix':
            # Create scatter matrix for fraction comparisons
            if len(selected_fractions) >= 2:
                # Prepare data for scatter matrix
                combined_data = pd.DataFrame()
                
                for dataset_name, data_handler in data_dict.items():
                    temp_data = data_handler.data[['date'] + [f"{f}_mean" for f in selected_fractions if f"{f}_mean" in data_handler.data.columns]].copy()
                    temp_data['dataset'] = dataset_name
                    combined_data = pd.concat([combined_data, temp_data], ignore_index=True)
                
                # Create scatter matrix
                fraction_cols = [f"{f}_mean" for f in selected_fractions if f"{f}_mean" in combined_data.columns]
                
                if len(fraction_cols) >= 2:
                    fig = px.scatter_matrix(
                        combined_data,
                        dimensions=fraction_cols,
                        color='dataset',
                        title="Albedo Fraction Correlation Matrix",
                        labels={col: CLASS_LABELS[col.replace('_mean', '')] for col in fraction_cols}
                    )
                    
                    fig.update_layout(height=600)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Need at least 2 fraction classes for scatter matrix")
            else:
                st.warning("Need at least 2 fraction classes for scatter matrix")
        
        elif chart_type == 'Correlation Heatmap':
            # Create correlation heatmap
            all_correlations = {}
            
            for dataset_name, data_handler in data_dict.items():
                fraction_cols = [f"{f}_mean" for f in selected_fractions if f"{f}_mean" in data_handler.data.columns]
                
                if len(fraction_cols) >= 2:
                    corr_matrix = data_handler.data[fraction_cols].corr()
                    
                    # Rename columns/index for display
                    display_names = {col: CLASS_LABELS[col.replace('_mean', '')] for col in fraction_cols}
                    corr_matrix.rename(columns=display_names, index=display_names, inplace=True)
                    
                    fig = px.imshow(
                        corr_matrix,
                        color_continuous_scale='RdBu_r',
                        aspect='auto',
                        title=f"Fraction Correlation Matrix - {dataset_name}",
                        text_auto=True
                    )
                    
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"Need at least 2 fraction classes for correlation heatmap ({dataset_name})")
        
        elif chart_type == 'Distribution':
            # Create distribution plots
            for dataset_name, data_handler in data_dict.items():
                st.subheader(f"Distribution Analysis - {dataset_name}")
                
                fig = make_subplots(
                    rows=1, cols=len(selected_fractions),
                    subplot_titles=[CLASS_LABELS[f] for f in selected_fractions]
                )
                
                for idx, fraction in enumerate(selected_fractions):
                    col_name = f"{fraction}_mean"
                    if col_name in data_handler.data.columns:
                        data = data_handler.data[col_name].dropna()
                        
                        fig.add_trace(
                            go.Histogram(
                                x=data,
                                nbinsx=50,
                                name=CLASS_LABELS[fraction],
                                showlegend=False
                            ),
                            row=1, col=idx+1
                        )
                
                fig.update_layout(height=400, title=f"Albedo Distributions - {dataset_name}")
                st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == 'Box Plots':
            # Create box plots by season or year
            aggregation_level = st.selectbox(
                "Box Plot Grouping",
                options=['Month', 'Season', 'Year'],
                index=0
            )
            
            for dataset_name, data_handler in data_dict.items():
                st.subheader(f"Box Plot Analysis - {dataset_name}")
                
                plot_data = data_handler.data.copy()
                
                # Create grouping column
                if aggregation_level == 'Month':
                    plot_data['group'] = plot_data['date'].dt.month
                    group_labels = {i: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][i-1] 
                                  for i in range(1, 13)}
                elif aggregation_level == 'Season':
                    plot_data['group'] = plot_data['date'].dt.month.map(
                        lambda x: 'Winter' if x in [12, 1, 2] else
                                 'Spring' if x in [3, 4, 5] else
                                 'Summer' if x in [6, 7, 8] else 'Autumn'
                    )
                    group_labels = None
                else:  # Year
                    plot_data['group'] = plot_data['year']
                    group_labels = None
                
                fig = go.Figure()
                
                for fraction in selected_fractions:
                    col_name = f"{fraction}_mean"
                    if col_name in plot_data.columns:
                        for group in sorted(plot_data['group'].unique()):
                            group_data = plot_data[plot_data['group'] == group][col_name].dropna()
                            
                            if len(group_data) > 0:
                                display_name = group_labels[group] if group_labels else str(group)
                                
                                fig.add_trace(go.Box(
                                    y=group_data,
                                    name=f"{CLASS_LABELS[fraction]} - {display_name}",
                                    boxpoints='outliers'
                                ))
                
                fig.update_layout(
                    title=f"Albedo Distribution by {aggregation_level} - {dataset_name}",
                    yaxis_title="Albedo",
                    height=500,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Statistical analysis section
        if show_statistics or show_trends or show_seasonality:
            st.header("📊 Statistical Analysis")
            
            tabs = []
            if show_statistics:
                tabs.append("Descriptive Statistics")
            if show_trends:
                tabs.append("Trend Analysis")
            if show_seasonality:
                tabs.append("Seasonal Decomposition")
            
            tab_objects = st.tabs(tabs)
            tab_idx = 0
            
            if show_statistics:
                with tab_objects[tab_idx]:
                    st.subheader("Descriptive Statistics")
                    
                    for dataset_name, data_handler in data_dict.items():
                        st.markdown(f"### {dataset_name}")
                        
                        stats_data = []
                        for fraction in selected_fractions:
                            col_name = f"{fraction}_mean"
                            if col_name in data_handler.data.columns:
                                data = data_handler.data[col_name].dropna()
                                
                                stats_data.append({
                                    'Fraction': CLASS_LABELS[fraction],
                                    'Count': len(data),
                                    'Mean': f"{data.mean():.4f}",
                                    'Median': f"{data.median():.4f}",
                                    'Std Dev': f"{data.std():.4f}",
                                    'Min': f"{data.min():.4f}",
                                    'Max': f"{data.max():.4f}",
                                    'Skewness': f"{data.skew():.3f}",
                                    'Kurtosis': f"{data.kurtosis():.3f}"
                                })
                        
                        if stats_data:
                            stats_df = pd.DataFrame(stats_data)
                            st.dataframe(stats_df, use_container_width=True, hide_index=True)
                
                tab_idx += 1
            
            if show_trends:
                with tab_objects[tab_idx]:
                    st.subheader("Trend Analysis")
                    
                    for dataset_name, data_handler in data_dict.items():
                        st.markdown(f"### {dataset_name}")
                        
                        trend_calc = TrendCalculator(data_handler)
                        trend_results = []
                        
                        for fraction in selected_fractions:
                            trends = trend_calc.calculate_basic_trends(fraction)
                            if trends:
                                trend_results.append({
                                    'Fraction': CLASS_LABELS[fraction],
                                    'Slope (per year)': f"{trends['slope']:.6f}",
                                    'P-value': f"{trends['p_value']:.4f}",
                                    'Tau': f"{trends['tau']:.3f}",
                                    'Significant': '✅ Yes' if trends['p_value'] < 0.05 else '❌ No',
                                    'Trend Direction': '📈 Increasing' if trends['slope'] > 0 else '📉 Decreasing'
                                })
                        
                        if trend_results:
                            trend_df = pd.DataFrame(trend_results)
                            st.dataframe(trend_df, use_container_width=True, hide_index=True)
                
                tab_idx += 1
            
            if show_seasonality:
                with tab_objects[tab_idx]:
                    st.subheader("Seasonal Decomposition")
                    
                    for dataset_name, data_handler in data_dict.items():
                        st.markdown(f"### {dataset_name}")
                        
                        seasonal_analyzer = SeasonalAnalyzer(data_handler)
                        
                        for fraction in selected_fractions:
                            st.markdown(f"#### {CLASS_LABELS[fraction]}")
                            
                            # Calculate seasonal statistics
                            seasonal_stats = seasonal_analyzer.calculate_seasonal_statistics(fraction)
                            
                            if seasonal_stats:
                                # Create seasonal decomposition plot
                                fig_seasonal = make_subplots(
                                    rows=2, cols=2,
                                    subplot_titles=['Monthly Pattern', 'Seasonal Amplitude', 
                                                  'Annual Trend', 'Seasonal Consistency']
                                )
                                
                                # Monthly pattern
                                fig_seasonal.add_trace(
                                    go.Scatter(
                                        x=list(range(1, 13)),
                                        y=[seasonal_stats['monthly_means'][i] for i in range(1, 13)],
                                        mode='lines+markers',
                                        name='Monthly Mean'
                                    ),
                                    row=1, col=1
                                )
                                
                                # Add other seasonal analysis plots here...
                                
                                fig_seasonal.update_layout(height=600, showlegend=False)
                                st.plotly_chart(fig_seasonal, use_container_width=True)
        
        # Export section
        st.header("💾 Export Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export Current Plot"):
                # This would export the currently displayed plot
                st.success("Plot export functionality would be implemented here")
        
        with col2:
            if st.button("📋 Export Statistics"):
                # Export statistical summaries
                st.success("Statistics export functionality would be implemented here")
        
        with col3:
            if st.button("💾 Export Data"):
                # Export filtered data
                st.success("Data export functionality would be implemented here")
        
        # Advanced export options
        with st.expander("🔧 Advanced Export Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Format Options:**")
                st.markdown(f"- Format: {export_format}")
                st.markdown(f"- DPI: {export_dpi}")
                st.markdown(f"- Include metadata: Yes")
            
            with col2:
                st.markdown("**Data Options:**")
                st.markdown("- Include filtered data")
                st.markdown("- Include statistical summaries")
                st.markdown("- Include analysis parameters")
    
    else:
        # Instructions if no data loaded
        st.info("""
        👈 **Getting Started:**
        
        1. **Select Datasets**: Choose MCD43A3, MOD10A1, or both
        2. **Choose Fractions**: Select ice fraction classes to analyze
        3. **Set Date Range**: Use flexible date selection options
        4. **Configure Analysis**: Choose chart type and parameters
        5. **Load Data**: Click "Load/Refresh Data" to begin
        
        This interactive explorer provides maximum flexibility for custom analyses:
        
        ### 🎯 Key Features:
        - **Flexible Date Selection**: Full range, year range, custom dates, or specific seasons
        - **Multiple Chart Types**: Time series, scatter matrix, correlations, distributions, box plots
        - **Statistical Analysis**: Descriptive stats, trend analysis, seasonal decomposition
        - **Export Capabilities**: Multiple formats with customizable options
        - **Real-time Updates**: Modify parameters and see results immediately
        
        ### 💡 Pro Tips:
        - Use seasonal analysis for climate studies
        - Compare multiple datasets with scatter matrices
        - Export high-DPI plots for publications
        - Apply quality filters for cleaner analysis
        """)
        
        # Quick start examples
        st.subheader("🚀 Quick Start Examples")
        
        example_col1, example_col2 = st.columns(2)
        
        with example_col1:
            st.markdown("""
            **🌿 Summer Analysis (2020-2024)**
            - Datasets: Both MCD43A3 & MOD10A1
            - Fractions: Pure ice, Mostly ice
            - Date Mode: Specific Seasons (Summer)
            - Chart: Time Series
            """)
        
        with example_col2:
            st.markdown("""
            **❄️ Winter Trends (Full Period)**
            - Dataset: MCD43A3
            - Fractions: All classes
            - Date Mode: Full Range
            - Chart: Correlation Heatmap
            """)