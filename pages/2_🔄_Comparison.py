"""
Dataset Comparison Page
======================

Compare MCD43A3 and MOD10A1 datasets with correlation analysis and visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
import sys
from scipy import stats

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import project modules
from config import (
    FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS
)
from data.dataset_manager import DatasetManager
from analysis.comparison import DatasetComparator

# Page config
st.set_page_config(
    page_title="Dataset Comparison - Saskatchewan Glacier",
    page_icon="🔄",
    layout="wide"
)

# Title
st.title("🔄 Dataset Comparison")
st.markdown("Compare MCD43A3 and MOD10A1 datasets to understand their relationships and differences")

# Initialize session state
if 'comparison_loaded' not in st.session_state:
    st.session_state.comparison_loaded = False

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Comparison Settings")
    
    # Fraction selection
    selected_fraction = st.selectbox(
        "Select Fraction Class",
        options=FRACTION_CLASSES,
        index=0,
        format_func=lambda x: CLASS_LABELS[x],
        help="Choose which ice fraction class to compare"
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
    st.subheader("📊 Analysis Options")
    
    # Temporal alignment
    alignment_method = st.radio(
        "Temporal Alignment",
        options=['Daily Average', '16-Day Average', 'Monthly Average'],
        index=1,
        help="How to align the different temporal resolutions"
    )
    
    # Statistical options
    show_regression = st.checkbox("Show Regression Line", value=True)
    show_confidence = st.checkbox("Show Confidence Intervals", value=True)
    remove_outliers = st.checkbox("Remove Outliers (3σ)", value=False)

# Load data with caching
@st.cache_data
def load_comparison_data(start_year, end_year):
    """Load both datasets and prepare for comparison"""
    try:
        manager = DatasetManager()
        
        # Load both datasets
        mcd43a3 = manager.load_mcd43a3()
        mod10a1 = manager.load_mod10a1()
        
        if mcd43a3 is None or mod10a1 is None:
            return None, None, "Failed to load one or both datasets"
        
        # Filter by date range
        mcd43a3.data = mcd43a3.data[
            (mcd43a3.data['year'] >= start_year) & 
            (mcd43a3.data['year'] <= end_year)
        ]
        mod10a1.data = mod10a1.data[
            (mod10a1.data['year'] >= start_year) & 
            (mod10a1.data['year'] <= end_year)
        ]
        
        return mcd43a3, mod10a1, None
        
    except Exception as e:
        return None, None, str(e)

# Main content
main_container = st.container()

with main_container:
    # Load data button
    if st.button("🔄 Load/Refresh Comparison Data", type="primary"):
        with st.spinner("Loading datasets for comparison..."):
            mcd43a3, mod10a1, error = load_comparison_data(start_year, end_year)
            
            if error:
                st.error(f"Error loading data: {error}")
            else:
                st.session_state.mcd43a3 = mcd43a3
                st.session_state.mod10a1 = mod10a1
                st.session_state.comparison_loaded = True
                st.success("✅ Both datasets loaded successfully!")
    
    # Display comparison if data is loaded
    if st.session_state.comparison_loaded:
        mcd43a3 = st.session_state.mcd43a3
        mod10a1 = st.session_state.mod10a1
        
        # Initialize comparator
        comparator = DatasetComparator(mcd43a3, mod10a1)
        
        # Overview metrics
        st.header("📊 Dataset Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("MCD43A3 Records", f"{len(mcd43a3.data):,}")
        with col2:
            st.metric("MOD10A1 Records", f"{len(mod10a1.data):,}")
        with col3:
            st.metric("Date Overlap", 
                     f"{max(mcd43a3.data['date'].min(), mod10a1.data['date'].min()).date()} to "
                     f"{min(mcd43a3.data['date'].max(), mod10a1.data['date'].max()).date()}")
        with col4:
            st.metric("Selected Fraction", CLASS_LABELS[selected_fraction])
        
        # Create tabs for different analyses
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Time Series Comparison", 
            "Correlation Analysis", 
            "Difference Analysis",
            "Seasonal Comparison",
            "Statistical Summary"
        ])
        
        with tab1:
            st.subheader("Time Series Comparison")
            
            # Align datasets based on selected method
            with st.spinner(f"Aligning datasets using {alignment_method}..."):
                if alignment_method == 'Daily Average':
                    aligned_data = comparator.align_daily(selected_fraction)
                elif alignment_method == '16-Day Average':
                    aligned_data = comparator.align_16day(selected_fraction)
                else:  # Monthly Average
                    aligned_data = comparator.align_monthly(selected_fraction)
            
            if aligned_data is not None and len(aligned_data) > 0:
                # Remove outliers if requested
                if remove_outliers:
                    mean_mcd = aligned_data['mcd43a3'].mean()
                    std_mcd = aligned_data['mcd43a3'].std()
                    mean_mod = aligned_data['mod10a1'].mean()
                    std_mod = aligned_data['mod10a1'].std()
                    
                    mask = (
                        (aligned_data['mcd43a3'] >= mean_mcd - 3*std_mcd) & 
                        (aligned_data['mcd43a3'] <= mean_mcd + 3*std_mcd) &
                        (aligned_data['mod10a1'] >= mean_mod - 3*std_mod) & 
                        (aligned_data['mod10a1'] <= mean_mod + 3*std_mod)
                    )
                    aligned_data = aligned_data[mask]
                
                # Create comparison plot
                fig = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.1,
                    subplot_titles=('Albedo Time Series', 'Difference (MCD43A3 - MOD10A1)'),
                    row_heights=[0.7, 0.3]
                )
                
                # Add MCD43A3 trace
                fig.add_trace(
                    go.Scatter(
                        x=aligned_data['date'],
                        y=aligned_data['mcd43a3'],
                        mode='lines',
                        name='MCD43A3',
                        line=dict(color='blue', width=2),
                        opacity=0.8
                    ),
                    row=1, col=1
                )
                
                # Add MOD10A1 trace
                fig.add_trace(
                    go.Scatter(
                        x=aligned_data['date'],
                        y=aligned_data['mod10a1'],
                        mode='lines',
                        name='MOD10A1',
                        line=dict(color='red', width=2),
                        opacity=0.8
                    ),
                    row=1, col=1
                )
                
                # Calculate and plot difference
                difference = aligned_data['mcd43a3'] - aligned_data['mod10a1']
                
                fig.add_trace(
                    go.Scatter(
                        x=aligned_data['date'],
                        y=difference,
                        mode='lines',
                        name='Difference',
                        line=dict(color='green', width=1.5),
                        fill='tozeroy',
                        fillcolor='rgba(0,255,0,0.1)'
                    ),
                    row=2, col=1
                )
                
                # Add zero line for difference plot
                fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
                
                # Update layout
                fig.update_xaxes(title_text="Date", row=2, col=1)
                fig.update_yaxes(title_text="Albedo", row=1, col=1)
                fig.update_yaxes(title_text="Difference", row=2, col=1)
                
                fig.update_layout(
                    height=600,
                    title=f"Time Series Comparison - {CLASS_LABELS[selected_fraction]}",
                    hovermode='x unified',
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Summary statistics for difference
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Mean Difference", f"{difference.mean():.4f}")
                with col2:
                    st.metric("Std Dev of Difference", f"{difference.std():.4f}")
                with col3:
                    st.metric("RMSE", f"{np.sqrt((difference**2).mean()):.4f}")
            
            else:
                st.warning("No overlapping data found for the selected parameters.")
        
        with tab2:
            st.subheader("Correlation Analysis")
            
            # Get aligned data for correlation
            aligned_data = comparator.align_16day(selected_fraction)
            
            if aligned_data is not None and len(aligned_data) > 10:
                # Remove NaN values
                clean_data = aligned_data[['mcd43a3', 'mod10a1']].dropna()
                
                if len(clean_data) > 10:
                    # Calculate correlation
                    corr_coef, p_value = stats.pearsonr(clean_data['mcd43a3'], clean_data['mod10a1'])
                    
                    # Create scatter plot
                    fig_scatter = go.Figure()
                    
                    # Add scatter points
                    fig_scatter.add_trace(go.Scatter(
                        x=clean_data['mcd43a3'],
                        y=clean_data['mod10a1'],
                        mode='markers',
                        name='Data points',
                        marker=dict(
                            size=8,
                            color=clean_data.index,
                            colorscale='Viridis',
                            showscale=True,
                            colorbar=dict(title="Time Index")
                        )
                    ))
                    
                    # Add regression line if requested
                    if show_regression:
                        # Calculate regression
                        slope, intercept, r_value, p_value_reg, std_err = stats.linregress(
                            clean_data['mcd43a3'], clean_data['mod10a1']
                        )
                        
                        # Create regression line
                        x_range = np.linspace(clean_data['mcd43a3'].min(), clean_data['mcd43a3'].max(), 100)
                        y_pred = slope * x_range + intercept
                        
                        fig_scatter.add_trace(go.Scatter(
                            x=x_range,
                            y=y_pred,
                            mode='lines',
                            name=f'Regression (R²={r_value**2:.3f})',
                            line=dict(color='red', width=2, dash='dash')
                        ))
                        
                        # Add confidence interval if requested
                        if show_confidence:
                            # Calculate confidence interval
                            predict_se = std_err * np.sqrt(1/len(clean_data) + 
                                                         (x_range - clean_data['mcd43a3'].mean())**2 / 
                                                         ((clean_data['mcd43a3']**2).sum() - 
                                                          len(clean_data) * clean_data['mcd43a3'].mean()**2))
                            margin = 1.96 * predict_se
                            
                            fig_scatter.add_trace(go.Scatter(
                                x=x_range,
                                y=y_pred + margin,
                                mode='lines',
                                line=dict(width=0),
                                showlegend=False,
                                hoverinfo='skip'
                            ))
                            
                            fig_scatter.add_trace(go.Scatter(
                                x=x_range,
                                y=y_pred - margin,
                                mode='lines',
                                line=dict(width=0),
                                fill='tonexty',
                                fillcolor='rgba(255,0,0,0.1)',
                                name='95% CI',
                                hoverinfo='skip'
                            ))
                    
                    # Add 1:1 line
                    min_val = min(clean_data['mcd43a3'].min(), clean_data['mod10a1'].min())
                    max_val = max(clean_data['mcd43a3'].max(), clean_data['mod10a1'].max())
                    fig_scatter.add_trace(go.Scatter(
                        x=[min_val, max_val],
                        y=[min_val, max_val],
                        mode='lines',
                        name='1:1 Line',
                        line=dict(color='gray', width=1, dash='dot')
                    ))
                    
                    fig_scatter.update_layout(
                        title=f"Correlation Analysis - {CLASS_LABELS[selected_fraction]}",
                        xaxis_title="MCD43A3 Albedo",
                        yaxis_title="MOD10A1 Albedo",
                        height=500,
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig_scatter, use_container_width=True)
                    
                    # Display correlation statistics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Pearson Correlation", f"{corr_coef:.3f}")
                    with col2:
                        st.metric("P-value", f"{p_value:.4f}")
                    with col3:
                        st.metric("R²", f"{corr_coef**2:.3f}")
                    with col4:
                        st.metric("Sample Size", len(clean_data))
                    
                    # Additional statistics
                    if show_regression:
                        st.markdown("### Regression Statistics")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Slope", f"{slope:.3f}")
                        with col2:
                            st.metric("Intercept", f"{intercept:.3f}")
                        with col3:
                            st.metric("Standard Error", f"{std_err:.4f}")
                else:
                    st.warning("Insufficient data points for correlation analysis.")
            else:
                st.warning("No overlapping data found for correlation analysis.")
        
        with tab3:
            st.subheader("Difference Analysis")
            
            # Get aligned data
            aligned_data = comparator.align_16day(selected_fraction)
            
            if aligned_data is not None and len(aligned_data) > 0:
                # Calculate differences
                aligned_data['difference'] = aligned_data['mcd43a3'] - aligned_data['mod10a1']
                aligned_data['abs_difference'] = aligned_data['difference'].abs()
                aligned_data['percent_difference'] = (aligned_data['difference'] / 
                                                     ((aligned_data['mcd43a3'] + aligned_data['mod10a1']) / 2) * 100)
                
                # Create difference distribution plot
                fig_dist = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('Difference Distribution', 'Difference vs Time',
                                  'Absolute Difference vs MCD43A3', 'Monthly Average Difference')
                )
                
                # Histogram of differences
                fig_dist.add_trace(
                    go.Histogram(
                        x=aligned_data['difference'],
                        name='Difference',
                        nbinsx=50,
                        marker_color='lightblue'
                    ),
                    row=1, col=1
                )
                
                # Time series of differences
                fig_dist.add_trace(
                    go.Scatter(
                        x=aligned_data['date'],
                        y=aligned_data['difference'],
                        mode='lines',
                        name='Difference',
                        line=dict(color='orange')
                    ),
                    row=1, col=2
                )
                
                # Scatter of absolute difference vs MCD43A3
                fig_dist.add_trace(
                    go.Scatter(
                        x=aligned_data['mcd43a3'],
                        y=aligned_data['abs_difference'],
                        mode='markers',
                        name='Abs Difference',
                        marker=dict(size=5, color='green', opacity=0.5)
                    ),
                    row=2, col=1
                )
                
                # Monthly average differences
                monthly_diff = aligned_data.groupby(aligned_data['date'].dt.month)['difference'].agg(['mean', 'std'])
                
                fig_dist.add_trace(
                    go.Bar(
                        x=list(range(1, 13)),
                        y=monthly_diff['mean'],
                        name='Monthly Avg',
                        error_y=dict(type='data', array=monthly_diff['std']),
                        marker_color='purple'
                    ),
                    row=2, col=2
                )
                
                # Update layouts
                fig_dist.update_xaxes(title_text="Difference", row=1, col=1)
                fig_dist.update_xaxes(title_text="Date", row=1, col=2)
                fig_dist.update_xaxes(title_text="MCD43A3 Albedo", row=2, col=1)
                fig_dist.update_xaxes(title_text="Month", row=2, col=2)
                fig_dist.update_yaxes(title_text="Count", row=1, col=1)
                fig_dist.update_yaxes(title_text="Difference", row=1, col=2)
                fig_dist.update_yaxes(title_text="Abs Difference", row=2, col=1)
                fig_dist.update_yaxes(title_text="Avg Difference", row=2, col=2)
                
                fig_dist.update_layout(height=800, showlegend=False, template="plotly_white")
                
                st.plotly_chart(fig_dist, use_container_width=True)
                
                # Summary statistics
                st.markdown("### Difference Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Mean Difference", f"{aligned_data['difference'].mean():.4f}")
                with col2:
                    st.metric("Median Difference", f"{aligned_data['difference'].median():.4f}")
                with col3:
                    st.metric("Max Absolute Difference", f"{aligned_data['abs_difference'].max():.4f}")
                with col4:
                    st.metric("Mean Absolute Difference", f"{aligned_data['abs_difference'].mean():.4f}")
            
            else:
                st.warning("No data available for difference analysis.")
        
        with tab4:
            st.subheader("Seasonal Comparison")
            
            # Prepare seasonal data
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### MCD43A3 Seasonal Pattern")
                seasonal_mcd = comparator.calculate_seasonal_patterns('MCD43A3', selected_fraction)
                
                if seasonal_mcd is not None:
                    fig_mcd = go.Figure()
                    fig_mcd.add_trace(go.Scatter(
                        x=list(range(1, 13)),
                        y=seasonal_mcd['mean'],
                        mode='lines+markers',
                        name='MCD43A3',
                        line=dict(color='blue', width=2),
                        error_y=dict(type='data', array=seasonal_mcd['std'], visible=True)
                    ))
                    
                    fig_mcd.update_layout(
                        xaxis=dict(
                            tickmode='array',
                            tickvals=list(range(1, 13)),
                            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                        ),
                        yaxis_title="Average Albedo",
                        height=350,
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig_mcd, use_container_width=True)
            
            with col2:
                st.markdown("### MOD10A1 Seasonal Pattern")
                seasonal_mod = comparator.calculate_seasonal_patterns('MOD10A1', selected_fraction)
                
                if seasonal_mod is not None:
                    fig_mod = go.Figure()
                    fig_mod.add_trace(go.Scatter(
                        x=list(range(1, 13)),
                        y=seasonal_mod['mean'],
                        mode='lines+markers',
                        name='MOD10A1',
                        line=dict(color='red', width=2),
                        error_y=dict(type='data', array=seasonal_mod['std'], visible=True)
                    ))
                    
                    fig_mod.update_layout(
                        xaxis=dict(
                            tickmode='array',
                            tickvals=list(range(1, 13)),
                            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                        ),
                        yaxis_title="Average Albedo",
                        height=350,
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig_mod, use_container_width=True)
            
            # Combined seasonal comparison
            st.markdown("### Combined Seasonal Patterns")
            
            if seasonal_mcd is not None and seasonal_mod is not None:
                fig_combined = go.Figure()
                
                # MCD43A3
                fig_combined.add_trace(go.Scatter(
                    x=list(range(1, 13)),
                    y=seasonal_mcd['mean'],
                    mode='lines+markers',
                    name='MCD43A3',
                    line=dict(color='blue', width=2),
                    error_y=dict(type='data', array=seasonal_mcd['std'], visible=show_confidence)
                ))
                
                # MOD10A1
                fig_combined.add_trace(go.Scatter(
                    x=list(range(1, 13)),
                    y=seasonal_mod['mean'],
                    mode='lines+markers',
                    name='MOD10A1',
                    line=dict(color='red', width=2),
                    error_y=dict(type='data', array=seasonal_mod['std'], visible=show_confidence)
                ))
                
                fig_combined.update_layout(
                    title=f"Seasonal Pattern Comparison - {CLASS_LABELS[selected_fraction]}",
                    xaxis=dict(
                        title="Month",
                        tickmode='array',
                        tickvals=list(range(1, 13)),
                        ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    ),
                    yaxis_title="Average Albedo",
                    height=400,
                    hovermode='x unified',
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_combined, use_container_width=True)
        
        with tab5:
            st.subheader("Statistical Summary")
            
            # Calculate comprehensive statistics for both datasets
            stats_comparison = comparator.calculate_comparison_statistics(selected_fraction)
            
            if stats_comparison is not None:
                # Create comparison table
                st.markdown("### Statistical Comparison")
                
                stats_df = pd.DataFrame({
                    'Statistic': ['Mean', 'Median', 'Std Dev', 'Min', 'Max', 'Skewness', 'Kurtosis'],
                    'MCD43A3': [
                        f"{stats_comparison['mcd43a3']['mean']:.4f}",
                        f"{stats_comparison['mcd43a3']['median']:.4f}",
                        f"{stats_comparison['mcd43a3']['std']:.4f}",
                        f"{stats_comparison['mcd43a3']['min']:.4f}",
                        f"{stats_comparison['mcd43a3']['max']:.4f}",
                        f"{stats_comparison['mcd43a3']['skewness']:.3f}",
                        f"{stats_comparison['mcd43a3']['kurtosis']:.3f}"
                    ],
                    'MOD10A1': [
                        f"{stats_comparison['mod10a1']['mean']:.4f}",
                        f"{stats_comparison['mod10a1']['median']:.4f}",
                        f"{stats_comparison['mod10a1']['std']:.4f}",
                        f"{stats_comparison['mod10a1']['min']:.4f}",
                        f"{stats_comparison['mod10a1']['max']:.4f}",
                        f"{stats_comparison['mod10a1']['skewness']:.3f}",
                        f"{stats_comparison['mod10a1']['kurtosis']:.3f}"
                    ],
                    'Difference': [
                        f"{stats_comparison['mcd43a3']['mean'] - stats_comparison['mod10a1']['mean']:.4f}",
                        f"{stats_comparison['mcd43a3']['median'] - stats_comparison['mod10a1']['median']:.4f}",
                        f"{stats_comparison['mcd43a3']['std'] - stats_comparison['mod10a1']['std']:.4f}",
                        "-",
                        "-",
                        "-",
                        "-"
                    ]
                })
                
                st.dataframe(stats_df, use_container_width=True, hide_index=True)
                
                # Trend comparison
                st.markdown("### Trend Comparison")
                
                trends_df = pd.DataFrame({
                    'Dataset': ['MCD43A3', 'MOD10A1'],
                    'Trend (per year)': [
                        f"{stats_comparison['mcd43a3']['trend']:.5f}",
                        f"{stats_comparison['mod10a1']['trend']:.5f}"
                    ],
                    'P-value': [
                        f"{stats_comparison['mcd43a3']['trend_pvalue']:.4f}",
                        f"{stats_comparison['mod10a1']['trend_pvalue']:.4f}"
                    ],
                    'Significant': [
                        '✅ Yes' if stats_comparison['mcd43a3']['trend_pvalue'] < 0.05 else '❌ No',
                        '✅ Yes' if stats_comparison['mod10a1']['trend_pvalue'] < 0.05 else '❌ No'
                    ]
                })
                
                st.dataframe(trends_df, use_container_width=True, hide_index=True)
                
                # Box plot comparison
                st.markdown("### Distribution Comparison")
                
                fig_box = go.Figure()
                
                # Add box plots for both datasets
                fig_box.add_trace(go.Box(
                    y=stats_comparison['mcd43a3']['data'],
                    name='MCD43A3',
                    marker_color='blue'
                ))
                
                fig_box.add_trace(go.Box(
                    y=stats_comparison['mod10a1']['data'],
                    name='MOD10A1',
                    marker_color='red'
                ))
                
                fig_box.update_layout(
                    title=f"Albedo Distribution Comparison - {CLASS_LABELS[selected_fraction]}",
                    yaxis_title="Albedo",
                    height=400,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_box, use_container_width=True)
            
            else:
                st.warning("Unable to calculate comparison statistics.")
    
    else:
        # Instructions if no data loaded
        st.info("""
        👈 **Getting Started:**
        1. Select a fraction class to compare
        2. Choose your date range
        3. Configure analysis options
        4. Click "Load/Refresh Comparison Data" to begin
        
        This page will compare MCD43A3 and MOD10A1 datasets across multiple dimensions:
        - Time series alignment and differences
        - Correlation and regression analysis
        - Seasonal pattern comparison
        - Statistical summaries
        """)