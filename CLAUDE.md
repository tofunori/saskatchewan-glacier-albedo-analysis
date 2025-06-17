# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Saskatchewan Glacier Albedo Analysis - A comprehensive Python package for analyzing albedo trends using MODIS satellite data (2010-2024). The project analyzes two datasets:
- **MCD43A3**: General albedo (MODIS Combined, 16-day composite)
- **MOD10A1**: Snow albedo (Terra Snow Cover, daily)

## Key Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Running the Analysis

#### Command Line Interface (CLI)
```bash
# Main interactive interface (from project root)
python scripts/main.py

# Or as module
python -m saskatchewan_albedo.scripts.main
```

#### Streamlit Web Interface
```bash
# Launch interactive web application
streamlit run streamlit_app.py

# Access at http://localhost:8501
```

### Development Commands
```bash
# No formal test suite exists yet
# No linting/formatting commands configured
```

## Architecture Overview

### Package Structure
The code is organized directly at the project root with these key components:

1. **Entry Points**: 
   - `scripts/main.py` - Command-line interactive menu system
   - `streamlit_app.py` - Web interface entry point
2. **Configuration**: `config.py` - All settings, paths, and parameters
3. **Data Pipeline**:
   - `data/handler.py` - AlbedoDataHandler for CSV loading
   - `data/dataset_manager.py` - Multi-dataset management
4. **Analysis Modules**:
   - `analysis/trends.py` - Statistical trend analysis
   - `analysis/seasonal.py` - Seasonal patterns
   - `analysis/pixel_analysis.py` - Quality/coverage analysis
   - `analysis/comparison.py` - Cross-dataset comparison
5. **Visualization**:
   - `visualization/charts.py` - Main chart generation
   - `visualization/daily_plots.py` - Daily melt season plots
   - `visualization/comparison_plots.py` - Comparison visualizations
6. **Web Interface**:
   - `pages/` - Streamlit multi-page application
   - `streamlit_utils/` - Web-specific utilities and components

### Data Flow
1. Google Earth Engine scripts export MODIS data to CSV
2. AlbedoDataHandler loads and prepares data
3. Analysis modules process data (trends, seasonal, quality)
4. Visualization modules generate plots
5. Results saved to `results/` directory

### Key Design Patterns
- **Configuration-driven**: All parameters in `config.py`
- **Modular analysis**: Each analysis type is independent
- **Dataset abstraction**: Unified interface for multiple MODIS products
- **Interactive workflow**: Menu-driven user interface

## Important Instructions

### Code Organization
- Always keep `main.py` small and short
- Break new code into smaller sections
- Organize new modules in appropriate folders at the project root
- Follow existing patterns for consistency

### File Management
- NEVER create files unless absolutely necessary
- ALWAYS prefer editing existing files
- NEVER proactively create documentation files (*.md) or README files

### Working with Data
- Input CSV files are in `data/csv/`
- Results go to `results/` with subdirectories by dataset type
- Quality thresholds and fraction classes are defined in `config.py`

### Adding New Features
1. Check if similar functionality exists
2. Add configuration to `config.py` if needed
3. Create module in appropriate directory
4. Integrate with menu system in `main.py`
5. Use existing visualization patterns

### Common Workflows

#### Adding a New Analysis Type
1. Create module in `analysis/`
2. Add configuration section to `config.py`
3. Create visualization module if needed
4. Add menu option to `scripts/main.py`
5. Update `scripts/analysis_functions.py` to integrate

#### Adding a New Dataset
1. Add dataset configuration to `config.py`
2. Ensure CSV follows existing naming patterns
3. Update DatasetManager if needed
4. Test with existing analysis pipelines

#### Modifying Visualizations
1. Check existing patterns in `visualization/` modules
2. Use configuration from `config.py` for styles
3. Follow naming conventions for output files
4. Ensure proper directory structure in results

### Quality Checks
- Verify relative paths work from project root
- Check that all dependencies are in requirements.txt
- Test menu navigation after changes
- Ensure results are saved to correct directories

### Note on Testing
No formal test suite exists. Manual testing through the interactive menu is the current validation method.