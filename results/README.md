# Saskatchewan Glacier Albedo Analysis - Results Directory

This directory contains all outputs, results, and generated data from the Saskatchewan glacier albedo analysis project, organized by MODIS product type and data category.

## Directory Structure

```
results/
├── MCD43A3_albedo/         # BRDF-Albedo product (primary albedo data)
│   ├── raw_data/           # Original GEE exports, downloaded files
│   ├── processed_data/     # Cleaned, filtered datasets
│   ├── trend_analysis/     # Statistical analysis outputs
│   ├── figures/           # Plots, charts, visualizations
│   └── reports/           # Excel, text, summary reports
├── MOD10A1_snow_cover/     # Terra Snow Cover product
│   ├── raw_data/          # Downloaded MOD10A1 files
│   ├── processed_data/    # Processed snow cover data
│   ├── analysis/          # Snow cover analysis results
│   └── figures/           # Snow cover visualizations
├── MYD10A1_aqua_snow/      # Aqua Snow Cover product
│   ├── raw_data/          # Downloaded MYD10A1 files
│   ├── processed_data/    # Processed Aqua snow data
│   ├── analysis/          # Aqua snow analysis results
│   └── figures/           # Aqua snow visualizations
├── combined_analysis/      # Multi-product comparisons and integration
│   ├── multi_product_comparisons/  # Cross-product analysis
│   ├── integrated_reports/         # Combined analysis reports
│   └── summary_figures/           # Summary visualizations
└── metadata/              # Project metadata and documentation
    ├── processing_logs/   # Analysis logs and migration records
    ├── data_quality_reports/  # Data quality assessments
    └── configuration_snapshots/  # Saved configuration states
```

## MODIS Products Overview

### MCD43A3 - BRDF-Albedo (Primary Product)
- **Source**: Combined Terra and Aqua observations
- **Resolution**: 500m, daily
- **Primary Use**: Albedo trend analysis
- **Key Variables**: Shortwave albedo, quality flags

### MOD10A1 - Terra Snow Cover
- **Source**: Terra satellite
- **Resolution**: 500m, daily  
- **Primary Use**: Snow cover validation and correlation
- **Key Variables**: Snow cover extent, quality assessment

### MYD10A1 - Aqua Snow Cover
- **Source**: Aqua satellite
- **Resolution**: 500m, daily
- **Primary Use**: Complementary snow cover analysis
- **Key Variables**: Snow cover extent, quality assessment

## Data Categories

### Raw Data
- Original downloads from Google Earth Engine
- Unprocessed MODIS HDF/TIFF files
- GEE export CSV files with pixel-level data

### Processed Data
- Quality-filtered datasets
- Temporally aggregated data
- Fraction-based albedo time series
- Analysis-ready CSV files

### Analysis Results
- Mann-Kendall trend test outputs
- Sen's slope calculations
- Bootstrap confidence intervals
- Autocorrelation analysis results

### Figures
- Trend overview plots
- Seasonal pattern visualizations
- Correlation matrices
- Time series plots
- Dashboard summaries

### Reports
- Excel workbooks with comprehensive results
- Statistical analysis text reports
- Summary CSV files for external use

## Glacier Fraction Classes

The analysis organizes data by glacier coverage fractions:

- **Border (0-25%)**: Edge regions with minimal ice coverage
- **Mixed Low (25-50%)**: Areas with low ice fraction
- **Mixed High (50-75%)**: Areas with moderate ice fraction  
- **Mostly Ice (75-90%)**: Predominantly ice-covered areas
- **Pure Ice (90-100%)**: Nearly complete ice coverage

## File Naming Conventions

### Analysis Output Files
- `saskatchewan_albedo_analysis_{variable}_{timestamp}.xlsx`
- `saskatchewan_albedo_statistical_report_{variable}_{timestamp}.txt`
- `saskatchewan_summary_{variable}_{timestamp}.csv`

### Figure Files
- `trend_overview_{variable}.png`
- `seasonal_patterns_{variable}.png`
- `correlation_matrix_{variable}.png`
- `timeseries_{fraction}_{variable}.png`
- `dashboard_summary_{variable}.png`

### Raw Data Files
- `daily_albedo_*_{start_year}_{end_year}.csv`
- `*_MCD43A3_*.tif`
- `*_MOD10A1_*.tif`
- `*_MYD10A1_*.tif`

## Migration from Legacy Structure

If migrating from the old structure, use the provided migration script:

```bash
# Dry run to see what would be moved
python migrate_to_organized_structure.py --dry-run --verbose

# Perform actual migration  
python migrate_to_organized_structure.py --verbose
```

This will:
- Move files to appropriate organized locations
- Create backups of the original structure
- Generate migration logs for reference

## Data Access and Usage

### Configuration Integration
The new structure is integrated with the analysis configuration:

```python
from config import get_output_path

# Get organized output paths
figures_dir = get_output_path('MCD43A3_albedo', 'figures')
reports_dir = get_output_path('MCD43A3_albedo', 'reports')
```

### Version Control
- Data files are excluded from git tracking via `.gitignore`
- README files and structure documentation are tracked
- Configuration snapshots preserve analysis settings

## Maintenance

- Run regular data quality checks in `metadata/data_quality_reports/`
- Review processing logs for analysis errors
- Update configuration snapshots when changing analysis parameters
- Archive old results periodically to prevent disk space issues

---

**Generated**: 2024-06-18  
**Analysis Package**: Saskatchewan Albedo Trend Analysis v2.0  
**Contact**: Generated with Claude Code Analysis