# Saskatchewan Glacier Albedo Analysis - Streamlit App

## Overview

This Streamlit web application provides an interactive interface for analyzing albedo trends from MODIS satellite data (2010-2024) for Saskatchewan Glacier. The app complements the existing command-line interface with user-friendly visualizations and real-time analysis capabilities.

## Features

### 🏠 **Home Page**
- Project overview and documentation
- Quick start guide
- Links to analysis pages

### 📊 **Dataset Analysis**
- Interactive analysis of individual datasets (MCD43A3 or MOD10A1)
- Real-time parameter adjustment
- Time series visualization with trend analysis
- Seasonal pattern analysis
- Statistical summaries
- Export capabilities

### 🔄 **Comparison**
- Side-by-side comparison of MCD43A3 vs MOD10A1
- Correlation analysis with scatter plots
- Temporal alignment options
- Difference analysis
- Seasonal pattern comparison

### 🏔️ **Elevation Analysis**
- Elevation-dependent albedo patterns
- Williamson & Menounos (2021) methodology
- Transient snowline altitude estimation
- Multi-band trend analysis
- Seasonal variations by elevation

### 🔍 **Interactive Explorer**
- Maximum flexibility for custom analyses
- Multiple chart types (time series, correlations, distributions)
- Flexible date selection (full range, year range, custom dates, seasons)
- Real-time parameter adjustment
- Advanced export options

## Installation and Setup

### Prerequisites

1. **Python Environment**: Python 3.8 or higher
2. **Project Dependencies**: All existing project requirements
3. **Streamlit**: Added to requirements.txt

### Installation Steps

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Installation**:
   ```bash
   streamlit --version
   ```

### Running the App

1. **Navigate to Project Directory**:
   ```bash
   cd /path/to/saskatchewan-glacier-albedo-analysis
   ```

2. **Launch Streamlit App**:
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Access the App**:
   - The app will automatically open in your default browser
   - Default URL: http://localhost:8501
   - Use the sidebar to navigate between pages

## App Structure

```
streamlit_app.py                 # Main application entry point
pages/                          # Multi-page structure
├── 1_📊_Dataset_Analysis.py    # Individual dataset analysis
├── 2_🔄_Comparison.py          # Cross-dataset comparison  
├── 3_🏔️_Elevation_Analysis.py # Elevation-dependent analysis
└── 4_🔍_Interactive_Explorer.py # Custom analysis interface
streamlit_utils/                # Streamlit-specific utilities
├── __init__.py
├── data_loaders.py            # Cached data loading functions
├── plot_generators.py         # Plotly visualization functions
└── ui_components.py           # Reusable UI components
```

## Key Features

### 🎨 **Interactive Visualizations**
- **Plotly Integration**: All charts are interactive with zoom, pan, and hover
- **Real-time Updates**: Charts update automatically when parameters change
- **Multiple Chart Types**: Time series, scatter plots, heatmaps, distributions, box plots
- **Export Options**: Download plots in PNG, HTML, PDF, or SVG formats

### 📊 **Analysis Capabilities**
- **Trend Analysis**: Mann-Kendall tests with statistical significance
- **Seasonal Decomposition**: Monthly and seasonal pattern analysis
- **Correlation Analysis**: Cross-dataset correlation with regression lines
- **Quality Control**: Configurable data quality filtering
- **Statistical Summaries**: Comprehensive descriptive statistics

### ⚙️ **Flexible Configuration**
- **Dataset Selection**: Choose MCD43A3, MOD10A1, or both
- **Fraction Classes**: Select specific ice fraction classes
- **Date Ranges**: Full period, year ranges, custom dates, or specific seasons
- **Temporal Aggregation**: Daily, weekly, monthly, seasonal, or annual
- **Visualization Options**: Color schemes, confidence intervals, trend lines

### 💾 **Export and Sharing**
- **Plot Export**: High-resolution images and interactive HTML files
- **Data Export**: Filtered datasets and statistical summaries
- **Parameter Export**: Save analysis configurations
- **Shareable URLs**: Bookmark specific analysis configurations

## Usage Examples

### Basic Workflow

1. **Start with Dataset Analysis**:
   - Select MCD43A3 or MOD10A1
   - Choose fraction classes (e.g., pure_ice, mostly_ice)
   - Set date range (2010-2024 or custom)
   - Load data and explore time series

2. **Compare Datasets**:
   - Go to Comparison page
   - Select alignment method (daily, 16-day, monthly)
   - Analyze correlations and differences
   - Export comparison plots

3. **Explore Elevation Patterns**:
   - Navigate to Elevation Analysis
   - Select elevation bands of interest
   - Analyze seasonal patterns by elevation
   - Calculate transient snowline altitude

4. **Custom Analysis**:
   - Use Interactive Explorer for maximum flexibility
   - Try different chart types and aggregations
   - Export results for publications

### Advanced Features

- **Caching**: Data is cached for better performance
- **Session State**: Your selections persist while navigating
- **Error Handling**: Graceful handling of missing data or errors
- **Responsive Design**: Works on desktop and tablet devices

## Integration with Existing Workflow

### Relationship to CLI Interface

The Streamlit app **complements** the existing command-line interface:

- **CLI Interface** (`scripts/main.py`): 
  - Batch processing
  - Automated analysis pipelines
  - Script-based workflows
  - Production runs

- **Streamlit App**:
  - Interactive exploration
  - Parameter tuning
  - Visualization
  - Presentation and sharing

### Shared Components

Both interfaces use the same core modules:
- `config.py`: Configuration and settings
- `data/`: Data loading and management
- `analysis/`: Statistical analysis modules
- `visualization/`: Chart generation (extended for Plotly)

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   streamlit run streamlit_app.py --server.port 8502
   ```

2. **Module Import Errors**:
   - Ensure you're running from the project root directory
   - Check that all dependencies are installed

3. **Data Loading Issues**:
   - Verify CSV files exist in `data/csv/` directory
   - Check file permissions and formats

4. **Performance Issues**:
   - Clear cache using the app's cache management
   - Reduce date ranges for large datasets

### Getting Help

- **Streamlit Documentation**: https://docs.streamlit.io/
- **Plotly Documentation**: https://plotly.com/python/
- **Project Issues**: Create an issue in the project repository

## Future Enhancements

### Planned Features
- **Real-time Data Updates**: Integration with data pipelines
- **Advanced Analytics**: Machine learning models for prediction
- **Multi-site Analysis**: Extension to other glacier sites
- **Collaborative Features**: Shared analysis sessions

### Contributing
- Follow existing code style and patterns
- Test new features thoroughly
- Update documentation for new capabilities
- Consider backward compatibility with CLI interface

## Performance Optimization

### Caching Strategy
- **Dataset Loading**: Cached for 1 hour
- **Statistical Calculations**: Cached for 30 minutes
- **Plot Generation**: Dynamic based on parameters

### Memory Management
- **Lazy Loading**: Data loaded only when needed
- **Efficient Filtering**: SQL-style filtering for large datasets
- **Progressive Rendering**: Large plots rendered progressively

## Security and Deployment

### Local Development
- App runs locally by default
- No external data transmission

### Production Deployment
- Consider Streamlit Cloud or other hosting options
- Configure authentication if needed
- Set up monitoring and logging

## License and Credits

This Streamlit interface is part of the Saskatchewan Glacier Albedo Analysis project and follows the same licensing terms. The interface builds upon:

- **Streamlit**: Web app framework
- **Plotly**: Interactive visualization library
- **Existing Analysis Pipeline**: Core analysis modules

For citation and acknowledgments, see the main project README.