@echo off
REM Saskatchewan Glacier Albedo Analysis Dashboard Launcher (Windows)
REM ================================================================

echo.
echo 🏔️ Saskatchewan Glacier Albedo Analysis Dashboard
echo ==================================================
echo 🚀 Starting dashboard server...
echo 📊 Loading MODIS data (2010-2024)...
echo 🌐 Dashboard will open in your browser
echo ==================================================
echo.

cd /d "%~dp0.."
python dashboard/run_dashboard.py

pause