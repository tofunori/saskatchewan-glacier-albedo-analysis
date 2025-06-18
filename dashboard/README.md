# Saskatchewan Glacier Albedo Dashboard

Interactive web dashboard for exploring MODIS albedo data from Saskatchewan Glacier (2010-2024).

## 🆕 Academic Dashboard Available

We now offer **two dashboard versions**:

### 🔬 **Academic Dashboard** (RECOMMENDED)
**New enhanced version with comprehensive statistical analysis**

- **Advanced Statistical Analysis**: Mann-Kendall tests, Sen's slope, bootstrap confidence intervals
- **Publication-Quality Visualizations**: Academic-grade plots with statistical annotations
- **Comprehensive Results Export**: CSV, Excel, JSON, PDF reports
- **Professional Analytics**: Autocorrelation analysis, seasonal trends, correlation matrices
- **Academic Standards**: Publication-ready outputs and methodology documentation

### 📊 **Basic Dashboard** 
**Original simple visualization dashboard**

- **Multi-Dataset Support**: Switch between MCD43A3 (16-day composite) and MOD10A1 (daily) datasets
- **Multiple Visualization Types**: 
  - **Line Plots**: Traditional trend visualization
  - **Scatter Plots**: Individual daily observations as points
  - **Stacked Bar Charts**: Comparative analysis of all fraction classes
- **Interactive Controls**: Dataset selection, plot type, fraction class, and time aggregation
- **Enhanced Analytics**: Summary statistics adapted to visualization type
- **Real-time Updates**: All charts update instantly when changing selections

## Quick Start

### 🔬 Academic Dashboard (RECOMMENDED)

**Windows:**
```powershell
cd dashboard
python run_academic_dashboard.py
```

**Linux/Mac:**
```bash
cd dashboard
python3 run_academic_dashboard.py
```

**Direct Python:**
```bash
cd dashboard
python -m shiny run app_enhanced.py --host 0.0.0.0 --port 8000
```

### 📊 Basic Dashboard

**Windows Users**

**Option 1: Double-click the batch file**
```
run_dashboard.bat
```

**Option 2: PowerShell/Command Prompt**
```powershell
cd dashboard
python run_dashboard.py
```

**Option 3: Direct Python**
```powershell
cd dashboard
python -m shiny run app.py
```

**Linux/Mac Users**

```bash
cd dashboard
python3 run_dashboard.py
```

## Requirements

### Academic Dashboard Requirements
The academic dashboard requires additional packages for statistical analysis:
- `shiny >= 1.0.0`
- `pandas >= 1.5.0`
- `plotly >= 5.0.0`
- `numpy >= 1.21.0`
- `scipy >= 1.9.0` *(for statistical tests)*
- `scikit-learn >= 1.1.0` *(for bootstrap analysis)*

Install all dependencies:
```bash
pip install shiny pandas plotly numpy scipy scikit-learn
```

### Basic Dashboard Requirements
- `shiny >= 1.0.0`
- `pandas >= 1.5.0`
- `plotly >= 5.0.0`
- `numpy >= 1.21.0`

Install basic dependencies:
```bash
pip install shiny pandas plotly numpy
```

## Data

The dashboard supports two MODIS datasets:

### MCD43A3 - General Albedo
- **File**: `../data/csv/daily_albedo_mann_kendall_ready_2010_2024.csv`
- **Resolution**: 16-day composite
- **Description**: MODIS Combined albedo data
- **Best for**: Long-term trend analysis

### MOD10A1 - Snow Albedo  
- **File**: `../data/csv/daily_snow_albedo_mann_kendall_mod10a1_2010_2024.csv`
- **Resolution**: Daily observations
- **Description**: Terra Snow Cover daily albedo
- **Best for**: Daily evolution analysis, detailed temporal patterns

## Fraction Classes

- **Pure Ice** (90-100%): Nearly pure ice coverage
- **Mostly Ice** (75-90%): Predominantly ice with some mixed surfaces
- **Mixed High** (50-75%): Mixed ice and other surfaces, ice dominant
- **Mixed Low** (25-50%): Mixed surfaces with moderate ice coverage
- **Border** (0-25%): Edge areas with minimal ice coverage

## Troubleshooting

### Dashboard won't start
1. **Check Python installation**: Run `python --version`
2. **Install dependencies**: `pip install shiny pandas plotly`
3. **Verify data files**: Ensure `../data/csv/` contains the required CSV files

### Data loading errors
- The dashboard includes fallback error handling
- Check that CSV files exist and are properly formatted
- Look for error messages in the terminal/console

### Port already in use
- Change the port in `run_dashboard.py`: modify `--port 8000` to another port
- Or kill the existing process using that port

### Windows PowerShell execution policy
If you get execution policy errors:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Development

The dashboard is built with:
- **Framework**: Shiny for Python 1.4.0
- **Visualization**: Plotly 6.1.2
- **Data Processing**: Pandas 2.1.4
- **Architecture**: Reactive programming with server-side state

## 🔬 Academic Dashboard Features

### Statistical Analysis Tabs

1. **📊 Overview**: Dataset information and basic summary statistics
2. **📈 Trend Analysis**: 
   - Mann-Kendall trend tests with significance testing
   - Sen's slope estimation with confidence intervals
   - Autocorrelation analysis
   - Publication-quality trend visualizations
3. **🔄 Bootstrap Analysis**:
   - Bootstrap confidence intervals (configurable iterations: 100-2000)
   - Statistical power analysis
   - Bootstrap distribution visualizations
4. **📅 Seasonal Patterns**:
   - Monthly trend analysis
   - Seasonal significance testing
   - Interactive seasonal pattern plots
5. **🔗 Correlation Analysis**:
   - Inter-fraction correlation matrices
   - Statistical significance testing
   - Correlation strength assessment
6. **📋 Statistical Tables**:
   - Comprehensive results tables
   - Export functionality (CSV, Excel, JSON)
   - Summary statistics

### Advanced Features

- **Publication-Quality Plots**: All visualizations meet academic publishing standards
- **Statistical Rigor**: Same level of analysis as main.py command-line interface
- **Export Capabilities**: 
  - Statistical results in multiple formats
  - High-resolution figures (PNG, SVG, PDF)
  - Comprehensive methodology reports
  - Citation-ready documentation
- **Parameter Control**: 
  - Adjustable significance levels (α = 0.001, 0.01, 0.05)
  - Configurable bootstrap iterations
  - Variable selection (mean/median)
- **Academic Standards**: Following established statistical practices for albedo trend analysis

### Validation

Run the validation script to ensure accuracy:
```bash
cd dashboard
python validate_dashboard_analysis.py
```

### File Structure
```
dashboard/
├── app.py                        # Basic dashboard
├── app_enhanced.py               # Academic dashboard ⭐
├── statistical_analysis.py       # Statistical analysis module
├── academic_plots.py             # Publication-quality plots
├── export_manager.py             # Results export functionality
├── run_dashboard.py              # Basic dashboard runner
├── run_academic_dashboard.py     # Academic dashboard runner ⭐
├── validate_dashboard_analysis.py # Validation script
├── run_dashboard.bat             # Windows batch file
├── test_dashboard.py             # Test suite
└── README.md                     # This file
```

### Extending the Dashboard

To add new features:
1. Modify `app.py` for new UI components or server logic
2. Update `run_dashboard.py` for new dependencies
3. Test with `test_dashboard.py`

## Integration

This dashboard integrates with the main Saskatchewan Glacier analysis project:
- Uses existing data handlers and configuration
- Follows established naming conventions
- Reuses visualization styling and color schemes
- Compatible with the existing analysis workflow

## Support

For issues with the dashboard:
1. Check the console output for error messages
2. Verify all dependencies are installed
3. Ensure data files are present and accessible
4. Review the troubleshooting section above

The dashboard is designed to work alongside the existing command-line analysis tools and provides a user-friendly interface for data exploration.