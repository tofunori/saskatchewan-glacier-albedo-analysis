@echo off
REM Windows Batch Script to Run MODIS Downloader in WSL
REM Saskatchewan Glacier Albedo Analysis Project
REM 
REM This script launches the MODIS downloader Python script inside WSL from Windows
REM Make sure WSL is installed and Ubuntu distribution is available

echo =================================================================
echo Saskatchewan Glacier MODIS Data Downloader (Windows WSL Launcher)
echo =================================================================
echo.

REM Check if WSL is available
wsl --list --quiet >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: WSL is not installed or not available.
    echo Please install WSL and Ubuntu from Microsoft Store.
    echo See: https://docs.microsoft.com/en-us/windows/wsl/install
    pause
    exit /b 1
)

echo Checking WSL status...
wsl --status >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: WSL status check failed. Continuing anyway...
)

echo WSL is available. Launching MODIS downloader...
echo.

REM Change to the project directory in WSL and run the Python script
REM The path is converted from Windows path to WSL path automatically
echo Changing to project directory: /home/tofunori/saskatchewan-glacier-albedo-analysis/modis_data
echo Running Python script: modis_downloader.py
echo.

wsl -d Ubuntu -- bash -c "cd /home/tofunori/saskatchewan-glacier-albedo-analysis/modis_data && python3 modis_downloader.py"

REM Check exit code
if %errorlevel% equ 0 (
    echo.
    echo =================================================================
    echo MODIS downloader completed successfully!
    echo Check the modis_data directory for downloaded files.
    echo =================================================================
) else (
    echo.
    echo =================================================================
    echo ERROR: MODIS downloader failed with exit code %errorlevel%
    echo Please check the error messages above.
    echo =================================================================
)

echo.
echo Press any key to exit...
pause >nul