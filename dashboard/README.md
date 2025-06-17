# Saskatchewan Glacier Albedo Dashboard

Interactive web dashboard for exploring MODIS albedo data from Saskatchewan Glacier (2010-2024).

## Features

- **Interactive Time Series**: Visualize albedo trends over time
- **Fraction Class Selection**: Compare different ice coverage fractions
- **Summary Statistics**: View descriptive statistics for selected data
- **Real-time Updates**: Charts update instantly when changing selections

## Quick Start

### Windows Users

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

### Linux/Mac Users

```bash
cd dashboard
python3 run_dashboard.py
```

## Requirements

The dashboard requires the following Python packages:
- `shiny >= 1.0.0`
- `pandas >= 1.5.0`
- `plotly >= 5.0.0`
- `numpy >= 1.21.0`

Install missing dependencies:
```bash
pip install shiny pandas plotly numpy
```

## Data

The dashboard uses the MCD43A3 dataset from the main project:
- **File**: `../data/csv/daily_albedo_mann_kendall_ready_2010_2024.csv`
- **Period**: 2010-2024
- **Source**: MODIS Combined albedo data (16-day composite)

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

### File Structure
```
dashboard/
├── app.py              # Main Shiny application
├── run_dashboard.py    # Cross-platform runner script
├── run_dashboard.bat   # Windows batch file
├── test_dashboard.py   # Test suite
└── README.md          # This file
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