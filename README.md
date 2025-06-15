# Saskatchewan Glacier Albedo Analysis

Analysis of albedo evolution for Saskatchewan Glacier using Google Earth Engine (2010-2024).

## Overview

This project analyzes the temporal evolution of surface albedo for Saskatchewan Glacier using MODIS satellite data. The analysis covers the period from 2010 to 2024, focusing on summer months (June-September) when albedo measurements are most relevant for understanding glacier melt dynamics.

## Data Source

- **Satellite Data**: MODIS MCD43A3 (500m resolution)
- **Albedo Type**: White Sky Albedo (WSA) - shortwave
- **Quality Filtering**: Only pixels with quality flags ≤ 1 are included
- **Temporal Coverage**: Daily observations, 2010-2024
- **Spatial Coverage**: Saskatchewan Glacier, Canadian Rockies

## Key Features

1. **Annual Analysis**
   - Summer mean albedo calculation (June-September)
   - Trend analysis over 15-year period
   - Statistical significance testing

2. **Daily Analysis**
   - High-resolution temporal dynamics
   - Quality assessment per observation
   - Seasonal patterns identification

3. **Spatial Analysis**
   - Pixel-level coverage assessment
   - Change detection between periods
   - Visualization of spatial patterns

## Files

- `saskatchewan_glacier_albedo_analysis_complete.js` - Main analysis script for Google Earth Engine
- `test_pixel_coverage.js` - Test script for pixel coverage threshold analysis

## Key Findings

- **Trend**: Decreasing albedo trend of -0.0075 per year (2010-2024)
- **Coverage**: Analysis uses pixels with ≥50% coverage within glacier mask
- **Data Quality**: Comprehensive quality filtering ensures robust results

## Usage

1. Open Google Earth Engine Code Editor
2. Copy the script content
3. Ensure access to the glacier mask asset: `projects/tofunori/assets/Saskatchewan_glacier_2024_updated`
4. Run the script

## Outputs

- CSV files with annual and daily statistics
- GeoTIFF images of albedo maps
- Temporal evolution charts
- Statistical analysis results

## Author

Created for glaciological research on Saskatchewan Glacier dynamics.

## License

This project is open source and available for research purposes.