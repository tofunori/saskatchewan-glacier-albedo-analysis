@echo off
echo ================================================================
echo    Saskatchewan Glacier Albedo Analysis Dashboard
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Starting dashboard...
echo Dashboard will be available at: http://localhost:8000
echo Press Ctrl+C to stop the dashboard
echo.

REM Change to dashboard directory
cd /d "%~dp0"

REM Run the dashboard
python run_dashboard.py

echo.
echo Dashboard stopped.
pause