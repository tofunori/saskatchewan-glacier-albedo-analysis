# MYD10A1 Aqua Snow Cover Analysis Results

This directory contains outputs related to MODIS MYD10A1 Aqua Snow Cover product analysis for the Saskatchewan glacier region.

## Product Information

**MODIS Product**: MYD10A1 (Aqua Daily Snow Cover)  
**Spatial Resolution**: 500m  
**Temporal Resolution**: Daily  
**Primary Variables**: Snow cover extent, quality assessment  
**Analysis Period**: 2010-2024 (melt season: June-September)  
**Overpass Time**: ~1:30 PM local time

## Purpose

The MYD10A1 data provides:
- **Complementary observations** to Terra (MOD10A1)
- **Afternoon snow conditions** vs. morning observations
- **Enhanced temporal sampling** with Terra combination
- **Cross-validation** of snow cover patterns

## Directory Contents

### raw_data/
Contains original Aqua snow cover downloads:
- MYD10A1 HDF files from NASA DAAC
- Google Earth Engine snow cover exports
- Quality assessment datasets
- Geometric and projection information

### processed_data/
Contains processed Aqua snow cover data:
- Cloud-screened snow cover maps
- Diurnal difference analysis (vs. Terra)
- Combined Terra-Aqua products
- Quality-enhanced daily series

### analysis/
Contains Aqua-specific analysis results:
- Diurnal snow cover variations
- Terra-Aqua comparison statistics
- Aqua-albedo correlations
- Afternoon melt detection

### figures/
Contains Aqua snow cover visualizations:
- Terra vs. Aqua comparison plots
- Diurnal snow cover differences
- Combined snow cover products
- Temporal sampling improvements

## Key Analysis Aspects

### Diurnal Analysis
- **Morning vs. Afternoon**: Terra (~10:30 AM) vs. Aqua (~1:30 PM)
- **Daily melt progression**: Snow loss during daytime
- **Seasonal diurnal patterns**: Changes throughout melt season

### Multi-Sensor Integration
- Combined Terra-Aqua snow products
- Enhanced cloud-gap filling
- Improved temporal resolution
- Cross-sensor validation

### Albedo Correlation
- Afternoon albedo-snow relationships
- Diurnal albedo variations
- Snow metamorphism effects
- Melt-refreeze cycle detection

## Data Quality Considerations

### Aqua-Specific Factors
- Later overpass time affects snow detection
- Higher solar zenith angles
- Different atmospheric conditions
- Potential diurnal bias

### Quality Enhancement
- Terra-Aqua cross-validation
- Cloud screening optimization
- Temporal consistency checks
- Spatial coherence assessment

## Usage Examples

### Loading Aqua Snow Data
```python
import pandas as pd
import numpy as np

# Load Aqua snow cover time series
aqua_snow = pd.read_csv('processed_data/MYD10A1_daily_snow_cover_2010_2024.csv')

# Load Terra-Aqua comparison
comparison = pd.read_csv('analysis/terra_aqua_snow_comparison.csv')
```

### Diurnal Analysis
```python
# Compare morning (Terra) vs afternoon (Aqua) snow cover
terra_data = pd.read_csv('../MOD10A1_snow_cover/processed_data/MOD10A1_daily_snow_cover.csv')
aqua_data = pd.read_csv('processed_data/MYD10A1_daily_snow_cover.csv')

# Calculate diurnal differences
merged = pd.merge(terra_data, aqua_data, on='date', suffixes=('_terra', '_aqua'))
merged['diurnal_diff'] = merged['snow_cover_aqua'] - merged['snow_cover_terra']
```

### Combined Product Creation
```python
# Create enhanced snow cover product using both sensors
def combine_snow_products(terra_snow, aqua_snow, weights=[0.6, 0.4]):
    """Combine Terra and Aqua snow products with temporal weighting"""
    combined = weights[0] * terra_snow + weights[1] * aqua_snow
    return combined
```

## File Patterns

### Raw Data
- `MYD10A1.A*.hdf` - Original Aqua MODIS files
- `*_aqua_snow_*.csv` - GEE Aqua exports
- `*_MYD10A1_quality_*.csv` - Aqua quality flags

### Processed Data
- `*_aqua_daily_snow_*.csv` - Daily Aqua snow series
- `*_terra_aqua_combined_*.csv` - Combined products
- `*_diurnal_differences_*.csv` - Morning-afternoon differences

### Analysis Results
- `*_aqua_trends_*.csv` - Aqua-specific trends
- `*_diurnal_analysis_*.csv` - Diurnal variation analysis
- `*_cross_sensor_validation_*.csv` - Terra-Aqua validation

## Quality Assessment

### MYD10A1 Quality Flags
- **0**: Best quality (cloud-free, good observation)
- **1**: Good quality (minor issues)
- **2**: OK quality (significant uncertainty)
- **3**: Poor quality (not recommended for analysis)

### Diurnal Quality Factors
- Solar illumination differences
- Atmospheric path variations
- Snow metamorphism effects
- Temperature-dependent snow properties

## Cross-Sensor Validation

### Agreement Metrics
- Pixel-level correspondence with Terra
- Seasonal agreement patterns
- Fraction-specific correlations
- Temporal consistency assessment

### Divergence Analysis
- Systematic diurnal differences
- Weather-dependent variations
- Topographic effects on observations
- Snow type and condition influences

## Integration with Primary Analysis

### Albedo Enhancement
- Improved cloud masking for albedo
- Enhanced temporal sampling
- Diurnal albedo pattern validation
- Snow-albedo relationship refinement

### Trend Analysis Support
- Cross-validation of albedo trends
- Independent snow cover trends
- Diurnal trend variations
- Enhanced uncertainty assessment

## Related Products

See also:
- `../MCD43A3_albedo/` - Primary albedo analysis
- `../MOD10A1_snow_cover/` - Terra snow cover (morning)
- `../combined_analysis/` - Multi-product integration and comparison

---

**Last Updated**: 2024-06-18  
**Analysis Package**: Saskatchewan Albedo Trend Analysis v2.0