# Saskatchewan Glacier Albedo Analysis Dashboard

## Overview

Interactive web dashboard for exploring 15 years (2010-2024) of Saskatchewan Glacier albedo data from MODIS satellite observations. Built with Python Shiny and Plotly for comprehensive data analysis and visualization.

## Features

### 🏔️ Core Capabilities
- **Dual Dataset Support**: MCD43A3 (general albedo) and MOD10A1 (snow albedo)
- **Interactive Time Series**: Pan, zoom, and explore temporal patterns
- **Statistical Analysis**: Mann-Kendall trend tests, seasonal decomposition
- **Multi-Dataset Comparison**: Side-by-side analysis of different MODIS products
- **Quality Assessment**: Data coverage and reliability metrics

### 📊 Analysis Tools
- **Trend Detection**: Statistical significance testing with multiple methods
- **Seasonal Patterns**: Monthly and day-of-year analysis
- **Fraction Classes**: 5 glacier coverage categories (0-25% to 90-100%)
- **Real-time Filtering**: Date ranges, quality thresholds, fraction selection
- **Export Capabilities**: Data and visualizations in multiple formats

### 🎯 Interactive Features
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Analysis updates as you change filters
- **Hover Details**: Rich tooltips with contextual information
- **Customizable Views**: Toggle trends, seasonal patterns, confidence intervals

## Quick Start

### Requirements
```bash
# Install dependencies
pip install -r requirements.txt
```

Required packages:
- shiny >= 1.0.0
- plotly >= 5.0.0
- pandas >= 1.5.0
- numpy >= 1.21.0
- pymannkendall >= 1.4.3

### Launch Dashboard

**Option 1: Python Script**
```bash
python dashboard/run_dashboard.py
```

**Option 2: Direct App Launch**
```bash
cd dashboard
python app.py
```

**Option 3: Windows Batch File**
```cmd
dashboard\run_dashboard.bat
```

### Access Dashboard
- Open browser to: http://127.0.0.1:8000
- Dashboard loads automatically with default settings
- Use sidebar controls to customize analysis

## Dashboard Structure

### 📂 Files
- `app.py` - Main Shiny application
- `components.py` - UI component definitions
- `plots.py` - Interactive plotting functions
- `run_dashboard.py` - Launch script
- `run_dashboard.bat` - Windows launcher

### 🎛️ User Interface

#### Sidebar Controls
1. **Dataset Selection** - Choose MCD43A3, MOD10A1, or comparison mode
2. **Data Filters** - Fraction classes, date ranges, quality thresholds
3. **Analysis Options** - Variable selection, trend methods, display options
4. **Advanced Filters** - Seasonal focus, pixel thresholds, quality classes
5. **Export Panel** - Download data and visualizations
6. **Info Panel** - Dataset documentation and metadata

#### Main Tabs
1. **📈 Time Series** - Interactive temporal analysis with trend detection
2. **📊 Statistical Analysis** - Comprehensive trend and seasonal statistics
3. **🔄 Dataset Comparison** - Multi-dataset correlation and difference analysis
4. **🏔️ Elevation Analysis** - Elevation-stratified albedo patterns
5. **📋 Data Quality** - Coverage metrics and quality assessment

## Data Requirements

### Input Files (in `data/csv/`)
- `daily_albedo_mann_kendall_ready_2010_2024.csv` (MCD43A3)
- `daily_snow_albedo_mann_kendall_mod10a1_2010_2024.csv` (MOD10A1)
- `global_quality_distribution_daily_2010_2024.csv` (MCD43A3 quality)
- `snow_quality_distribution_daily_mod10a1_2010_2024.csv` (MOD10A1 quality)

### Expected Columns
- `date` - Date in YYYY-MM-DD format
- `{fraction}_{variable}` - Albedo values (e.g., `pure_ice_mean`)
- `month`, `year`, `day_of_year` - Temporal variables
- Quality columns (dataset-specific)

## Usage Examples

### Basic Analysis
1. Select dataset (MCD43A3 or MOD10A1)
2. Choose fraction classes of interest
3. Set date range
4. View time series and trends

### Comparative Analysis
1. Switch to "Compare Datasets" mode
2. Select matching fraction classes
3. Examine correlation and differences
4. Download comparison results

### Seasonal Analysis
1. Enable "Highlight Seasonal Patterns"
2. Focus on specific seasons using advanced filters
3. Examine monthly and day-of-year patterns
4. Export seasonal statistics

## Technical Details

### Architecture
- **Framework**: Python Shiny for reactive web applications
- **Visualization**: Plotly for interactive charts
- **Analysis**: Integration with existing Saskatchewan glacier analysis modules
- **Data Handling**: Pandas for efficient data manipulation

### Performance
- **Caching**: Reactive computations cache data for speed
- **Filtering**: Client-side filtering for responsive interactions
- **Plotting**: Efficient Plotly rendering with selective updates

### Integration
- **Existing Codebase**: Seamless integration with analysis modules
- **Configuration**: Uses existing `config.py` settings
- **Data Pipeline**: Compatible with current CSV export workflow

## Troubleshooting

### Common Issues

**Dashboard won't start:**
```bash
# Check requirements
pip install -r requirements.txt

# Verify Python version (3.8+)
python --version

# Check file permissions
ls -la dashboard/
```

**Data not loading:**
- Verify CSV files exist in `data/csv/`
- Check file formats match expected structure
- Review console for error messages

**Plots not displaying:**
- Ensure Plotly is installed and up-to-date
- Check browser JavaScript console
- Try refreshing the page

### Performance Tips
- Filter data to reasonable date ranges for large datasets
- Limit number of fraction classes for complex analyses
- Use quality thresholds to focus on reliable data

## Development

### Adding New Features
1. Define UI components in `components.py`
2. Implement plotting functions in `plots.py`
3. Add server logic to `app.py`
4. Test with sample data

### Customization
- Modify `components.py` for different UI layouts
- Extend `plots.py` for additional visualization types
- Update `config.py` for new datasets or parameters

## Support

For issues or questions:
1. Check existing analysis documentation in parent directory
2. Review error messages in console output
3. Verify data file formats and availability

---

*Built for the Saskatchewan Glacier Albedo Analysis project - Interactive exploration of 15 years of MODIS satellite data*