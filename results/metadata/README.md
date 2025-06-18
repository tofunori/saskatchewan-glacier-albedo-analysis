# Metadata and Documentation Directory

This directory contains project metadata, processing logs, data quality reports, and configuration snapshots for the Saskatchewan glacier albedo analysis.

## Directory Contents

### processing_logs/
Analysis execution logs and migration records:
- **Migration logs**: Records of file structure reorganization
- **Analysis logs**: Detailed processing steps and timing
- **Error logs**: Issues encountered during analysis
- **Performance logs**: Execution time and resource usage

### data_quality_reports/
Data quality assessment and validation reports:
- **Coverage reports**: Spatial and temporal data availability
- **Quality flag analysis**: Distribution of MODIS quality indicators
- **Missing data assessment**: Gap analysis and impact evaluation
- **Cross-product validation**: Inter-product consistency checks

### configuration_snapshots/
Saved analysis configuration states:
- **Parameter settings**: Analysis configuration backups
- **Version control**: Analysis package version history
- **Reproducibility records**: Complete analysis state capture
- **Change documentation**: Configuration evolution tracking

## File Types and Patterns

### Processing Logs
```
migration_log_YYYYMMDD_HHMMSS.txt          # File migration records
analysis_execution_YYYYMMDD_HHMMSS.log     # Analysis runtime logs  
error_report_YYYYMMDD_HHMMSS.log           # Error and warning logs
performance_profile_YYYYMMDD_HHMMSS.log    # Performance metrics
```

### Data Quality Reports
```
data_coverage_report_YYYYMMDD.csv          # Spatial-temporal coverage
quality_flag_distribution_YYYYMMDD.csv     # MODIS quality statistics
missing_data_analysis_YYYYMMDD.csv         # Gap analysis results
cross_validation_report_YYYYMMDD.csv       # Multi-product validation
```

### Configuration Snapshots
```
config_snapshot_YYYYMMDD_HHMMSS.json       # Complete configuration state
analysis_parameters_YYYYMMDD.yaml          # Analysis parameter settings
version_info_YYYYMMDD.txt                  # Software version information
reproducibility_record_YYYYMMDD.json       # Full reproducibility metadata
```

## Key Metadata Components

### 1. Processing Documentation

#### Migration Records
- **File movements**: Complete log of structure reorganization
- **Backup locations**: Pre-migration backup directory paths
- **Conflict resolution**: How file naming conflicts were handled
- **Verification**: Post-migration integrity checks

#### Analysis Execution
- **Processing timeline**: Start/end times for each analysis step
- **Resource usage**: Memory, CPU, and disk utilization
- **Error handling**: Issues encountered and resolution
- **Performance metrics**: Execution efficiency tracking

### 2. Data Quality Tracking

#### Coverage Assessment
```python
# Example coverage report structure
coverage_metrics = {
    'temporal_coverage': {
        'start_date': '2010-06-01',
        'end_date': '2024-09-30',
        'total_days': 5234,
        'available_days': 4987,
        'coverage_percentage': 95.3
    },
    'spatial_coverage': {
        'total_pixels': 1547,
        'valid_pixels': 1398,
        'coverage_percentage': 90.4
    },
    'fraction_coverage': {
        'border': {'available_days': 4234, 'percentage': 80.9},
        'mixed_low': {'available_days': 4756, 'percentage': 90.9},
        # ... other fractions
    }
}
```

#### Quality Flag Analysis
- **Distribution statistics**: Frequency of each quality level
- **Temporal patterns**: Quality variations over time
- **Spatial patterns**: Quality variations across glacier
- **Seasonal effects**: Quality changes during melt season

### 3. Configuration Management

#### Version Control
- **Analysis package versions**: Software version tracking
- **Parameter evolution**: Changes to analysis settings over time
- **Reproducibility metadata**: Complete environment capture
- **Dependency tracking**: External library versions

#### Analysis Parameters
```yaml
# Example configuration snapshot
analysis_config:
  version: "2.0"
  date: "2024-06-18"
  parameters:
    bootstrap_iterations: 1000
    significance_levels: [0.001, 0.01, 0.05]
    quality_threshold: 10
    autocorr_thresholds:
      weak: 0.1
      moderate: 0.3
      strong: 0.5
  data_sources:
    primary_csv: "daily_albedo_mann_kendall_ready_2010_2024.csv"
    modis_products: ["MCD43A3", "MOD10A1", "MYD10A1"]
  output_structure:
    base_dir: "results"
    organized: true
    version: "2.0"
```

## Quality Assurance

### Automated Checks
- **Data integrity**: Checksum validation of processed files
- **Completeness**: Verification of expected outputs
- **Consistency**: Cross-product validation metrics
- **Format compliance**: File format and structure validation

### Manual Review
- **Scientific validity**: Expert review of analysis results
- **Methodological soundness**: Statistical approach validation
- **Documentation completeness**: Metadata coverage assessment
- **Reproducibility testing**: Independent analysis replication

## Maintenance and Archival

### Regular Maintenance
- **Log rotation**: Periodic cleanup of old log files
- **Archive creation**: Long-term storage of important metadata
- **Backup verification**: Regular backup integrity checks
- **Update documentation**: Keep metadata current with changes

### Archival Strategy
- **Retention periods**: How long to keep different metadata types
- **Compression**: Efficient storage of historical logs
- **Access procedures**: How to retrieve archived metadata
- **Migration planning**: Future metadata format transitions

## Usage Examples

### Loading Quality Reports
```python
import pandas as pd
import json

# Load data coverage report
coverage = pd.read_csv('data_quality_reports/data_coverage_report_20240618.csv')

# Load configuration snapshot
with open('configuration_snapshots/config_snapshot_20240618_120000.json', 'r') as f:
    config = json.load(f)
```

### Generating Quality Reports
```python
def generate_quality_report(data, output_path):
    """Generate comprehensive data quality report"""
    quality_metrics = {
        'coverage_stats': calculate_coverage_statistics(data),
        'quality_distribution': analyze_quality_flags(data),
        'temporal_gaps': identify_temporal_gaps(data),
        'spatial_patterns': assess_spatial_coverage(data)
    }
    
    # Save report
    pd.DataFrame(quality_metrics).to_csv(output_path)
    return quality_metrics
```

### Creating Configuration Snapshots
```python
def create_config_snapshot():
    """Create complete configuration snapshot for reproducibility"""
    from config import *
    import json
    from datetime import datetime
    
    snapshot = {
        'timestamp': datetime.now().isoformat(),
        'analysis_config': ANALYSIS_CONFIG,
        'export_config': EXPORT_CONFIG,
        'output_structure': OUTPUT_STRUCTURE,
        'fraction_classes': FRACTION_CLASSES,
        'class_labels': CLASS_LABELS,
        'version_info': get_version_info()
    }
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'configuration_snapshots/config_snapshot_{timestamp}.json'
    
    with open(filename, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    return filename
```

## Integration with Analysis

### Automated Logging
- Analysis scripts automatically generate logs
- Configuration snapshots created at analysis start
- Quality reports generated post-processing
- Error tracking integrated into all workflows

### Reproducibility Support
- Complete parameter capture for replication
- Version tracking for software dependencies
- Data provenance documentation
- Analysis workflow documentation

## Related Documentation

- `../README.md` - Main results directory overview
- `../MCD43A3_albedo/README.md` - Primary analysis documentation
- `../../migrate_to_organized_structure.py` - Migration script documentation
- `../../config.py` - Analysis configuration documentation

---

**Last Updated**: 2024-06-18  
**Analysis Package**: Saskatchewan Albedo Trend Analysis v2.0  
**Metadata Framework**: Comprehensive Analysis Documentation