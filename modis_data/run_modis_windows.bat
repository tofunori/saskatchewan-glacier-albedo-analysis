@echo off
echo ================================================================
echo MODIS Data Downloader - Windows Launcher
echo ================================================================
echo.

REM Check if conda environment is activated
python -c "import sys; print('Python:', sys.executable)" 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Python not found. Please activate your conda environment first:
    echo    conda activate geo-env
    echo.
    pause
    exit /b 1
)

REM Check if required packages are available
echo 🔍 Checking dependencies...
python -c "import geopandas, modis_tools; print('✅ Dependencies OK')" 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Missing dependencies. Installing modis-tools...
    conda install -c conda-forge modis-tools -y
    if %ERRORLEVEL% neq 0 (
        echo ❌ Failed to install modis-tools
        echo Please run manually: conda install -c conda-forge modis-tools
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Launching MODIS downloader...
echo.

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Run the Python script
python "%SCRIPT_DIR%modis_downloader_windows.py"

echo.
echo ================================================================
echo Download completed! Check the output above for results.
echo Files are accessible from Windows File Explorer at:
echo \\wsl.localhost\Ubuntu\home\tofunori\saskatchewan-glacier-albedo-analysis\modis_data
echo ================================================================
pause