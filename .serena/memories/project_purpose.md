# Project Purpose

## Saskatchewan Glacier Albedo Analysis

This project is a comprehensive Python package for analyzing albedo evolution for Saskatchewan Glacier using MODIS satellite data from Google Earth Engine (2010-2024).

### Main Goals:
- **Temporal Analysis**: Study albedo trends over 15-year period (2010-2024)
- **Multi-Dataset Support**: Analyze both MCD43A3 (general albedo) and MOD10A1 (snow albedo) datasets
- **Quality Assessment**: Comprehensive data quality filtering and pixel coverage analysis
- **Seasonal Patterns**: Focus on summer months (June-September) when albedo measurements are most relevant
- **Statistical Analysis**: Trend analysis with significance testing using Mann-Kendall tests
- **Visualization**: Generate comprehensive charts, maps, and temporal evolution plots

### Key Research Focus:
- Understanding glacier melt dynamics through albedo changes
- Detection of climate change impacts on glacier surface properties
- Spatial and temporal pattern analysis for glaciological research

### Data Sources:
- **MODIS MCD43A3**: 500m resolution, 16-day composite albedo data
- **MODIS MOD10A1**: Daily snow cover albedo data
- **Google Earth Engine**: Data processing and export platform
- **Quality Filtering**: Only pixels with quality flags ≤ 1 are included