# Codebase Structure

## Root Level
- **`scripts/main.py`**: Primary entry point with interactive menu system
- **`config.py`**: Centralized configuration for all datasets and analysis parameters
- **`setup.py`**: Package configuration and dependencies
- **`README.md`**: Project documentation
- **`CLAUDE.md`**: Instructions for Claude Code assistant

## Core Modules

### 1. Scripts (`scripts/`)
- **`main.py`**: Interactive menu system and main entry point
- **`analysis_functions.py`**: High-level analysis orchestration functions
- **`main_backup.py`**: Legacy backup version

### 2. Data Management (`data/`)
- **`handler.py`**: `AlbedoDataHandler` class for CSV data loading and processing
- **`dataset_manager.py`**: Multi-dataset management and coordination
- **`loader.py`**: Data loading utilities
- **`modis/`**: MODIS-specific data processing

### 3. Analysis Modules (`analysis/`)
- **`trends.py`**: Statistical trend analysis (Mann-Kendall tests)
- **`seasonal.py`**: Seasonal pattern analysis
- **`pixel_analysis.py`**: Quality assessment and pixel coverage analysis
- **`comparison.py`**: Cross-dataset comparison tools
- **`elevation_analysis.py`**: Elevation-based analysis
- **`spatial.py`**: Spatial analysis functions
- **`advanced.py`**: Advanced analytical methods

### 4. Visualization (`visualization/`)
- **`charts.py`**: Main chart generation
- **`daily_plots.py`**: Daily time series visualizations
- **`comparison_plots.py`**: Multi-dataset comparison plots
- **`elevation_plots.py`**: Elevation-specific visualizations
- **`pixel_plots.py`**: Quality and coverage visualizations
- **`monthly.py`**: Monthly aggregation plots
- **`pixel_plots/`**: Specialized pixel analysis plots

### 5. Utility Modules (`utils/`)
- Various utility functions and helpers

## Data Directories
- **`data/`**: Input CSV files and raw data
- **`results/`**: Output directory with dataset-specific subdirectories
  - `MCD43A3_albedo/`: General albedo analysis results
  - `MOD10A1_snow_cover/`: Snow albedo analysis results
  - `combined_analysis/`: Cross-dataset comparisons

## Configuration Structure
- **`docs/`**: Documentation files
- **`legacy/`**: Legacy code and deprecated scripts
- **`.serena/`**: Serena MCP configuration
- **`.claude/`**: Claude Code configuration

## Key Design Principles
1. **Configuration-Driven**: All parameters in `config.py`
2. **Modular Architecture**: Each analysis type is independent
3. **Dataset Abstraction**: Unified interface for multiple MODIS products
4. **Interactive Workflow**: Menu-driven user experience
5. **Result Organization**: Structured output with dataset-specific directories