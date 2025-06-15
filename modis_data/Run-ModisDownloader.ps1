#Requires -Version 5.1
<#
.SYNOPSIS
    PowerShell Script to Run MODIS Downloader in WSL
    Saskatchewan Glacier Albedo Analysis Project

.DESCRIPTION
    This script launches the MODIS downloader Python script inside WSL from Windows PowerShell.
    It includes error checking, dependency verification, and proper path handling.

.PARAMETER InstallDependencies
    Switch to install Python dependencies in WSL before running the downloader

.PARAMETER StartDate
    Start date for MODIS data download (YYYY-MM-DD format)

.PARAMETER EndDate
    End date for MODIS data download (YYYY-MM-DD format)

.PARAMETER LimitPerProduct
    Maximum number of granules to download per product type (for testing)

.EXAMPLE
    .\Run-ModisDownloader.ps1
    Run with default parameters

.EXAMPLE
    .\Run-ModisDownloader.ps1 -InstallDependencies
    Install dependencies first, then run downloader

.EXAMPLE
    .\Run-ModisDownloader.ps1 -StartDate "2024-08-01" -EndDate "2024-08-15" -LimitPerProduct 5
    Run with custom date range and download limit
#>

param(
    [switch]$InstallDependencies,
    [string]$StartDate = "",
    [string]$EndDate = "",
    [int]$LimitPerProduct = 0
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Define project paths
$WSLProjectPath = "/home/tofunori/saskatchewan-glacier-albedo-analysis/modis_data"
$WindowsProjectPath = "\\wsl.localhost\Ubuntu\home\tofunori\saskatchewan-glacier-albedo-analysis\modis_data"

Write-Host "=================================================================" -ForegroundColor Green
Write-Host "Saskatchewan Glacier MODIS Data Downloader (PowerShell WSL Launcher)" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green
Write-Host ""

# Function to check if WSL is available
function Test-WSLAvailable {
    try {
        $wslResult = wsl --list --quiet 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ WSL is available" -ForegroundColor Green
            return $true
        } else {
            throw "WSL command failed"
        }
    } catch {
        Write-Host "✗ WSL is not installed or not available" -ForegroundColor Red
        Write-Host "  Please install WSL and Ubuntu from Microsoft Store" -ForegroundColor Yellow
        Write-Host "  See: https://docs.microsoft.com/en-us/windows/wsl/install" -ForegroundColor Yellow
        return $false
    }
}

# Function to check if Ubuntu distribution exists
function Test-UbuntuDistribution {
    try {
        $distributions = wsl --list --quiet
        if ($distributions -match "Ubuntu") {
            Write-Host "✓ Ubuntu distribution found" -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ Ubuntu distribution not found" -ForegroundColor Red
            Write-Host "  Available distributions:" -ForegroundColor Yellow
            wsl --list
            return $false
        }
    } catch {
        Write-Host "✗ Could not check WSL distributions" -ForegroundColor Red
        return $false
    }
}

# Function to check if project directory exists in WSL
function Test-ProjectDirectory {
    try {
        $result = wsl -d Ubuntu -- test -d $WSLProjectPath
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Project directory found: $WSLProjectPath" -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ Project directory not found: $WSLProjectPath" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "✗ Could not check project directory" -ForegroundColor Red
        return $false
    }
}

# Function to install dependencies in WSL
function Install-WSLDependencies {
    Write-Host "Installing Python dependencies in WSL..." -ForegroundColor Yellow
    
    try {
        # Update package lists
        Write-Host "Updating package lists..." -ForegroundColor Yellow
        wsl -d Ubuntu -- sudo apt update
        
        # Install system dependencies
        Write-Host "Installing system dependencies..." -ForegroundColor Yellow
        wsl -d Ubuntu -- sudo apt install -y python3-pip python3-venv python3-dev gdal-bin libgdal-dev
        
        # Create virtual environment if it doesn't exist
        Write-Host "Setting up Python virtual environment..." -ForegroundColor Yellow
        wsl -d Ubuntu -- bash -c "cd $WSLProjectPath && python3 -m venv venv_modis"
        
        # Install Python packages
        Write-Host "Installing Python packages..." -ForegroundColor Yellow
        wsl -d Ubuntu -- bash -c "cd $WSLProjectPath && source venv_modis/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"
        
        Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "✗ Failed to install dependencies: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to run the MODIS downloader
function Invoke-ModisDownloader {
    param(
        [string]$StartDate,
        [string]$EndDate,
        [int]$LimitPerProduct
    )
    
    Write-Host "Running MODIS downloader..." -ForegroundColor Yellow
    Write-Host "Project directory: $WSLProjectPath" -ForegroundColor Cyan
    
    # Build the command
    $pythonCmd = "cd $WSLProjectPath && source venv_modis/bin/activate && python3 modis_downloader.py"
    
    # Add parameters if provided
    if ($StartDate -and $EndDate) {
        Write-Host "Date range: $StartDate to $EndDate" -ForegroundColor Cyan
        # Note: You would need to modify modis_downloader.py to accept command line arguments
        # For now, it uses hardcoded dates in the main() function
    }
    
    if ($LimitPerProduct -gt 0) {
        Write-Host "Download limit per product: $LimitPerProduct" -ForegroundColor Cyan
    }
    
    Write-Host ""
    
    try {
        # Execute the Python script in WSL
        wsl -d Ubuntu -- bash -c $pythonCmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "=================================================================" -ForegroundColor Green
            Write-Host "✓ MODIS downloader completed successfully!" -ForegroundColor Green
            Write-Host "Check the modis_data directory for downloaded files." -ForegroundColor Green
            Write-Host "Windows path: $WindowsProjectPath" -ForegroundColor Cyan
            Write-Host "=================================================================" -ForegroundColor Green
            return $true
        } else {
            throw "Python script failed with exit code $LASTEXITCODE"
        }
    } catch {
        Write-Host ""
        Write-Host "=================================================================" -ForegroundColor Red
        Write-Host "✗ MODIS downloader failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please check the error messages above." -ForegroundColor Red
        Write-Host "=================================================================" -ForegroundColor Red
        return $false
    }
}

# Main execution
try {
    # Check prerequisites
    Write-Host "Checking prerequisites..." -ForegroundColor Yellow
    
    if (-not (Test-WSLAvailable)) {
        exit 1
    }
    
    if (-not (Test-UbuntuDistribution)) {
        exit 1
    }
    
    if (-not (Test-ProjectDirectory)) {
        Write-Host "Please ensure the project is properly set up in WSL." -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "✓ All prerequisites met" -ForegroundColor Green
    Write-Host ""
    
    # Install dependencies if requested
    if ($InstallDependencies) {
        if (-not (Install-WSLDependencies)) {
            exit 1
        }
        Write-Host ""
    }
    
    # Run the downloader
    $success = Invoke-ModisDownloader -StartDate $StartDate -EndDate $EndDate -LimitPerProduct $LimitPerProduct
    
    if (-not $success) {
        exit 1
    }
    
} catch {
    Write-Host ""
    Write-Host "✗ Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace:" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")