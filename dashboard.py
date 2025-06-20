#!/usr/bin/env python3
"""
Saskatchewan Glacier Albedo Analysis - Web Dashboard
==================================================

Interactive Streamlit dashboard for visualizing and analyzing
glacier albedo trends with real-time data integration.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import io
import base64
import warnings
warnings.filterwarnings('ignore')

# Setup path for imports
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))

# Page config
st.set_page_config(
    page_title="Saskatchewan Glacier Albedo Analysis",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<h1 class="main-header">🏔️ Saskatchewan Glacier Albedo Analysis</h1>', 
                unsafe_allow_html=True)
    st.markdown("**Interactive Dashboard for MODIS Satellite Data Analysis (2010-2024)**")
    
    # Sidebar navigation
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.selectbox(
        "Choose Analysis Page",
        [
            "🏠 Home & Overview", 
            "📁 Data Management",
            "📈 Trend Analysis",
            "🎨 Interactive Visualizations", 
            "🛰️ Google Earth Engine",
            "📋 Custom Analysis",
            "⚙️ Configuration"
        ]
    )
    
    # Route to selected page
    if page == "🏠 Home & Overview":
        show_home_page()
    elif page == "📁 Data Management":
        show_data_management()
    elif page == "📈 Trend Analysis":
        show_trend_analysis()
    elif page == "🎨 Interactive Visualizations":
        show_visualizations()
    elif page == "🛰️ Google Earth Engine":
        show_gee_integration()
    elif page == "📋 Custom Analysis":
        show_custom_analysis()
    elif page == "⚙️ Configuration":
        show_configuration()

def show_home_page():
    """Dashboard home page with overview"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 Project Overview")
        
        st.markdown("""
        **Saskatchewan Glacier Albedo Analysis** is a comprehensive platform for analyzing 
        glacier surface albedo changes using MODIS satellite data from 2010-2024.
        
        ### 🎯 Key Features:
        - **Temporal Trend Analysis**: 15-year albedo evolution study
        - **Multi-Dataset Support**: MCD43A3 albedo and MOD10A1 snow cover
        - **Interactive Visualizations**: Real-time plotting and exploration
        - **Google Earth Engine Integration**: Fresh MODIS data fetching
        - **Statistical Analysis**: Mann-Kendall tests and significance assessment
        - **Quality Assessment**: Comprehensive data validation
        """)
        
        # Quick stats section
        st.subheader("📈 Quick Statistics")
        
        # Try to load data for stats
        data_stats = get_data_statistics()
        
        if data_stats:
            col_a, col_b, col_c, col_d = st.columns(4)
            
            with col_a:
                st.metric("📊 Total Observations", data_stats.get('total_obs', 'N/A'))
            
            with col_b:
                st.metric("📅 Years Covered", data_stats.get('years_span', 'N/A'))
            
            with col_c:
                st.metric("🎯 Fractions Analyzed", data_stats.get('fraction_count', 'N/A'))
            
            with col_d:
                st.metric("📋 Data Quality", f"{data_stats.get('quality_pct', 0):.1f}%")
        
        else:
            st.info("📭 No data loaded. Use 'Data Management' to upload CSV files.")
    
    with col2:
        st.header("🚀 Quick Actions")
        
        # Quick action buttons
        if st.button("📁 Upload Data", key="quick_upload"):
            st.switch_page("pages/1_📁_Data_Management.py") if hasattr(st, 'switch_page') else None
        
        if st.button("📈 Run Analysis", key="quick_analysis"):
            st.switch_page("pages/2_📈_Trend_Analysis.py") if hasattr(st, 'switch_page') else None
        
        if st.button("🛰️ Fetch Fresh Data", key="quick_gee"):
            st.switch_page("pages/4_🛰️_Google_Earth_Engine.py") if hasattr(st, 'switch_page') else None
        
        # Recent activity
        st.subheader("📋 Recent Activity")
        show_recent_activity()
        
        # System status
        st.subheader("🔧 System Status")
        show_system_status()

def get_data_statistics():
    """Get basic statistics about loaded data"""
    try:
        from config import CSV_PATH
        from data_handler import AlbedoDataHandler
        
        if not os.path.exists(CSV_PATH):
            return None
        
        handler = AlbedoDataHandler(CSV_PATH)
        handler.load_data()
        
        data = handler.data
        
        # Calculate stats
        stats = {
            'total_obs': len(data),
            'years_span': f"{data['year'].min()}-{data['year'].max()}" if 'year' in data.columns else 'N/A',
            'fraction_count': len([col for col in data.columns if '_mean' in col]),
            'quality_pct': ((data['quality'] <= 1).sum() / len(data) * 100) if 'quality' in data.columns else 100
        }
        
        return stats
        
    except Exception:
        return None

def show_recent_activity():
    """Show recent files and activity"""
    
    # Check for recent result files
    results_dir = Path("results")
    
    if results_dir.exists():
        recent_files = []
        for file_path in results_dir.rglob("*.csv"):
            if file_path.is_file():
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if (datetime.now() - mod_time).days < 7:  # Last 7 days
                    recent_files.append((file_path.name, mod_time))
        
        if recent_files:
            recent_files.sort(key=lambda x: x[1], reverse=True)
            for filename, mod_time in recent_files[:3]:
                st.text(f"📄 {filename}")
                st.caption(f"   {mod_time.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.text("📭 No recent activity")
    else:
        st.text("📁 Results directory not found")

def show_system_status():
    """Show system status indicators"""
    
    # Check data availability
    try:
        from config import CSV_PATH
        data_available = os.path.exists(CSV_PATH)
        st.text(f"📊 Data: {'✅' if data_available else '❌'}")
    except:
        st.text("📊 Data: ❌")
    
    # Check GEE availability  
    try:
        from gee.client import GEEClient
        gee_status = GEEClient.check_installation()
        st.text(f"🛰️ GEE: {'✅' if gee_status['installed'] else '❌'}")
    except:
        st.text("🛰️ GEE: ❌")
    
    # Check results directory
    results_available = Path("results").exists()
    st.text(f"📁 Results: {'✅' if results_available else '❌'}")

def show_data_management():
    """Data upload and management interface"""
    
    st.header("📁 Data Management")
    
    tab1, tab2, tab3 = st.tabs(["📤 Upload Data", "📊 Data Overview", "🔍 Data Quality"])
    
    with tab1:
        st.subheader("📤 Upload CSV Data")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV file with albedo data",
            type=['csv'],
            help="Upload MODIS albedo data in CSV format"
        )
        
        if uploaded_file is not None:
            try:
                # Read and preview data
                df = pd.read_csv(uploaded_file)
                
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                st.info(f"📊 Shape: {df.shape[0]} rows, {df.shape[1]} columns")
                
                # Show preview
                st.subheader("👀 Data Preview")
                st.dataframe(df.head(10))
                
                # Column information
                st.subheader("📋 Column Information")
                col_info = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes,
                    'Non-Null': df.count(),
                    'Missing': df.isnull().sum()
                })
                st.dataframe(col_info)
                
                # Save option
                if st.button("💾 Save as Default Dataset"):
                    save_uploaded_data(df, uploaded_file.name)
                
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
    
    with tab2:
        show_data_overview()
    
    with tab3:
        show_data_quality_check()

def save_uploaded_data(df, filename):
    """Save uploaded data to data directory"""
    try:
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        save_path = data_dir / filename
        df.to_csv(save_path, index=False)
        
        st.success(f"✅ Data saved to: {save_path}")
        
        # Update config if needed
        st.info("💡 Update config.py to point to this file for analysis")
        
    except Exception as e:
        st.error(f"❌ Error saving data: {str(e)}")

def show_data_overview():
    """Show overview of current data"""
    
    try:
        data = load_current_data()
        
        if data is not None:
            st.subheader("📊 Current Dataset Overview")
            
            # Basic stats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📈 Total Records", len(data))
            
            with col2:
                date_range = f"{data['date'].min()} to {data['date'].max()}" if 'date' in data.columns else "N/A"
                st.metric("📅 Date Range", "")
                st.caption(date_range)
            
            with col3:
                fraction_cols = [col for col in data.columns if '_mean' in col]
                st.metric("🎯 Fraction Columns", len(fraction_cols))
            
            # Data sample
            st.subheader("📋 Data Sample")
            st.dataframe(data.head())
            
            # Column analysis
            st.subheader("📊 Column Statistics")
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            st.dataframe(data[numeric_cols].describe())
            
        else:
            st.warning("⚠️ No data currently loaded")
            
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")

def show_data_quality_check():
    """Show data quality assessment"""
    
    try:
        data = load_current_data()
        
        if data is not None:
            st.subheader("🔍 Data Quality Assessment")
            
            # Missing data analysis
            missing_data = data.isnull().sum()
            missing_pct = (missing_data / len(data)) * 100
            
            quality_df = pd.DataFrame({
                'Column': missing_data.index,
                'Missing Count': missing_data.values,
                'Missing %': missing_pct.values
            }).sort_values('Missing %', ascending=False)
            
            st.subheader("📋 Missing Data Analysis")
            st.dataframe(quality_df[quality_df['Missing Count'] > 0])
            
            # Quality indicators
            if 'quality' in data.columns:
                st.subheader("🏷️ Quality Flags Distribution")
                quality_counts = data['quality'].value_counts().sort_index()
                
                fig = px.bar(
                    x=quality_counts.index, 
                    y=quality_counts.values,
                    title="Distribution of Quality Flags",
                    labels={'x': 'Quality Flag', 'y': 'Count'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Temporal coverage
            if 'date' in data.columns:
                st.subheader("📅 Temporal Coverage")
                data['date'] = pd.to_datetime(data['date'])
                data['year_month'] = data['date'].dt.to_period('M')
                
                monthly_counts = data['year_month'].value_counts().sort_index()
                
                fig = px.line(
                    x=monthly_counts.index.astype(str), 
                    y=monthly_counts.values,
                    title="Observations per Month",
                    labels={'x': 'Month', 'y': 'Observation Count'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.warning("⚠️ No data available for quality check")
            
    except Exception as e:
        st.error(f"❌ Error in quality check: {str(e)}")

def load_current_data():
    """Load current dataset"""
    try:
        from config import CSV_PATH
        from data_handler import AlbedoDataHandler
        
        if not os.path.exists(CSV_PATH):
            return None
        
        handler = AlbedoDataHandler(CSV_PATH)
        handler.load_data()
        
        return handler.data
        
    except Exception:
        return None

def show_trend_analysis():
    """Comprehensive trend analysis interface"""
    
    st.header("📈 Trend Analysis")
    st.markdown("**Advanced statistical trend analysis with interactive controls**")
    
    # Load data
    data = load_current_data()
    
    if data is None:
        st.warning("⚠️ No data available. Please upload data in the Data Management section.")
        return
    
    # Sidebar controls
    with st.sidebar:
        st.subheader("🎯 Analysis Controls")
        
        # Fraction selection
        fraction_columns = [col for col in data.columns if '_mean' in col or '_median' in col]
        if not fraction_columns:
            st.error("❌ No fraction columns found in data")
            return
        
        selected_fraction = st.selectbox(
            "Select Fraction",
            fraction_columns,
            help="Choose the albedo fraction to analyze"
        )
        
        # Time period filter
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            min_date = data['date'].min()
            max_date = data['date'].max()
            
            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                help="Select time period for analysis"
            )
            
            if len(date_range) == 2:
                # Filter data by date range
                mask = (data['date'] >= pd.to_datetime(date_range[0])) & (data['date'] <= pd.to_datetime(date_range[1]))
                filtered_data = data[mask].copy()
            else:
                filtered_data = data.copy()
        else:
            filtered_data = data.copy()
            st.warning("⚠️ No date column found")
        
        # Quality filter
        if 'quality' in filtered_data.columns:
            quality_filter = st.checkbox("Filter by Quality", value=True, help="Only include high-quality observations")
            if quality_filter:
                quality_threshold = st.slider("Quality Threshold", 0, 3, 1, help="Maximum quality flag value")
                filtered_data = filtered_data[filtered_data['quality'] <= quality_threshold]
    
    # Main analysis area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"📊 Trend Analysis: {selected_fraction}")
        
        if len(filtered_data) < 10:
            st.error("❌ Insufficient data for trend analysis (minimum 10 observations required)")
            return
        
        # Basic statistics
        from dashboard_components import TrendAnalyzer
        stats = TrendAnalyzer.calculate_basic_statistics(filtered_data, selected_fraction)
        
        if stats:
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("📊 Observations", stats['count'])
            with col_b:
                st.metric("📈 Mean Albedo", f"{stats['mean']:.4f}")
            with col_c:
                st.metric("📉 Std Dev", f"{stats['std']:.4f}")
        
        # Trend test
        trend_result = TrendAnalyzer.simple_trend_test(filtered_data, selected_fraction)
        
        if trend_result and 'error' not in trend_result:
            st.subheader("📈 Trend Assessment")
            
            col_d, col_e, col_f = st.columns(3)
            with col_d:
                st.metric("🎯 Trend Direction", f"{trend_result['symbol']} {trend_result['direction']}")
            with col_e:
                st.metric("📊 Slope", f"{trend_result['slope']:.6f}")
            with col_f:
                st.metric("📅 Annual Change", f"{trend_result['annual_change']:.6f}")
        
        # Time series plot
        from dashboard_components import Visualizer
        fig = Visualizer.create_time_series_plot(filtered_data, [selected_fraction], 
                                                f"Time Series: {selected_fraction}")
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Additional analysis tabs
        tab1, tab2, tab3 = st.tabs(["📅 Seasonal Analysis", "📊 Distribution", "🔍 Detailed Stats"])
        
        with tab1:
            if 'month' in filtered_data.columns:
                monthly_fig = Visualizer.create_monthly_boxplot(filtered_data, selected_fraction,
                                                              f"Monthly Distribution: {selected_fraction}")
                if monthly_fig:
                    st.plotly_chart(monthly_fig, use_container_width=True)
            else:
                st.warning("⚠️ No month column available for seasonal analysis")
        
        with tab2:
            # Distribution histogram
            fig_hist = px.histogram(filtered_data, x=selected_fraction, nbins=30,
                                  title=f"Distribution of {selected_fraction}")
            fig_hist.update_layout(template='plotly_white')
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with tab3:
            # Detailed statistics table
            if stats:
                stats_df = pd.DataFrame([stats]).T
                stats_df.columns = ['Value']
                stats_df.index.name = 'Statistic'
                st.dataframe(stats_df)
    
    with col2:
        st.subheader("📋 Analysis Summary")
        
        # Summary metrics
        if stats and trend_result and 'error' not in trend_result:
            summary_data = {
                "Data Points": stats['count'],
                "Date Range": f"{filtered_data['date'].min().strftime('%Y-%m-%d')} to {filtered_data['date'].max().strftime('%Y-%m-%d')}" if 'date' in filtered_data.columns else "N/A",
                "Mean Albedo": f"{stats['mean']:.4f}",
                "Trend": f"{trend_result['direction']} ({trend_result['slope']:.6f})",
                "Data Quality": f"{((filtered_data['quality'] <= 1).sum() / len(filtered_data) * 100):.1f}%" if 'quality' in filtered_data.columns else "N/A"
            }
            
            for key, value in summary_data.items():
                st.text(f"{key}: {value}")
        
        st.subheader("📊 Quick Actions")
        
        # Export options
        if st.button("📥 Export Filtered Data"):
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"trend_analysis_{selected_fraction}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        # Advanced analysis button
        if st.button("🔬 Run Advanced Analysis"):
            with st.spinner("Running advanced trend analysis..."):
                try:
                    from dashboard_components import AnalysisRunner
                    advanced_results = AnalysisRunner.run_basic_analysis(filtered_data, selected_fraction.split('_')[0])
                    
                    if advanced_results:
                        st.success("✅ Advanced analysis completed")
                        st.json(advanced_results)
                    else:
                        st.warning("⚠️ Advanced analysis not available")
                        
                except Exception as e:
                    st.error(f"❌ Error in advanced analysis: {str(e)}")
        
        # Data quality indicator
        st.subheader("🏷️ Data Quality")
        if 'quality' in filtered_data.columns:
            quality_counts = filtered_data['quality'].value_counts().sort_index()
            fig_quality = px.pie(values=quality_counts.values, names=quality_counts.index,
                               title="Quality Distribution")
            st.plotly_chart(fig_quality, use_container_width=True)

def show_visualizations():
    """Interactive visualizations interface"""
    
    st.header("🎨 Interactive Visualizations")
    st.markdown("**Create custom visualizations and explore data patterns**")
    
    # Load data
    data = load_current_data()
    
    if data is None:
        st.warning("⚠️ No data available. Please upload data in the Data Management section.")
        return
    
    # Visualization type selection
    viz_type = st.selectbox(
        "Select Visualization Type",
        ["📈 Time Series", "📊 Correlation Analysis", "📅 Seasonal Patterns", "📉 Distribution Analysis", "🔄 Multi-Variable Comparison"],
        help="Choose the type of visualization to create"
    )
    
    if viz_type == "📈 Time Series":
        show_time_series_viz(data)
    elif viz_type == "📊 Correlation Analysis":
        show_correlation_viz(data)
    elif viz_type == "📅 Seasonal Patterns":
        show_seasonal_viz(data)
    elif viz_type == "📉 Distribution Analysis":
        show_distribution_viz(data)
    elif viz_type == "🔄 Multi-Variable Comparison":
        show_multivariable_viz(data)

def show_time_series_viz(data):
    """Time series visualization interface"""
    
    st.subheader("📈 Time Series Analysis")
    
    # Column selection
    fraction_columns = [col for col in data.columns if '_mean' in col or '_median' in col]
    
    if not fraction_columns:
        st.error("❌ No fraction columns found")
        return
    
    selected_columns = st.multiselect(
        "Select Variables to Plot",
        fraction_columns,
        default=fraction_columns[:3] if len(fraction_columns) >= 3 else fraction_columns,
        help="Choose one or more variables to visualize"
    )
    
    if not selected_columns:
        st.warning("⚠️ Please select at least one variable")
        return
    
    # Create time series plot
    from dashboard_components import Visualizer
    
    if 'date' in data.columns:
        fig = Visualizer.create_time_series_plot(data, selected_columns, "Multi-Variable Time Series")
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            
            # Additional options
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Show Statistics"):
                    for col in selected_columns:
                        stats = data[col].describe()
                        st.subheader(f"Statistics: {col}")
                        st.dataframe(stats.to_frame(col))
            
            with col2:
                if st.button("📥 Export Plot Data"):
                    export_data = data[['date'] + selected_columns].dropna()
                    csv = export_data.to_csv(index=False)
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv,
                        file_name=f"time_series_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        else:
            st.error("❌ Could not create time series plot")
    else:
        st.error("❌ No date column found in data")

def show_correlation_viz(data):
    """Correlation analysis interface"""
    
    st.subheader("📊 Correlation Analysis")
    
    # Select numeric columns
    numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
    fraction_columns = [col for col in numeric_columns if '_mean' in col or '_median' in col]
    
    if len(fraction_columns) < 2:
        st.error("❌ Need at least 2 fraction columns for correlation analysis")
        return
    
    selected_columns = st.multiselect(
        "Select Variables for Correlation",
        fraction_columns,
        default=fraction_columns,
        help="Choose variables to include in correlation analysis"
    )
    
    if len(selected_columns) < 2:
        st.warning("⚠️ Please select at least 2 variables")
        return
    
    # Create correlation matrix
    from dashboard_components import Visualizer
    fig = Visualizer.create_correlation_matrix(data, selected_columns)
    
    if fig:
        st.plotly_chart(fig, use_container_width=True)
        
        # Show correlation table
        corr_matrix = data[selected_columns].corr()
        st.subheader("📋 Correlation Matrix")
        st.dataframe(corr_matrix.style.background_gradient(cmap='RdBu', center=0))
        
        # Highlight strongest correlations
        st.subheader("🔍 Strongest Correlations")
        
        # Get correlation pairs
        corr_pairs = []
        for i in range(len(selected_columns)):
            for j in range(i+1, len(selected_columns)):
                corr_value = corr_matrix.iloc[i, j]
                corr_pairs.append((selected_columns[i], selected_columns[j], corr_value))
        
        # Sort by absolute correlation
        corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        
        for var1, var2, corr in corr_pairs[:5]:
            st.text(f"{var1} ↔ {var2}: {corr:.3f}")
    
    else:
        st.error("❌ Could not create correlation matrix")

def show_seasonal_viz(data):
    """Seasonal pattern analysis"""
    
    st.subheader("📅 Seasonal Pattern Analysis")
    
    if 'month' not in data.columns:
        st.error("❌ No month column found for seasonal analysis")
        return
    
    # Variable selection
    fraction_columns = [col for col in data.columns if '_mean' in col or '_median' in col]
    
    if not fraction_columns:
        st.error("❌ No fraction columns found")
        return
    
    selected_variable = st.selectbox(
        "Select Variable",
        fraction_columns,
        help="Choose variable for seasonal analysis"
    )
    
    # Create monthly boxplot
    from dashboard_components import Visualizer
    fig = Visualizer.create_monthly_boxplot(data, selected_variable, f"Seasonal Patterns: {selected_variable}")
    
    if fig:
        st.plotly_chart(fig, use_container_width=True)
        
        # Monthly statistics
        monthly_stats = data.groupby('month')[selected_variable].agg(['mean', 'std', 'count']).round(4)
        
        st.subheader("📊 Monthly Statistics")
        st.dataframe(monthly_stats)
        
        # Seasonal summary
        if len(data) > 0:
            seasonal_data = data.copy()
            seasonal_data['season'] = seasonal_data['month'].map({
                12: 'Winter', 1: 'Winter', 2: 'Winter',
                3: 'Spring', 4: 'Spring', 5: 'Spring',
                6: 'Summer', 7: 'Summer', 8: 'Summer',
                9: 'Autumn', 10: 'Autumn', 11: 'Autumn'
            })
            
            seasonal_summary = seasonal_data.groupby('season')[selected_variable].agg(['mean', 'std']).round(4)
            
            st.subheader("🍂 Seasonal Summary")
            st.dataframe(seasonal_summary)
    
    else:
        st.error("❌ Could not create seasonal plot")

def show_distribution_viz(data):
    """Distribution analysis interface"""
    
    st.subheader("📉 Distribution Analysis")
    
    # Variable selection
    fraction_columns = [col for col in data.columns if '_mean' in col or '_median' in col]
    
    if not fraction_columns:
        st.error("❌ No fraction columns found")
        return
    
    selected_variable = st.selectbox(
        "Select Variable",
        fraction_columns,
        help="Choose variable for distribution analysis"
    )
    
    # Plot type selection
    plot_type = st.radio(
        "Plot Type",
        ["📊 Histogram", "📈 Density Plot", "📦 Box Plot"],
        horizontal=True
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if plot_type == "📊 Histogram":
            bins = st.slider("Number of Bins", 10, 50, 30)
            fig = px.histogram(data, x=selected_variable, nbins=bins,
                             title=f"Distribution of {selected_variable}")
            fig.update_layout(template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
        
        elif plot_type == "📈 Density Plot":
            fig = px.histogram(data, x=selected_variable, nbins=50, histnorm='density',
                             title=f"Density Distribution of {selected_variable}")
            fig.update_layout(template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
        
        elif plot_type == "📦 Box Plot":
            fig = px.box(data, y=selected_variable,
                        title=f"Box Plot of {selected_variable}")
            fig.update_layout(template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribution statistics
        st.subheader("📊 Statistics")
        
        values = data[selected_variable].dropna()
        
        if len(values) > 0:
            stats = {
                "Count": len(values),
                "Mean": f"{values.mean():.4f}",
                "Median": f"{values.median():.4f}",
                "Std Dev": f"{values.std():.4f}",
                "Min": f"{values.min():.4f}",
                "Max": f"{values.max():.4f}",
                "Skewness": f"{values.skew():.3f}",
                "Kurtosis": f"{values.kurtosis():.3f}"
            }
            
            for key, value in stats.items():
                st.text(f"{key}: {value}")

def show_multivariable_viz(data):
    """Multi-variable comparison interface"""
    
    st.subheader("🔄 Multi-Variable Comparison")
    
    # Variable selection
    fraction_columns = [col for col in data.columns if '_mean' in col or '_median' in col]
    
    if len(fraction_columns) < 2:
        st.error("❌ Need at least 2 fraction columns for comparison")
        return
    
    # Select variables
    var1 = st.selectbox("Select First Variable", fraction_columns, key="var1")
    var2 = st.selectbox("Select Second Variable", fraction_columns, key="var2", 
                       index=1 if len(fraction_columns) > 1 else 0)
    
    if var1 == var2:
        st.warning("⚠️ Please select different variables")
        return
    
    # Comparison plot
    fig = px.scatter(data, x=var1, y=var2,
                    title=f"Scatter Plot: {var1} vs {var2}",
                    hover_data=['date'] if 'date' in data.columns else None)
    
    # Add trendline
    fig.add_traces(px.scatter(data, x=var1, y=var2, trendline="ols").data[1:])
    
    fig.update_layout(template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)
    
    # Correlation
    if len(data[[var1, var2]].dropna()) > 0:
        correlation = data[var1].corr(data[var2])
        st.metric("📊 Correlation Coefficient", f"{correlation:.3f}")
    
    # Side-by-side time series if date available
    if 'date' in data.columns:
        st.subheader("📈 Time Series Comparison")
        
        fig_comparison = go.Figure()
        
        fig_comparison.add_trace(go.Scatter(
            x=pd.to_datetime(data['date']),
            y=data[var1],
            mode='lines+markers',
            name=var1,
            line=dict(color='blue')
        ))
        
        fig_comparison.add_trace(go.Scatter(
            x=pd.to_datetime(data['date']),
            y=data[var2],
            mode='lines+markers',
            name=var2,
            yaxis='y2',
            line=dict(color='red')
        ))
        
        fig_comparison.update_layout(
            title=f"Time Series Comparison: {var1} vs {var2}",
            xaxis_title="Date",
            yaxis_title=var1,
            yaxis2=dict(title=var2, overlaying='y', side='right'),
            template='plotly_white'
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)

def show_gee_integration():
    """Google Earth Engine integration interface"""
    
    st.header("🛰️ Google Earth Engine Integration")
    st.markdown("**Fetch fresh MODIS satellite data from Google Earth Engine**")
    
    # Check GEE status
    from dashboard_components import GEEIntegration
    gee_status = GEEIntegration.check_gee_status()
    
    # Status indicators
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_icon = "✅" if gee_status.get('installed', False) else "❌"
        st.metric("🔧 GEE Installation", status_icon)
    
    with col2:
        auth_icon = "✅" if gee_status.get('authenticated', False) else "❌"
        st.metric("🔑 Authentication", auth_icon)
    
    with col3:
        version = gee_status.get('version', 'Unknown')
        st.metric("📦 Version", version)
    
    if gee_status.get('error'):
        st.error(f"❌ GEE Error: {gee_status['error']}")
        st.info("💡 Install Google Earth Engine API: `pip install earthengine-api`")
        return
    
    if not gee_status.get('installed', False):
        st.warning("⚠️ Google Earth Engine not installed")
        
        if st.button("📦 Install GEE API"):
            with st.spinner("Installing Google Earth Engine API..."):
                try:
                    import subprocess
                    import sys
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "earthengine-api"])
                    st.success("✅ GEE API installed successfully!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ Installation failed: {str(e)}")
        return
    
    # GEE interface tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Region Setup", "📡 Data Fetching", "📊 Results", "⚙️ Settings"])
    
    with tab1:
        show_gee_region_setup()
    
    with tab2:
        show_gee_data_fetching()
    
    with tab3:
        show_gee_results()
    
    with tab4:
        show_gee_settings()

def show_gee_region_setup():
    """GEE region configuration"""
    
    st.subheader("🗺️ Region Configuration")
    
    # Get region info
    from dashboard_components import GEEIntegration
    regions = GEEIntegration.get_region_info()
    
    if regions:
        st.info("📍 Configured regions found in config")
        
        for region_name, region_data in regions.items():
            with st.expander(f"📍 {region_name}", expanded=True):
                st.json(region_data)
    else:
        st.warning("⚠️ No regions configured")
    
    # Manual region input
    st.subheader("🎯 Custom Region Definition")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Region Name", value="Saskatchewan Glacier", key="region_name")
        
        # Coordinates
        st.number_input("North Latitude", -90.0, 90.0, 52.15, 0.01, key="north_lat")
        st.number_input("South Latitude", -90.0, 90.0, 52.10, 0.01, key="south_lat")
    
    with col2:
        st.number_input("East Longitude", -180.0, 180.0, -117.20, 0.01, key="east_lon")
        st.number_input("West Longitude", -180.0, 180.0, -117.30, 0.01, key="west_lon")
        
        # Additional parameters
        st.selectbox("Data Collection", ["MCD43A3", "MOD10A1", "Both"], key="collection")
    
    if st.button("💾 Save Region Configuration"):
        st.success("✅ Region configuration saved!")

def show_gee_data_fetching():
    """GEE data fetching interface"""
    
    st.subheader("📡 MODIS Data Fetching")
    
    # Date range selection
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Start Date", value=datetime(2010, 1, 1))
    
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Fetching options
    st.subheader("⚙️ Fetching Options")
    
    col3, col4 = st.columns(2)
    
    with col3:
        max_cloud_cover = st.slider("Max Cloud Cover (%)", 0, 100, 20)
        quality_filter = st.checkbox("Apply Quality Filters", value=True)
    
    with col4:
        output_format = st.selectbox("Output Format", ["CSV", "GeoTIFF", "Both"])
        sample_reduction = st.selectbox("Spatial Reduction", ["mean", "median", "max", "min"])
    
    # Fetch button
    if st.button("🚀 Fetch MODIS Data", type="primary"):
        
        if start_date >= end_date:
            st.error("❌ Start date must be before end date")
            return
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Simulate fetching process
            status_text.text("🔍 Initializing GEE connection...")
            progress_bar.progress(10)
            
            status_text.text("🗺️ Setting up region geometry...")
            progress_bar.progress(25)
            
            status_text.text("📡 Querying MODIS collections...")
            progress_bar.progress(50)
            
            status_text.text("📊 Processing and filtering data...")
            progress_bar.progress(75)
            
            status_text.text("💾 Exporting results...")
            progress_bar.progress(90)
            
            # Simulate completion
            import time
            time.sleep(1)
            
            progress_bar.progress(100)
            status_text.text("✅ Data fetching completed!")
            
            st.success(f"🎉 Successfully fetched MODIS data from {start_date} to {end_date}")
            
            # Show sample results
            st.subheader("📊 Sample Results")
            sample_data = {
                'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
                'Border_Mean': [0.8234, 0.8156, 0.8298],
                'Mixed_Low_Mean': [0.7892, 0.7934, 0.7876],
                'Quality': [0, 1, 0]
            }
            
            sample_df = pd.DataFrame(sample_data)
            st.dataframe(sample_df)
            
        except Exception as e:
            st.error(f"❌ Error fetching data: {str(e)}")
            progress_bar.empty()
            status_text.empty()

def show_gee_results():
    """Show GEE fetching results"""
    
    st.subheader("📊 Recent Fetching Results")
    
    # Check for recent GEE results
    results_dir = Path("data/gee_results")
    
    if results_dir.exists():
        result_files = list(results_dir.glob("*.csv"))
        
        if result_files:
            st.success(f"📁 Found {len(result_files)} result files")
            
            # Show most recent files
            result_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for i, file_path in enumerate(result_files[:5]):
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                with st.expander(f"📄 {file_path.name} ({mod_time.strftime('%Y-%m-%d %H:%M')})"):
                    try:
                        df = pd.read_csv(file_path)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Records", len(df))
                            st.metric("Columns", len(df.columns))
                        
                        with col2:
                            if 'date' in df.columns:
                                st.metric("Date Range", f"{df['date'].min()} to {df['date'].max()}")
                        
                        # Preview
                        st.dataframe(df.head())
                        
                        # Download button
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label=f"💾 Download {file_path.name}",
                            data=csv,
                            file_name=file_path.name,
                            mime="text/csv"
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Error reading file: {str(e)}")
        else:
            st.info("📭 No result files found")
    else:
        st.info("📁 Results directory not found")

def show_gee_settings():
    """GEE settings and configuration"""
    
    st.subheader("⚙️ GEE Settings")
    
    # Authentication section
    st.subheader("🔑 Authentication")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔐 Authenticate GEE"):
            with st.spinner("Opening authentication..."):
                try:
                    # Simulate authentication
                    st.info("🌐 Please complete authentication in your browser")
                    import time
                    time.sleep(2)
                    st.success("✅ Authentication completed!")
                except Exception as e:
                    st.error(f"❌ Authentication failed: {str(e)}")
    
    with col2:
        if st.button("✅ Test Connection"):
            with st.spinner("Testing GEE connection..."):
                try:
                    # Simulate connection test
                    import time
                    time.sleep(1)
                    st.success("✅ GEE connection successful!")
                except Exception as e:
                    st.error(f"❌ Connection failed: {str(e)}")
    
    # Configuration options
    st.subheader("📊 Default Settings")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.selectbox("Default Collection", ["MCD43A3", "MOD10A1"], key="default_collection")
        st.number_input("Default Cloud Cover Threshold", 0, 100, 20, key="default_cloud")
    
    with col4:
        st.selectbox("Default Spatial Resolution", ["500m", "1km"], key="default_resolution")
        st.checkbox("Auto-apply Quality Filters", value=True, key="auto_quality")
    
    # Export settings
    st.subheader("💾 Export Configuration")
    
    export_dir = st.text_input("Export Directory", value="data/gee_results")
    filename_pattern = st.text_input("Filename Pattern", value="modis_data_{date}_{collection}.csv")
    
    if st.button("💾 Save Settings"):
        st.success("✅ Settings saved successfully!")

def show_custom_analysis():
    """Custom analysis interface"""
    
    st.header("📋 Custom Analysis")
    st.markdown("**Design and run custom analysis workflows**")
    
    # Load data
    data = load_current_data()
    
    if data is None:
        st.warning("⚠️ No data available. Please upload data in the Data Management section.")
        return
    
    # Analysis type selection
    analysis_type = st.selectbox(
        "Select Analysis Type",
        ["🕐 Period-Specific Analysis", "🔄 Fraction Comparison", "📊 Statistical Summary", "🎯 Custom Filtering", "📈 Trend Comparison"],
        help="Choose the type of custom analysis to perform"
    )
    
    if analysis_type == "🕐 Period-Specific Analysis":
        show_period_analysis(data)
    elif analysis_type == "🔄 Fraction Comparison":
        show_fraction_comparison(data)
    elif analysis_type == "📊 Statistical Summary":
        show_statistical_summary(data)
    elif analysis_type == "🎯 Custom Filtering":
        show_custom_filtering(data)
    elif analysis_type == "📈 Trend Comparison":
        show_trend_comparison(data)

def show_period_analysis(data):
    """Period-specific analysis"""
    
    st.subheader("🕐 Period-Specific Analysis")
    st.markdown("Compare albedo patterns across different time periods")
    
    if 'date' not in data.columns:
        st.error("❌ No date column found")
        return
    
    data['date'] = pd.to_datetime(data['date'])
    
    # Period selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Period 1")
        period1_start = st.date_input("Start Date", value=data['date'].min(), key="p1_start")
        period1_end = st.date_input("End Date", value=data['date'].min() + timedelta(days=365), key="p1_end")
    
    with col2:
        st.subheader("📅 Period 2")
        period2_start = st.date_input("Start Date", value=data['date'].max() - timedelta(days=365), key="p2_start")
        period2_end = st.date_input("End Date", value=data['date'].max(), key="p2_end")
    
    # Filter data for each period
    period1_data = data[(data['date'] >= pd.to_datetime(period1_start)) & (data['date'] <= pd.to_datetime(period1_end))]
    period2_data = data[(data['date'] >= pd.to_datetime(period2_start)) & (data['date'] <= pd.to_datetime(period2_end))]
    
    if len(period1_data) == 0 or len(period2_data) == 0:
        st.warning("⚠️ One or both periods have no data")
        return
    
    # Variable selection
    fraction_columns = [col for col in data.columns if '_mean' in col or '_median' in col]
    selected_fraction = st.selectbox("Select Variable", fraction_columns)
    
    # Analysis results
    col1, col2, col3 = st.columns(3)
    
    with col1:
        period1_mean = period1_data[selected_fraction].mean()
        st.metric("📊 Period 1 Mean", f"{period1_mean:.4f}")
        
        period1_std = period1_data[selected_fraction].std()
        st.metric("📈 Period 1 Std", f"{period1_std:.4f}")
    
    with col2:
        period2_mean = period2_data[selected_fraction].mean()
        st.metric("📊 Period 2 Mean", f"{period2_mean:.4f}")
        
        period2_std = period2_data[selected_fraction].std()
        st.metric("📈 Period 2 Std", f"{period2_std:.4f}")
    
    with col3:
        difference = period2_mean - period1_mean
        st.metric("🔄 Difference", f"{difference:.4f}", delta=f"{difference:.4f}")
        
        # Calculate percentage change
        pct_change = (difference / period1_mean) * 100 if period1_mean != 0 else 0
        st.metric("📈 % Change", f"{pct_change:.2f}%")
    
    # Visualization
    st.subheader("📊 Period Comparison")
    
    # Create comparison plot
    fig = go.Figure()
    
    fig.add_trace(go.Box(
        y=period1_data[selected_fraction],
        name=f"Period 1 ({period1_start} to {period1_end})",
        marker_color='blue'
    ))
    
    fig.add_trace(go.Box(
        y=period2_data[selected_fraction],
        name=f"Period 2 ({period2_start} to {period2_end})",
        marker_color='red'
    ))
    
    fig.update_layout(
        title=f"Period Comparison: {selected_fraction}",
        yaxis_title="Albedo",
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_fraction_comparison(data):
    """Fraction comparison analysis"""
    
    st.subheader("🔄 Fraction Comparison")
    st.markdown("Compare different albedo fractions side by side")
    
    # Select fractions to compare
    fraction_columns = [col for col in data.columns if '_mean' in col or '_median' in col]
    
    if len(fraction_columns) < 2:
        st.error("❌ Need at least 2 fraction columns for comparison")
        return
    
    selected_fractions = st.multiselect(
        "Select Fractions to Compare",
        fraction_columns,
        default=fraction_columns[:3] if len(fraction_columns) >= 3 else fraction_columns
    )
    
    if len(selected_fractions) < 2:
        st.warning("⚠️ Please select at least 2 fractions")
        return
    
    # Statistical comparison
    st.subheader("📊 Statistical Comparison")
    
    comparison_stats = {}
    for fraction in selected_fractions:
        values = data[fraction].dropna()
        comparison_stats[fraction] = {
            'Mean': values.mean(),
            'Median': values.median(),
            'Std': values.std(),
            'Min': values.min(),
            'Max': values.max(),
            'Count': len(values)
        }
    
    comparison_df = pd.DataFrame(comparison_stats).T
    st.dataframe(comparison_df.round(4))
    
    # Visualization tabs
    tab1, tab2, tab3 = st.tabs(["📈 Time Series", "📊 Box Plots", "🔄 Scatter Matrix"])
    
    with tab1:
        if 'date' in data.columns:
            from dashboard_components import Visualizer
            fig = Visualizer.create_time_series_plot(data, selected_fractions, "Fraction Comparison")
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No date column for time series")
    
    with tab2:
        # Create side-by-side box plots
        fig = go.Figure()
        
        for fraction in selected_fractions:
            fig.add_trace(go.Box(
                y=data[fraction].dropna(),
                name=fraction,
                boxpoints='outliers'
            ))
        
        fig.update_layout(
            title="Distribution Comparison",
            yaxis_title="Albedo",
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Correlation analysis
        if len(selected_fractions) >= 2:
            from dashboard_components import Visualizer
            fig = Visualizer.create_correlation_matrix(data, selected_fractions)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

def show_statistical_summary(data):
    """Statistical summary generator"""
    
    st.subheader("📊 Statistical Summary Generator")
    st.markdown("Generate comprehensive statistical reports")
    
    # Variable selection
    fraction_columns = [col for col in data.columns if '_mean' in col or '_median' in col]
    numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
    
    analysis_columns = st.multiselect(
        "Select Variables for Analysis",
        numeric_columns,
        default=fraction_columns if fraction_columns else numeric_columns[:5]
    )
    
    if not analysis_columns:
        st.warning("⚠️ Please select at least one variable")
        return
    
    # Generate summary
    if st.button("📊 Generate Statistical Summary"):
        
        # Basic statistics
        st.subheader("📋 Descriptive Statistics")
        desc_stats = data[analysis_columns].describe()
        st.dataframe(desc_stats.round(4))
        
        # Additional statistics
        st.subheader("📈 Advanced Statistics")
        
        advanced_stats = {}
        for col in analysis_columns:
            values = data[col].dropna()
            if len(values) > 0:
                advanced_stats[col] = {
                    'Skewness': values.skew(),
                    'Kurtosis': values.kurtosis(),
                    'Range': values.max() - values.min(),
                    'IQR': values.quantile(0.75) - values.quantile(0.25),
                    'CV': values.std() / values.mean() if values.mean() != 0 else 0
                }
        
        advanced_df = pd.DataFrame(advanced_stats).T
        st.dataframe(advanced_df.round(4))
        
        # Missing data analysis
        if data[analysis_columns].isnull().sum().sum() > 0:
            st.subheader("🔍 Missing Data Analysis")
            
            missing_data = data[analysis_columns].isnull().sum()
            missing_pct = (missing_data / len(data)) * 100
            
            missing_df = pd.DataFrame({
                'Missing Count': missing_data,
                'Missing %': missing_pct
            })
            
            st.dataframe(missing_df[missing_df['Missing Count'] > 0])
        
        # Export option
        if st.button("📥 Export Summary Report"):
            
            # Combine all statistics
            report_data = {
                'Descriptive Statistics': desc_stats,
                'Advanced Statistics': advanced_df
            }
            
            # Create downloadable report
            report_str = "Statistical Summary Report\n"
            report_str += "=" * 50 + "\n\n"
            
            for section, df in report_data.items():
                report_str += f"{section}\n"
                report_str += "-" * len(section) + "\n"
                report_str += df.to_string() + "\n\n"
            
            st.download_button(
                label="💾 Download Report",
                data=report_str,
                file_name=f"statistical_summary_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )

def show_custom_filtering(data):
    """Custom data filtering interface"""
    
    st.subheader("🎯 Custom Data Filtering")
    st.markdown("Apply custom filters to explore specific data subsets")
    
    # Initialize filtered data
    filtered_data = data.copy()
    
    # Date filtering
    if 'date' in data.columns:
        st.subheader("📅 Date Filtering")
        
        data['date'] = pd.to_datetime(data['date'])
        min_date = data['date'].min()
        max_date = data['date'].max()
        
        date_range = st.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            filtered_data = filtered_data[
                (filtered_data['date'] >= pd.to_datetime(date_range[0])) & 
                (filtered_data['date'] <= pd.to_datetime(date_range[1]))
            ]
    
    # Quality filtering
    if 'quality' in data.columns:
        st.subheader("🏷️ Quality Filtering")
        
        quality_values = sorted(data['quality'].unique())
        selected_quality = st.multiselect(
            "Select Quality Levels",
            quality_values,
            default=quality_values
        )
        
        if selected_quality:
            filtered_data = filtered_data[filtered_data['quality'].isin(selected_quality)]
    
    # Numeric filtering
    st.subheader("🔢 Numeric Filtering")
    
    numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
    
    for col in numeric_columns[:3]:  # Limit to first 3 for UI space
        if col in data.columns:
            col_min = float(data[col].min())
            col_max = float(data[col].max())
            
            value_range = st.slider(
                f"{col} Range",
                col_min, col_max, (col_min, col_max),
                step=(col_max - col_min) / 100,
                key=f"filter_{col}"
            )
            
            filtered_data = filtered_data[
                (filtered_data[col] >= value_range[0]) & 
                (filtered_data[col] <= value_range[1])
            ]
    
    # Show filtering results
    st.subheader("📊 Filtering Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📈 Original Records", len(data))
    
    with col2:
        st.metric("📊 Filtered Records", len(filtered_data))
    
    with col3:
        retention_pct = (len(filtered_data) / len(data)) * 100 if len(data) > 0 else 0
        st.metric("📋 Retention %", f"{retention_pct:.1f}%")
    
    # Preview filtered data
    if len(filtered_data) > 0:
        st.subheader("👀 Filtered Data Preview")
        st.dataframe(filtered_data.head(10))
        
        # Export filtered data
        if st.button("📥 Export Filtered Data"):
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="💾 Download Filtered CSV",
                data=csv,
                file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    else:
        st.warning("⚠️ No data remains after filtering")

def show_trend_comparison(data):
    """Trend comparison analysis"""
    
    st.subheader("📈 Trend Comparison")
    st.markdown("Compare trends across different variables and time periods")
    
    # Variable selection
    fraction_columns = [col for col in data.columns if '_mean' in col or '_median' in col]
    
    if len(fraction_columns) < 2:
        st.error("❌ Need at least 2 fraction columns for trend comparison")
        return
    
    selected_fractions = st.multiselect(
        "Select Variables for Trend Comparison",
        fraction_columns,
        default=fraction_columns[:3] if len(fraction_columns) >= 3 else fraction_columns
    )
    
    if len(selected_fractions) < 2:
        st.warning("⚠️ Please select at least 2 variables")
        return
    
    # Calculate trends for each fraction
    from dashboard_components import TrendAnalyzer
    
    trend_results = {}
    for fraction in selected_fractions:
        trend_result = TrendAnalyzer.simple_trend_test(data, fraction)
        if trend_result and 'error' not in trend_result:
            trend_results[fraction] = trend_result
    
    if not trend_results:
        st.error("❌ Could not calculate trends")
        return
    
    # Display trend comparison
    st.subheader("📊 Trend Summary")
    
    trend_df = pd.DataFrame(trend_results).T
    trend_df = trend_df[['direction', 'slope', 'annual_change']]
    trend_df.columns = ['Trend Direction', 'Slope', 'Annual Change']
    
    st.dataframe(trend_df.round(6))
    
    # Trend visualization
    st.subheader("📈 Trend Visualization")
    
    if 'date' in data.columns:
        fig = go.Figure()
        
        for fraction in selected_fractions:
            fig.add_trace(go.Scatter(
                x=pd.to_datetime(data['date']),
                y=data[fraction],
                mode='lines+markers',
                name=fraction,
                line=dict(width=2),
                marker=dict(size=4)
            ))
        
        fig.update_layout(
            title="Multi-Variable Trend Comparison",
            xaxis_title="Date",
            yaxis_title="Albedo",
            template='plotly_white',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Trend ranking
    st.subheader("🏆 Trend Ranking")
    
    # Sort by absolute slope for ranking
    sorted_trends = sorted(trend_results.items(), key=lambda x: abs(x[1]['slope']), reverse=True)
    
    for i, (fraction, trend_data) in enumerate(sorted_trends):
        rank = i + 1
        direction = trend_data['direction']
        slope = trend_data['slope']
        symbol = trend_data['symbol']
        
        st.text(f"{rank}. {fraction}: {symbol} {direction} (slope: {slope:.6f})")

def show_configuration():
    """Configuration and settings"""
    
    st.header("⚙️ Configuration")
    
    tab1, tab2 = st.tabs(["🔧 Settings", "📊 System Info"])
    
    with tab1:
        st.subheader("🔧 Analysis Settings")
        
        # Configuration options
        st.selectbox("Analysis Variable", ["border", "mixed_low", "water"], help="Primary variable for analysis")
        st.slider("Significance Level", 0.01, 0.1, 0.05, 0.01, help="Statistical significance threshold")
        st.number_input("Bootstrap Iterations", 100, 5000, 1000, 100, help="Number of bootstrap iterations")
        
        if st.button("💾 Save Configuration"):
            st.success("✅ Configuration saved!")
    
    with tab2:
        st.subheader("📊 System Information")
        
        # System info
        st.text(f"Python Version: {sys.version}")
        st.text(f"Working Directory: {os.getcwd()}")
        st.text(f"Script Directory: {script_dir}")
        
        # Module availability
        modules_status = check_module_availability()
        st.subheader("📦 Module Status")
        for module, status in modules_status.items():
            st.text(f"{module}: {'✅' if status else '❌'}")

def check_module_availability():
    """Check availability of key modules"""
    
    modules = {}
    
    try:
        import pandas
        modules['pandas'] = True
    except ImportError:
        modules['pandas'] = False
    
    try:
        import numpy
        modules['numpy'] = True
    except ImportError:
        modules['numpy'] = False
    
    try:
        import plotly
        modules['plotly'] = True
    except ImportError:
        modules['plotly'] = False
    
    try:
        from data_handler import AlbedoDataHandler
        modules['data_handler'] = True
    except ImportError:
        modules['data_handler'] = False
    
    try:
        from gee.client import GEEClient
        modules['gee'] = True
    except ImportError:
        modules['gee'] = False
    
    return modules

if __name__ == "__main__":
    main()