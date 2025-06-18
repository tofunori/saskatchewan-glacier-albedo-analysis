# MCD43A3 BRDF-Albedo Analysis Results

This directory contains all outputs related to MODIS MCD43A3 BRDF-Albedo product analysis for the Saskatchewan glacier.

## Product Information

**MODIS Product**: MCD43A3 (Combined Terra and Aqua BRDF-Albedo)  
**Spatial Resolution**: 500m  
**Temporal Resolution**: Daily  
**Primary Variables**: Shortwave albedo, quality flags  
**Analysis Period**: 2010-2024 (melt season: June-September)

## Directory Contents

### raw_data/
Contains original data downloads and exports:
- Google Earth Engine CSV exports
- Original MODIS HDF/TIFF files
- Unprocessed albedo time series data
- Quality flag information

### processed_data/
Contains cleaned and analysis-ready datasets:
- Quality-filtered albedo time series
- Fraction-based aggregated data
- Mann-Kendall ready datasets
- Temporally aligned data series

### trend_analysis/
Contains statistical analysis outputs:
- Mann-Kendall trend test results
- Sen's slope calculations
- Bootstrap confidence intervals
- Autocorrelation analysis
- Significance testing results

### figures/
Contains visualizations and plots:
- `trend_overview_{variable}.png` - Overview of trends across all fractions
- `seasonal_patterns_{variable}.png` - Monthly and seasonal patterns
- `correlation_matrix_{variable}.png` - Inter-fraction correlations
- `timeseries_{fraction}_{variable}.png` - Detailed time series by fraction
- `dashboard_summary_{variable}.png` - Comprehensive dashboard

### reports/
Contains analysis reports and summaries:
- `saskatchewan_albedo_analysis_{variable}_{timestamp}.xlsx` - Full Excel reports
- `saskatchewan_albedo_statistical_report_{variable}_{timestamp}.txt` - Text reports
- `saskatchewan_summary_{variable}_{timestamp}.csv` - Summary tables

## Analysis Variables

**Primary Variables**:
- `mean` - Mean albedo per pixel fraction
- `median` - Median albedo per pixel fraction

**Fraction Classes**:
- `border` (0-25% ice coverage)
- `mixed_low` (25-50% ice coverage)
- `mixed_high` (50-75% ice coverage)  
- `mostly_ice` (75-90% ice coverage)
- `pure_ice` (90-100% ice coverage)

## Key Analysis Results

### Trend Detection
- Mann-Kendall trend test for each fraction class
- Sen's slope estimator for trend magnitude
- Bootstrap confidence intervals
- Seasonal trend analysis (monthly)

### Quality Control
- Autocorrelation assessment (lag-1, lag-2, lag-3)
- Modified Mann-Kendall for autocorrelated data
- Pre-whitening techniques when needed
- Data availability and coverage analysis

### Temporal Patterns
- Inter-annual trends (2010-2024)
- Seasonal cycles and anomalies
- Monthly trend variations
- Coverage fraction stability

## Data Quality Considerations

### Pixel Coverage
- Minimum 10 valid observations required for analysis
- Quality flags 0-1 accepted (good to moderate quality)
- Cloud contamination filtering applied
- Fraction-based aggregation reduces noise

### Statistical Significance
- p < 0.05 for significant trends
- Multiple significance levels tested (0.001, 0.01, 0.05)
- Bootstrap validation of trend estimates
- Autocorrelation correction applied where needed

## Usage Examples

### Loading Analysis Results
```python
import pandas as pd

# Load latest summary
summary = pd.read_csv('reports/saskatchewan_summary_mean_latest.csv')

# Load full time series
data = pd.read_csv('processed_data/daily_albedo_mann_kendall_ready_2010_2024.csv')
```

### Accessing Configuration
```python
from config import get_output_path, ALBEDO_PATHS

# Get organized paths
figures_dir = ALBEDO_PATHS['figures']
reports_dir = ALBEDO_PATHS['reports']
```

## File Patterns

### Raw Data
- `*_albedo_*.csv` - Google Earth Engine exports
- `*MCD43A3*.tif` - MODIS TIFF files
- `daily_albedo_*_2010_2024.csv` - Complete time series

### Processed Data  
- `*_mann_kendall_ready*.csv` - Analysis-ready datasets
- `*_quality_filtered*.csv` - Quality-controlled data
- `*_by_fraction*.csv` - Fraction-aggregated data

### Analysis Outputs
- `*_trends_*.csv` - Trend analysis results
- `*_bootstrap_*.csv` - Bootstrap results
- `*_autocorr_*.csv` - Autocorrelation analysis

## Related Products

See also:
- `../MOD10A1_snow_cover/` - Terra snow cover validation data
- `../MYD10A1_aqua_snow/` - Aqua snow cover validation data  
- `../combined_analysis/` - Multi-product integration

---

**Last Updated**: 2024-06-18  
**Analysis Package**: Saskatchewan Albedo Trend Analysis v2.0