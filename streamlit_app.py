#!/usr/bin/env python3
"""
Saskatchewan Glacier Albedo Analysis - Streamlit App
===================================================

Interactive web application for analyzing glacier albedo trends from MODIS satellite data.
This app provides a user-friendly interface to the existing analysis pipeline.

To run:
    streamlit run streamlit_app.py
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Page configuration
st.set_page_config(
    page_title="Saskatchewan Glacier Albedo Analysis",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/saskatchewan-glacier-albedo-analysis',
        'Report a bug': "https://github.com/yourusername/saskatchewan-glacier-albedo-analysis/issues",
        'About': """
        # Saskatchewan Glacier Albedo Analysis
        
        This application analyzes albedo trends from MODIS satellite data (2010-2024).
        
        **Datasets:**
        - MCD43A3: General albedo (16-day composite)
        - MOD10A1: Snow albedo (daily)
        """
    }
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1e3d59;
        text-align: center;
        margin-bottom: 2rem;
    }
    .dataset-card {
        background-color: #f5f7fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #1e3d59;
    }
    .metric-container {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🏔️ Saskatchewan Glacier Albedo Analysis</h1>', unsafe_allow_html=True)

# Introduction
st.markdown("""
Welcome to the interactive analysis tool for Saskatchewan Glacier albedo trends. 
This application provides comprehensive analysis of MODIS satellite data from 2010 to 2024.
""")

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🚀 Quick Start", "📚 Documentation"])

with tab1:
    st.header("Project Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="dataset-card">
        <h3>🌍 MCD43A3 Dataset</h3>
        <p><strong>Type:</strong> General Albedo</p>
        <p><strong>Temporal Resolution:</strong> 16-day composite</p>
        <p><strong>Source:</strong> MODIS Combined (Terra + Aqua)</p>
        <p><strong>Coverage:</strong> 2010-2024</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="dataset-card">
        <h3>❄️ MOD10A1 Dataset</h3>
        <p><strong>Type:</strong> Snow Albedo</p>
        <p><strong>Temporal Resolution:</strong> Daily</p>
        <p><strong>Source:</strong> Terra Snow Cover</p>
        <p><strong>Coverage:</strong> 2010-2024</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.header("Available Analyses")
    
    # Analysis types
    analyses = {
        "📈 Trend Analysis": "Statistical trends using Mann-Kendall test, seasonal patterns, and long-term changes",
        "🏔️ Elevation Analysis": "Albedo variations across elevation bands (2000m - 3400m)",
        "🔄 Dataset Comparison": "Cross-comparison between MCD43A3 and MOD10A1 products",
        "📅 Daily Melt Season": "High-resolution daily albedo during melt seasons",
        "🎯 Pixel Quality": "Quality assessment and coverage analysis"
    }
    
    for title, description in analyses.items():
        st.markdown(f"**{title}**: {description}")

with tab2:
    st.header("Quick Start Guide")
    
    st.markdown("""
    ### 🎯 Navigate to Analysis Pages
    
    Use the **sidebar** on the left to access different analysis modules:
    
    1. **📊 Dataset Analysis**: Analyze individual datasets (MCD43A3 or MOD10A1)
    2. **🔄 Comparison**: Compare trends between datasets
    3. **🏔️ Elevation Analysis**: Explore elevation-dependent patterns
    4. **🔍 Interactive Explorer**: Custom date ranges and parameters
    
    ### 💡 Tips for Best Experience
    
    - 🎨 **Interactive Plots**: All charts are interactive - zoom, pan, and hover for details
    - 💾 **Export Options**: Download plots and data using the download buttons
    - ⚙️ **Customization**: Adjust parameters in the sidebar for each analysis
    - 📈 **Real-time Updates**: Charts update automatically when you change settings
    """)
    
    # Quick metrics
    st.header("📊 Quick Statistics")
    
    try:
        from config import FRACTION_CLASSES, CLASS_LABELS, MCD43A3_CONFIG, MOD10A1_CONFIG
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Time Period", "2010-2024")
        with col2:
            st.metric("Years of Data", "15")
        with col3:
            st.metric("Datasets", "2 (MCD43A3, MOD10A1)")
        with col4:
            st.metric("Fraction Classes", len(FRACTION_CLASSES))
            
    except ImportError:
        st.warning("Configuration not loaded. Please check your setup.")

with tab3:
    st.header("Documentation")
    
    st.markdown("""
    ### 📖 User Guide
    
    This application provides an interactive interface to the Saskatchewan Glacier albedo analysis pipeline.
    
    #### Datasets
    - **MCD43A3**: MODIS combined albedo product (16-day composite)
    - **MOD10A1**: Terra snow albedo product (daily resolution)
    
    #### Fraction Classes
    The analysis uses ice fraction classes to categorize pixels:
    - **Pure Ice**: >95% ice coverage
    - **Mostly Ice**: 80-95% ice coverage
    - **Mixed Ice**: 50-80% ice coverage
    - **Some Ice**: 20-50% ice coverage
    - **Little Ice**: <20% ice coverage
    
    #### Analysis Methods
    - **Mann-Kendall Test**: Non-parametric trend detection
    - **Theil-Sen Estimator**: Robust slope estimation
    - **Seasonal Decomposition**: Separate trend, seasonal, and residual components
    
    ### 🔧 Technical Details
    
    - **Data Source**: Google Earth Engine exports
    - **Quality Control**: Configurable thresholds for data quality
    - **Visualization**: Plotly for interactive charts
    - **Backend**: Reuses existing Python analysis modules
    """)

# Sidebar
with st.sidebar:
    st.header("🧭 Navigation")
    
    st.markdown("""
    ### Available Pages:
    
    - **Home** (current)
    - **Dataset Analysis**
    - **Comparison**
    - **Elevation Analysis**
    - **Interactive Explorer**
    
    Navigate using the sidebar menu in Streamlit.
    """)
    
    st.divider()
    
    st.header("ℹ️ Information")
    st.markdown("""
    **Version**: 1.0.0  
    **Last Updated**: 2025  
    **Author**: Your Name  
    """)
    
    st.divider()
    
    # Add useful links
    st.header("🔗 Useful Links")
    st.markdown("""
    - [MODIS Products](https://modis.gsfc.nasa.gov/)
    - [Google Earth Engine](https://earthengine.google.com/)
    - [Project Repository](https://github.com/yourusername/saskatchewan-glacier-albedo-analysis)
    """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    Saskatchewan Glacier Albedo Analysis | Powered by Streamlit & MODIS Data
</div>
""", unsafe_allow_html=True)