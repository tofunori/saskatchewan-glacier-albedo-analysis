# MOD10A1 Terra Snow Cover Analysis Results

This directory contains outputs related to MODIS MOD10A1 Terra Snow Cover product analysis for the Saskatchewan glacier region.

## Product Information

**MODIS Product**: MOD10A1 (Terra Daily Snow Cover)  
**Spatial Resolution**: 500m  
**Temporal Resolution**: Daily  
**Primary Variables**: Snow cover extent, quality assessment  
**Analysis Period**: 2010-2024 (melt season: June-September)

## Purpose

The MOD10A1 data serves as:
- **Validation** for albedo-derived snow patterns
- **Correlation analysis** with albedo trends
- **Independent snow cover assessment**
- **Cloud-gap filling** for albedo analysis

## Directory Contents

### raw_data/
Contains original Terra snow cover downloads:
- MOD10A1 HDF files from NASA DAAC
- Google Earth Engine snow cover exports
- Original quality flag datasets
- Geometric correction information

### processed_data/
Contains processed snow cover data:
- Cloud-filtered snow cover maps
- Fraction-based snow cover aggregation
- Temporal gap-filled series
- Quality-controlled daily data

### analysis/
Contains snow cover analysis results:
- Snow cover trend analysis
- Correlation with albedo patterns
- Seasonal snow cycle characterization
- Coverage statistics and trends

### figures/
Contains snow cover visualizations:
- Snow cover extent time series
- Seasonal snow patterns
- Albedo-snow cover correlations
- Trend comparison plots

## Key Variables

### Snow Cover Products
- **Snow Cover Extent**: Binary snow/no-snow classification
- **Fractional Snow Cover**: Sub-pixel snow fraction estimates  
- **Quality Assessment**: Pixel reliability flags

### Analysis Metrics
- Daily snow coverage percentage
- Seasonal snow onset/melt dates
- Snow persistence duration
- Inter-annual variability

## Analysis Integration

### Albedo Validation
- Correlation between snow extent and albedo values
- Validation of albedo-based snow detection
- Cross-sensor consistency assessment

### Trend Comparison
- Snow cover trends vs. albedo trends
- Seasonal pattern differences
- Fraction-specific correlations

### Quality Enhancement
- Cloud masking for albedo analysis
- Gap-filling using snow cover information
- Multi-sensor data fusion

## Data Quality

### Processing Standards
- NASA standard algorithms applied
- Cloud detection and screening
- Geometric and radiometric corrections
- Quality flag interpretation

### Validation Metrics
- Agreement with ground observations
- Cross-validation with Aqua snow product
- Temporal consistency checks
- Spatial coherence assessment

## Usage Examples

### Loading Snow Cover Data
```python
import pandas as pd
import rasterio

# Load processed time series
snow_data = pd.read_csv('processed_data/MOD10A1_daily_snow_cover_2010_2024.csv')

# Load spatial snow cover map
with rasterio.open('processed_data/MOD10A1_seasonal_mean_2020.tif') as src:
    snow_map = src.read(1)
```

### Analysis Integration
```python
# Load both albedo and snow data for correlation
albedo_data = pd.read_csv('../MCD43A3_albedo/processed_data/daily_albedo_by_fraction.csv')
snow_data = pd.read_csv('processed_data/MOD10A1_daily_snow_cover.csv')

# Merge on date
combined = pd.merge(albedo_data, snow_data, on='date')
```

## File Patterns

### Raw Data
- `MOD10A1.A*.hdf` - Original MODIS files
- `*_snow_cover_*.csv` - GEE exports
- `*_quality_*.csv` - Quality flag data

### Processed Data
- `*_daily_snow_*.csv` - Daily snow cover series
- `*_gap_filled_*.csv` - Temporally interpolated data
- `*_by_fraction_*.csv` - Fraction-aggregated data

### Analysis Results
- `*_snow_trends_*.csv` - Snow cover trend analysis
- `*_albedo_correlation_*.csv` - Albedo-snow correlations
- `*_seasonal_stats_*.csv` - Seasonal characterization

## Quality Flags

### MOD10A1 Quality Interpretation
- **0**: Best quality
- **1**: Good quality
- **2**: OK quality (marginal)
- **3**: Poor quality (not recommended)

### Processing Flags
- Cloud contamination screening
- Sensor zenith angle filtering
- Temporal consistency checks

## Related Analysis

See also:
- `../MCD43A3_albedo/` - Primary albedo analysis
- `../MYD10A1_aqua_snow/` - Aqua snow cover complement
- `../combined_analysis/` - Multi-product integration

---

**Last Updated**: 2024-06-18  
**Analysis Package**: Saskatchewan Albedo Trend Analysis v2.0