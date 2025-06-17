"""
Elevation Analysis Page
======================

Analyze albedo variations across elevation bands following Williamson & Menounos (2021) methodology.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import project modules
from config import (
    ELEVATION_CONFIG, FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS
)
from data.loader import ElevationDataLoader
from analysis.elevation_analysis import ElevationAnalyzer
from visualization.elevation_plots import ElevationPlotter as ElevationVisualizer

# Page config
st.set_page_config(
    page_title="Elevation Analysis - Saskatchewan Glacier",
    page_icon="🏔️",
    layout="wide"
)

# Title
st.title("🏔️ Elevation Analysis")
st.markdown("Analyze albedo variations across elevation bands (Williamson & Menounos 2021 methodology)")

# Initialize session state
if 'elevation_data_loaded' not in st.session_state:
    st.session_state.elevation_data_loaded = False

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Analysis Settings")
    
    # Elevation band selection
    st.subheader("🏔️ Elevation Bands")
    
    # Display available elevation zones
    elevation_zones = ELEVATION_CONFIG['elevation_zones']
    
    selected_zones = st.multiselect(
        "Select Elevation Zones",
        options=elevation_zones,
        default=elevation_zones[:2],  # Default to first 2 zones
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    # Fraction selection
    selected_fraction = st.selectbox(
        "Select Fraction Class",
        options=FRACTION_CLASSES,
        index=0,
        format_func=lambda x: CLASS_LABELS[x]
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
    
    analysis_type = st.radio(
        "Analysis Type",
        options=['Time Series', 'Seasonal', 'Trend Analysis', 'Transient Snowline'],
        index=0
    )
    
    # Time aggregation for time series
    if analysis_type == 'Time Series':
        aggregation = st.selectbox(
            "Temporal Aggregation",
            options=['Daily', 'Weekly', 'Monthly', 'Annual'],
            index=1
        )
    
    show_uncertainty = st.checkbox("Show Uncertainty Bands", value=True)
    normalize_albedo = st.checkbox("Normalize Albedo (0-1)", value=False)

# Load data function
@st.cache_data
def load_elevation_data(start_year, end_year):
    """Load elevation-based albedo data"""
    try:
        loader = ElevationDataLoader()
        data = loader.load_elevation_data()
        
        if data is None:
            return None, "Failed to load elevation data"
        
        # Filter by date range
        data = data[(data['year'] >= start_year) & (data['year'] <= end_year)]
        
        return data, None
        
    except Exception as e:
        return None, str(e)

# Main content
main_container = st.container()

with main_container:
    # Load data button
    if st.button("🔄 Load/Refresh Elevation Data", type="primary"):
        with st.spinner("Loading elevation data..."):
            data, error = load_elevation_data(start_year, end_year)
            
            if error:
                st.error(f"Error loading data: {error}")
            else:
                st.session_state.elevation_data = data
                st.session_state.elevation_data_loaded = True
                st.success("✅ Elevation data loaded successfully!")
    
    # Display analysis if data is loaded
    if st.session_state.elevation_data_loaded and hasattr(st.session_state, 'elevation_data'):
        data = st.session_state.elevation_data
        
        # Initialize analyzer
        analyzer = ElevationAnalyzer(data)
        
        # Data overview
        st.header("📊 Data Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", f"{len(data):,}")
        with col2:
            st.metric("Elevation Bands", len(bands))
        with col3:
            st.metric("Date Range", f"{data['date'].min().date()} to {data['date'].max().date()}")
        with col4:
            st.metric("Selected Fraction", CLASS_LABELS[selected_fraction])
        
        # Display analysis based on selected type
        if analysis_type == 'Time Series':
            st.header("📈 Elevation Time Series Analysis")
            
            # Aggregate data based on selection
            if aggregation == 'Daily':
                plot_data = data
                date_col = 'date'
            elif aggregation == 'Weekly':
                data['week'] = data['date'].dt.to_period('W')
                plot_data = data.groupby(['week'] + [f'band_{b}' for b in bands]).mean().reset_index()
                plot_data['date'] = plot_data['week'].dt.to_timestamp()
                date_col = 'date'
            elif aggregation == 'Monthly':
                data['month'] = data['date'].dt.to_period('M')
                plot_data = data.groupby(['month'] + [f'band_{b}' for b in bands]).mean().reset_index()
                plot_data['date'] = plot_data['month'].dt.to_timestamp()
                date_col = 'date'
            else:  # Annual
                plot_data = data.groupby(['year'] + [f'band_{b}' for b in bands]).mean().reset_index()
                date_col = 'year'
            
            # Create time series plot
            fig = go.Figure()
            
            for zone in selected_zones:
                zone_col = f"{selected_fraction}_{zone}_mean"
                if zone_col in plot_data.columns:
                    y_data = plot_data[zone_col]
                    
                    if normalize_albedo:
                        y_data = (y_data - y_data.min()) / (y_data.max() - y_data.min())
                    
                    # Add main trace
                    fig.add_trace(go.Scatter(
                        x=plot_data[date_col],
                        y=y_data,
                        mode='lines',
                        name=zone.replace('_', ' ').title(),
                        line=dict(width=2)
                    ))
                    
                    # Add uncertainty band if requested
                    if show_uncertainty and f"{selected_fraction}_{zone}_std" in plot_data.columns:
                        std_col = f"{selected_fraction}_{zone}_std"
                        upper = y_data + plot_data[std_col]
                        lower = y_data - plot_data[std_col]
                        
                        fig.add_trace(go.Scatter(
                            x=plot_data[date_col],
                            y=upper,
                            mode='lines',
                            line=dict(width=0),
                            showlegend=False,
                            hoverinfo='skip'
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=plot_data[date_col],
                            y=lower,
                            mode='lines',
                            line=dict(width=0),
                            fill='tonexty',
                            fillcolor='rgba(128,128,128,0.2)',
                            showlegend=False,
                            hoverinfo='skip'
                        ))
            
            fig.update_layout(
                title=f"Albedo Variation by Elevation - {CLASS_LABELS[selected_fraction]} ({aggregation})",
                xaxis_title="Date" if date_col == 'date' else "Year",
                yaxis_title="Albedo" + (" (Normalized)" if normalize_albedo else ""),
                height=600,
                hovermode='x unified',
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Elevation gradient analysis
            st.subheader("🏔️ Elevation Gradient")
            
            # Calculate mean albedo by elevation zone
            gradient_data = []
            for zone in elevation_zones:
                zone_col = f"{selected_fraction}_{zone}_mean"
                if zone_col in data.columns:
                    mean_albedo = data[zone_col].mean()
                    std_albedo = data[zone_col].std()
                    gradient_data.append({
                        'Elevation Zone': zone.replace('_', ' ').title(),
                        'Zone Code': zone,
                        'Mean Albedo': mean_albedo,
                        'Std Dev': std_albedo
                    })
            
            if gradient_data:
                gradient_df = pd.DataFrame(gradient_data)
                
                fig_gradient = go.Figure()
                fig_gradient.add_trace(go.Scatter(
                    x=gradient_df['Mean Elevation (m)'],
                    y=gradient_df['Mean Albedo'],
                    mode='lines+markers',
                    error_y=dict(
                        type='data',
                        array=gradient_df['Std Dev'],
                        visible=show_uncertainty
                    ),
                    marker=dict(size=10),
                    line=dict(width=2)
                ))
                
                fig_gradient.update_layout(
                    title="Mean Albedo vs Elevation",
                    xaxis_title="Elevation (m)",
                    yaxis_title="Mean Albedo",
                    height=400,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_gradient, use_container_width=True)
        
        elif analysis_type == 'Seasonal':
            st.header("🌡️ Seasonal Patterns by Elevation")
            
            # Calculate monthly means by elevation
            data['month'] = data['date'].dt.month
            
            # Create subplot for each elevation band
            n_bands = len(selected_bands)
            fig = make_subplots(
                rows=(n_bands + 1) // 2,
                cols=2,
                subplot_titles=[ELEVATION_CONFIG['bands'][b]['name'] for b in selected_bands],
                vertical_spacing=0.1
            )
            
            for idx, band in enumerate(selected_bands):
                row = idx // 2 + 1
                col = idx % 2 + 1
                
                band_col = f"{selected_fraction}_band_{band}_mean"
                if band_col in data.columns:
                    monthly_data = data.groupby('month')[band_col].agg(['mean', 'std']).reset_index()
                    
                    fig.add_trace(
                        go.Scatter(
                            x=monthly_data['month'],
                            y=monthly_data['mean'],
                            mode='lines+markers',
                            name=ELEVATION_CONFIG['bands'][band]['name'],
                            error_y=dict(
                                type='data',
                                array=monthly_data['std'],
                                visible=show_uncertainty
                            ),
                            showlegend=False
                        ),
                        row=row, col=col
                    )
                    
                    fig.update_xaxes(
                        tickmode='array',
                        tickvals=list(range(1, 13)),
                        ticktext=['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'],
                        row=row, col=col
                    )
            
            fig.update_layout(
                height=400 * ((n_bands + 1) // 2),
                title=f"Seasonal Patterns by Elevation - {CLASS_LABELS[selected_fraction]}",
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Seasonal amplitude analysis
            st.subheader("📊 Seasonal Amplitude by Elevation")
            
            amplitude_data = []
            for band in bands:
                band_col = f"{selected_fraction}_band_{band}_mean"
                if band_col in data.columns:
                    monthly_means = data.groupby('month')[band_col].mean()
                    amplitude = monthly_means.max() - monthly_means.min()
                    amplitude_data.append({
                        'Elevation Band': ELEVATION_CONFIG['bands'][band]['name'],
                        'Mean Elevation (m)': np.mean(ELEVATION_CONFIG['bands'][band]['range']),
                        'Seasonal Amplitude': amplitude,
                        'Summer Mean': monthly_means[6:9].mean(),  # Jun-Aug
                        'Winter Mean': monthly_means[[12, 1, 2]].mean()  # Dec-Feb
                    })
            
            if amplitude_data:
                amplitude_df = pd.DataFrame(amplitude_data)
                
                fig_amp = go.Figure()
                fig_amp.add_trace(go.Bar(
                    x=amplitude_df['Elevation Band'],
                    y=amplitude_df['Seasonal Amplitude'],
                    marker_color='lightblue'
                ))
                
                fig_amp.update_layout(
                    title="Seasonal Amplitude vs Elevation",
                    xaxis_title="Elevation Band",
                    yaxis_title="Seasonal Amplitude",
                    height=400,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_amp, use_container_width=True)
                
                # Display table
                st.dataframe(amplitude_df, use_container_width=True, hide_index=True)
        
        elif analysis_type == 'Trend Analysis':
            st.header("📈 Elevation-Dependent Trends")
            
            # Calculate trends for each elevation band
            trend_results = []
            
            for band in bands:
                band_col = f"{selected_fraction}_band_{band}_mean"
                if band_col in data.columns:
                    # Prepare data for trend analysis
                    band_data = data[['date', band_col]].dropna()
                    
                    if len(band_data) > 10:
                        # Simple linear regression for trend
                        from scipy import stats
                        
                        # Convert date to numeric (days since start)
                        x = (band_data['date'] - band_data['date'].min()).dt.days
                        y = band_data[band_col]
                        
                        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                        
                        # Convert to per-year trend
                        trend_per_year = slope * 365.25
                        
                        trend_results.append({
                            'Elevation Band': ELEVATION_CONFIG['bands'][band]['name'],
                            'Mean Elevation (m)': np.mean(ELEVATION_CONFIG['bands'][band]['range']),
                            'Trend (per year)': trend_per_year,
                            'P-value': p_value,
                            'R²': r_value**2,
                            'Significant': '✅' if p_value < 0.05 else '❌'
                        })
            
            if trend_results:
                trend_df = pd.DataFrame(trend_results)
                
                # Plot trends vs elevation
                fig_trends = go.Figure()
                
                # Color based on significance
                colors = ['green' if row['Significant'] == '✅' else 'gray' 
                         for _, row in trend_df.iterrows()]
                
                fig_trends.add_trace(go.Scatter(
                    x=trend_df['Mean Elevation (m)'],
                    y=trend_df['Trend (per year)'],
                    mode='lines+markers',
                    marker=dict(
                        size=12,
                        color=colors,
                        symbol=['circle' if row['Significant'] == '✅' else 'circle-open' 
                               for _, row in trend_df.iterrows()]
                    ),
                    line=dict(width=2, color='blue'),
                    text=[f"p={row['P-value']:.3f}" for _, row in trend_df.iterrows()],
                    textposition="top center"
                ))
                
                # Add zero line
                fig_trends.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
                
                fig_trends.update_layout(
                    title=f"Albedo Trends by Elevation - {CLASS_LABELS[selected_fraction]}",
                    xaxis_title="Elevation (m)",
                    yaxis_title="Trend (per year)",
                    height=500,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_trends, use_container_width=True)
                
                # Display results table
                st.subheader("📊 Trend Statistics")
                display_df = trend_df.copy()
                display_df['Trend (per year)'] = display_df['Trend (per year)'].apply(lambda x: f"{x:.5f}")
                display_df['P-value'] = display_df['P-value'].apply(lambda x: f"{x:.4f}")
                display_df['R²'] = display_df['R²'].apply(lambda x: f"{x:.3f}")
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    avg_trend = trend_df['Trend (per year)'].mean()
                    st.metric("Average Trend", f"{avg_trend:.5f}/year")
                with col2:
                    sig_count = (trend_df['Significant'] == '✅').sum()
                    st.metric("Significant Trends", f"{sig_count}/{len(trend_df)}")
                with col3:
                    if len(trend_df) > 1:
                        # Check if trend changes with elevation
                        elev_trend_corr = np.corrcoef(trend_df['Mean Elevation (m)'], 
                                                     trend_df['Trend (per year)'])[0, 1]
                        st.metric("Elevation-Trend Correlation", f"{elev_trend_corr:.3f}")
        
        elif analysis_type == 'Transient Snowline':
            st.header("🏔️ Transient Snowline Analysis")
            
            st.info("""
            The transient snowline altitude (TSL) is estimated as the elevation where albedo 
            transitions from high (snow) to low (ice/rock) values. This analysis identifies 
            the TSL for each time period based on albedo gradients.
            """)
            
            # TSL threshold
            tsl_threshold = st.slider(
                "TSL Albedo Threshold",
                min_value=0.3,
                max_value=0.7,
                value=0.5,
                step=0.05,
                help="Albedo value used to define the snow/ice transition"
            )
            
            # Calculate TSL for each date
            tsl_data = []
            
            for date in data['date'].unique():
                date_data = data[data['date'] == date]
                
                # Get albedo values for each elevation
                elev_albedo = []
                for band in bands:
                    band_col = f"{selected_fraction}_band_{band}_mean"
                    if band_col in date_data.columns:
                        mean_elev = np.mean(ELEVATION_CONFIG['bands'][band]['range'])
                        albedo_val = date_data[band_col].iloc[0] if len(date_data) > 0 else np.nan
                        if not np.isnan(albedo_val):
                            elev_albedo.append((mean_elev, albedo_val))
                
                if len(elev_albedo) >= 2:
                    elev_albedo.sort(key=lambda x: x[0])  # Sort by elevation
                    elevations = [x[0] for x in elev_albedo]
                    albedos = [x[1] for x in elev_albedo]
                    
                    # Find TSL by interpolation
                    tsl_elev = np.interp(tsl_threshold, albedos[::-1], elevations[::-1])
                    
                    # Only include if TSL is within elevation range
                    if elevations[0] <= tsl_elev <= elevations[-1]:
                        tsl_data.append({
                            'date': date,
                            'tsl_elevation': tsl_elev,
                            'year': date.year,
                            'month': date.month,
                            'doy': date.dayofyear
                        })
            
            if tsl_data:
                tsl_df = pd.DataFrame(tsl_data)
                
                # TSL time series
                fig_tsl = go.Figure()
                
                fig_tsl.add_trace(go.Scatter(
                    x=tsl_df['date'],
                    y=tsl_df['tsl_elevation'],
                    mode='markers',
                    marker=dict(
                        size=5,
                        color=tsl_df['doy'],
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title="Day of Year")
                    ),
                    name='TSL'
                ))
                
                # Add trend line
                from scipy import stats
                x_numeric = (tsl_df['date'] - tsl_df['date'].min()).dt.days
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, tsl_df['tsl_elevation'])
                trend_line = intercept + slope * x_numeric
                
                fig_tsl.add_trace(go.Scatter(
                    x=tsl_df['date'],
                    y=trend_line,
                    mode='lines',
                    name=f'Trend ({slope*365.25:.1f} m/year)',
                    line=dict(color='red', dash='dash')
                ))
                
                fig_tsl.update_layout(
                    title="Transient Snowline Altitude Time Series",
                    xaxis_title="Date",
                    yaxis_title="TSL Elevation (m)",
                    height=500,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_tsl, use_container_width=True)
                
                # Seasonal TSL pattern
                st.subheader("📅 Seasonal TSL Pattern")
                
                monthly_tsl = tsl_df.groupby('month')['tsl_elevation'].agg(['mean', 'std', 'count']).reset_index()
                
                fig_seasonal_tsl = go.Figure()
                
                fig_seasonal_tsl.add_trace(go.Scatter(
                    x=monthly_tsl['month'],
                    y=monthly_tsl['mean'],
                    mode='lines+markers',
                    error_y=dict(
                        type='data',
                        array=monthly_tsl['std'],
                        visible=True
                    ),
                    marker=dict(size=10),
                    line=dict(width=2)
                ))
                
                fig_seasonal_tsl.update_layout(
                    title="Mean Monthly TSL Elevation",
                    xaxis=dict(
                        title="Month",
                        tickmode='array',
                        tickvals=list(range(1, 13)),
                        ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    ),
                    yaxis_title="TSL Elevation (m)",
                    height=400,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_seasonal_tsl, use_container_width=True)
                
                # TSL statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Mean TSL", f"{tsl_df['tsl_elevation'].mean():.0f} m")
                with col2:
                    st.metric("TSL Range", f"{tsl_df['tsl_elevation'].max() - tsl_df['tsl_elevation'].min():.0f} m")
                with col3:
                    st.metric("TSL Trend", f"{slope*365.25:.1f} m/year")
                with col4:
                    st.metric("Trend P-value", f"{p_value:.4f}")
            
            else:
                st.warning("Insufficient data to calculate transient snowline altitude.")
    
    else:
        # Instructions if no data loaded
        st.info("""
        👈 **Getting Started:**
        1. Select elevation bands to analyze
        2. Choose a fraction class
        3. Set your date range
        4. Select analysis type
        5. Click "Load/Refresh Elevation Data" to begin
        
        This page analyzes albedo variations across elevation following the 
        Williamson & Menounos (2021) methodology, providing insights into:
        - Elevation-dependent albedo patterns
        - Seasonal variations by elevation
        - Elevation-specific trends
        - Transient snowline altitude estimation
        """)
        
        # Show elevation zone information
        st.subheader("🏔️ Available Elevation Zones")
        
        zones_info = []
        for zone in ELEVATION_CONFIG['elevation_zones']:
            zones_info.append({
                'Zone ID': zone,
                'Name': zone.replace('_', ' ').title(),
                'Description': f"Elevation zone: {zone}"
            })
        
        zones_df = pd.DataFrame(zones_info)
        st.dataframe(zones_df, use_container_width=True, hide_index=True)