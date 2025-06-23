"""
Configuration Management for Saskatchewan Glacier Albedo Analysis
================================================================

Centralized configuration with validation and environment support.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
import seaborn as sns

# Fix Qt platform plugin warnings in WSL/headless environments
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')


@dataclass
class DatasetConfig:
    """Configuration for a single dataset."""
    name: str
    description: str
    csv_path: str
    qa_csv_path: str
    quality_levels: List[str]
    temporal_resolution: str
    scaling_info: str
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.csv_path:
            raise ValueError(f"csv_path required for dataset {self.name}")


@dataclass
class ElevationConfig:
    """Configuration for elevation analysis."""
    csv_path: str
    name: str
    description: str
    elevation_zones: List[str] = field(default_factory=lambda: ['above_median', 'at_median', 'below_median'])
    fraction_classes: List[str] = field(default_factory=lambda: ['mostly_ice', 'pure_ice'])
    output_dir: str = 'results/elevation_analysis'
    methodology: str = 'Williamson_Menounos_2021_adapted_with_fractions'
    reference_paper: str = 'Williamson, S.N. & Menounos, B. (2021). Remote Sensing of Environment 267'
    
    @property
    def combinations(self) -> int:
        """Calculate number of elevation-fraction combinations."""
        return len(self.fraction_classes) * len(self.elevation_zones)


@dataclass
class ComparisonConfig:
    """Configuration for dataset comparisons."""
    output_suffix: str = '_comparison'
    correlation_threshold: float = 0.7
    significance_level: float = 0.05
    difference_threshold: float = 0.1
    sync_tolerance_days: int = 1


@dataclass
class VisualizationConfig:
    """Configuration for visualizations."""
    style: str = 'seaborn-v0_8'
    palette: str = 'husl'
    font_family: List[str] = field(default_factory=lambda: ['DejaVu Sans', 'sans-serif'])
    font_sans_serif: List[str] = field(default_factory=lambda: ['DejaVu Sans', 'Arial', 'Liberation Sans', 'Helvetica'])
    
    def apply(self):
        """Apply visualization settings."""
        plt.style.use(self.style)
        sns.set_palette(self.palette)
        plt.rcParams['font.family'] = self.font_family
        plt.rcParams['font.sans-serif'] = self.font_sans_serif


class ConfigManager:
    """Central configuration manager."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self._setup_visualization()
        self._initialize_configs()
    
    def _setup_visualization(self):
        """Setup visualization configuration."""
        self.visualization = VisualizationConfig()
        self.visualization.apply()
    
    def _initialize_configs(self):
        """Initialize all configuration objects."""
        # Dataset configurations
        self.mcd43a3 = DatasetConfig(
            name='MCD43A3',
            description='Albédo général (MODIS Combined)',
            csv_path="data/csv/MCD43A3_albedo_daily_stats_2010_2024.csv",
            qa_csv_path="data/csv/MCD43A3_quality_distribution_daily_2010_2024.csv",
            quality_levels=['quality_0_best', 'quality_1_good', 'quality_2_moderate', 'quality_3_poor'],
            temporal_resolution='16-day composite',
            scaling_info='Scale factor: 0.001'
        )
        
        self.mod10a1 = DatasetConfig(
            name='MOD10A1',
            description='Albédo de neige (Terra Snow Cover)',
            csv_path="data/csv/MOD10A1_snow_daily_stats_2010_2024.csv",
            qa_csv_path="data/csv/MOD10A1_quality_distribution_daily_2010_2024.csv",
            quality_levels=['quality_0_best', 'quality_1_good', 'quality_2_ok', 'quality_other_night_ocean'],
            temporal_resolution='Daily',
            scaling_info='Percentage (1-100) to decimal (÷100)'
        )
        
        # Elevation analysis configuration
        self.elevation = ElevationConfig(
            csv_path="data/csv/MOD10A1_daily_snow_albedo_fraction_elevation_williamson_2010_2024.csv",
            name='MOD10A1_Elevation',
            description='Albédo par fraction × élévation (Williamson & Menounos 2021)'
        )
        
        # Comparison configuration
        self.comparison = ComparisonConfig()
        
        # Application settings
        self.default_dataset = "MCD43A3"
        self.data_mode = "database"  # or "csv"
        self.output_dir = "results"
        self.analysis_variable = "mean"
        
        # Fraction classes
        self.fraction_classes = ['border', 'mixed_low', 'mixed_high', 'mostly_ice', 'pure_ice']
        self.class_labels = {
            'border': '0-25% (Bordure)',
            'mixed_low': '25-50% (Mixte bas)',
            'mixed_high': '50-75% (Mixte haut)',
            'mostly_ice': '75-95% (Principalement glace)',
            'pure_ice': '95-100% (Glace pure)'
        }
    
    def get_dataset_config(self, dataset_name: str) -> Optional[DatasetConfig]:
        """Get configuration for a specific dataset."""
        configs = {
            'MCD43A3': self.mcd43a3,
            'MOD10A1': self.mod10a1
        }
        return configs.get(dataset_name)
    
    def get_all_datasets(self) -> Dict[str, DatasetConfig]:
        """Get all dataset configurations."""
        return {
            'MCD43A3': self.mcd43a3,
            'MOD10A1': self.mod10a1
        }
    
    def validate_paths(self) -> Dict[str, bool]:
        """Validate that all configured paths exist."""
        results = {}
        
        for name, config in self.get_all_datasets().items():
            csv_exists = Path(config.csv_path).exists()
            qa_exists = Path(config.qa_csv_path).exists()
            results[f"{name}_csv"] = csv_exists
            results[f"{name}_qa"] = qa_exists
        
        # Check elevation config
        elevation_exists = Path(self.elevation.csv_path).exists()
        results["elevation_csv"] = elevation_exists
        
        return results
    
    def print_summary(self):
        """Print configuration summary."""
        print("\n📋 CONFIGURATION SUMMARY")
        print("=" * 50)
        print(f"Default dataset: {self.default_dataset}")
        print(f"Data mode: {self.data_mode}")
        print(f"Output directory: {self.output_dir}")
        print(f"Analysis variable: {self.analysis_variable}")
        
        print(f"\n📊 Available datasets:")
        for name, config in self.get_all_datasets().items():
            print(f"  {name}: {config.description}")
        
        print(f"\n🔍 Fraction classes: {len(self.fraction_classes)}")
        for fraction in self.fraction_classes:
            print(f"  {fraction}: {self.class_labels[fraction]}")


# Global configuration instance
config = ConfigManager()

# Export commonly used configurations for backward compatibility
DEFAULT_DATASET = config.default_dataset
DATA_MODE = config.data_mode
OUTPUT_DIR = config.output_dir
ANALYSIS_VARIABLE = config.analysis_variable
FRACTION_CLASSES = config.fraction_classes
CLASS_LABELS = config.class_labels

# Dataset configurations for backward compatibility
MCD43A3_CONFIG = {
    'csv_path': config.mcd43a3.csv_path,
    'qa_csv_path': config.mcd43a3.qa_csv_path,
    'name': config.mcd43a3.name,
    'description': config.mcd43a3.description,
    'quality_levels': config.mcd43a3.quality_levels,
    'temporal_resolution': config.mcd43a3.temporal_resolution,
    'scaling_info': config.mcd43a3.scaling_info
}

MOD10A1_CONFIG = {
    'csv_path': config.mod10a1.csv_path,
    'qa_csv_path': config.mod10a1.qa_csv_path,
    'name': config.mod10a1.name,
    'description': config.mod10a1.description,
    'quality_levels': config.mod10a1.quality_levels,
    'temporal_resolution': config.mod10a1.temporal_resolution,
    'scaling_info': config.mod10a1.scaling_info
}

ELEVATION_CONFIG = {
    'csv_path': config.elevation.csv_path,
    'name': config.elevation.name,
    'description': config.elevation.description,
    'elevation_zones': config.elevation.elevation_zones,
    'fraction_classes': config.elevation.fraction_classes,
    'combinations': config.elevation.combinations,
    'methodology': config.elevation.methodology,
    'output_dir': config.elevation.output_dir,
    'reference_paper': config.elevation.reference_paper
}

COMPARISON_CONFIG = {
    'output_suffix': config.comparison.output_suffix,
    'correlation_threshold': config.comparison.correlation_threshold,
    'significance_level': config.comparison.significance_level,
    'difference_threshold': config.comparison.difference_threshold,
    'sync_tolerance_days': config.comparison.sync_tolerance_days
}

# Legacy compatibility
CSV_PATH = config.mcd43a3.csv_path
QA_CSV_PATH = config.mcd43a3.qa_csv_path

def print_config_summary():
    """Print configuration summary (legacy function)."""
    config.print_summary()