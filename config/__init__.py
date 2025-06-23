"""
Configuration package for Saskatchewan Glacier Albedo Analysis.
"""

from .settings import (
    config,
    ConfigManager,
    DatasetConfig,
    ElevationConfig,
    ComparisonConfig,
    VisualizationConfig,
    
    # Legacy exports for backward compatibility
    DEFAULT_DATASET,
    DATA_MODE,
    OUTPUT_DIR,
    ANALYSIS_VARIABLE,
    FRACTION_CLASSES,
    CLASS_LABELS,
    MCD43A3_CONFIG,
    MOD10A1_CONFIG,
    ELEVATION_CONFIG,
    COMPARISON_CONFIG,
    CSV_PATH,
    QA_CSV_PATH,
    print_config_summary
)

__all__ = [
    'config',
    'ConfigManager',
    'DatasetConfig',
    'ElevationConfig', 
    'ComparisonConfig',
    'VisualizationConfig',
    'DEFAULT_DATASET',
    'DATA_MODE',
    'OUTPUT_DIR',
    'ANALYSIS_VARIABLE',
    'FRACTION_CLASSES',
    'CLASS_LABELS',
    'MCD43A3_CONFIG',
    'MOD10A1_CONFIG',
    'ELEVATION_CONFIG',
    'COMPARISON_CONFIG',
    'CSV_PATH',
    'QA_CSV_PATH',
    'print_config_summary'
]