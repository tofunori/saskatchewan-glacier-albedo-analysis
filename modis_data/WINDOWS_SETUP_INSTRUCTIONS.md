# Running MODIS Downloader from Windows via WSL

This guide explains how to run the Saskatchewan Glacier MODIS downloader on Windows using Windows Subsystem for Linux (WSL).

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Running the Downloader](#running-the-downloader)
4. [Accessing Downloaded Data](#accessing-downloaded-data)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Usage](#advanced-usage)

## Prerequisites

### 1. Install WSL
If you don't have WSL installed:

1. Open PowerShell as Administrator
2. Run: `wsl --install`
3. Restart your computer
4. Install Ubuntu from Microsoft Store (recommended)

### 2. Verify WSL Installation
```cmd
wsl --list --verbose
```
You should see Ubuntu listed and running.

### 3. Access Project Directory
The project should be accessible at:
- **Windows Path:** `\\wsl.localhost\Ubuntu\home\tofunori\saskatchewan-glacier-albedo-analysis`
- **WSL Path:** `/home/tofunori/saskatchewan-glacier-albedo-analysis`

## Initial Setup

### Option 1: Automated Setup (Recommended)

1. **Install Dependencies:** Open the project folder in Windows Explorer and navigate to the `modis_data` directory, then run:
   ```cmd
   wsl -d Ubuntu -- bash -c "cd /home/tofunori/saskatchewan-glacier-albedo-analysis/modis_data && ./install_wsl_dependencies.sh"
   ```

### Option 2: Manual Setup

1. **Open WSL Terminal:**
   ```cmd
   wsl -d Ubuntu
   ```

2. **Navigate to Project:**
   ```bash
   cd /home/tofunori/saskatchewan-glacier-albedo-analysis/modis_data
   ```

3. **Run Installation Script:**
   ```bash
   ./install_wsl_dependencies.sh
   ```

## Running the Downloader

You have several options to run the MODIS downloader from Windows:

### Option 1: Windows Batch File (Easiest)

1. Navigate to: `\\wsl.localhost\Ubuntu\home\tofunori\saskatchewan-glacier-albedo-analysis\modis_data`
2. Double-click: `run_modis_downloader.bat`

Or from Command Prompt:
```cmd
cd "\\wsl.localhost\Ubuntu\home\tofunori\saskatchewan-glacier-albedo-analysis\modis_data"
run_modis_downloader.bat
```

### Option 2: PowerShell Script (Advanced)

From PowerShell:
```powershell
cd "\\wsl.localhost\Ubuntu\home\tofunori\saskatchewan-glacier-albedo-analysis\modis_data"
.\Run-ModisDownloader.ps1
```

With dependency installation:
```powershell
.\Run-ModisDownloader.ps1 -InstallDependencies
```

### Option 3: Direct WSL Command

From Command Prompt or PowerShell:
```cmd
wsl -d Ubuntu -- bash -c "cd /home/tofunori/saskatchewan-glacier-albedo-analysis/modis_data && source activate_modis_env.sh && python3 modis_downloader.py"
```

### Option 4: WSL Terminal

1. Open WSL:
   ```cmd
   wsl -d Ubuntu
   ```

2. Navigate and activate:
   ```bash
   cd /home/tofunori/saskatchewan-glacier-albedo-analysis/modis_data
   source activate_modis_env.sh
   ```

3. Run downloader:
   ```bash
   python3 modis_downloader.py
   ```

## Accessing Downloaded Data

Downloaded MODIS data will be stored in:

- **WSL Path:** `/home/tofunori/saskatchewan-glacier-albedo-analysis/modis_data/modis_data/`
- **Windows Path:** `\\wsl.localhost\Ubuntu\home\tofunori\saskatchewan-glacier-albedo-analysis\modis_data\modis_data\`

### Data Structure
```
modis_data/
├── MOD10A1_snow_cover/     # Snow cover data
├── MCD43A3_albedo/         # Albedo data
└── [other downloaded files]
```

### Opening in Windows Explorer
1. Press `Win + R`
2. Type: `\\wsl.localhost\Ubuntu\home\tofunori\saskatchewan-glacier-albedo-analysis\modis_data\modis_data`
3. Press Enter

## Troubleshooting

### Common Issues

#### 1. WSL Not Found
```
ERROR: WSL is not installed or not available
```
**Solution:** Install WSL following the prerequisites section.

#### 2. Ubuntu Distribution Missing
```
✗ Ubuntu distribution not found
```
**Solution:** Install Ubuntu from Microsoft Store or run `wsl --install -d Ubuntu`

#### 3. Project Directory Not Found
```
✗ Project directory not found
```
**Solution:** Ensure the project is cloned/copied to the correct WSL location:
```bash
wsl -d Ubuntu
cd /home/tofunori
git clone [repository-url] saskatchewan-glacier-albedo-analysis
```

#### 4. Permission Denied
```
Permission denied: './install_wsl_dependencies.sh'
```
**Solution:** Make scripts executable:
```bash
wsl -d Ubuntu -- bash -c "cd /home/tofunori/saskatchewan-glacier-albedo-analysis/modis_data && chmod +x *.sh"
```

#### 5. Python/Package Errors
```
ModuleNotFoundError: No module named 'modis_tools'
```
**Solution:** Reinstall dependencies:
```bash
wsl -d Ubuntu -- bash -c "cd /home/tofunori/saskatchewan-glacier-albedo-analysis/modis_data && ./install_wsl_dependencies.sh"
```

#### 6. NASA Earthdata Authentication Issues
```
Authentication failed
```
**Solution:** 
1. Verify your NASA Earthdata credentials
2. Update username/password in `modis_downloader.py`
3. Or set up `.netrc` file:
   ```bash
   echo "machine urs.earthdata.nasa.gov login YOUR_USERNAME password YOUR_PASSWORD" >> ~/.netrc
   chmod 600 ~/.netrc
   ```

#### 7. Network/Download Issues
```
Failed to download granules
```
**Solution:**
1. Check internet connection
2. Verify NASA Earthdata credentials
3. Try reducing download limit in the script
4. Check if NASA servers are accessible

### Getting Help

#### Check Environment
Run the environment checker:
```bash
wsl -d Ubuntu -- bash -c "cd /home/tofunori/saskatchewan-glacier-albedo-analysis/modis_data && source activate_modis_env.sh && python3 -c 'import sys; print(f\"Python: {sys.version}\"); import modis_tools; print(f\"modis-tools: {modis_tools.__version__}\")'"
```

#### View Logs
The downloader provides detailed output. Look for:
- ✓ Success indicators (green checkmarks)
- ⚠ Warnings (yellow)
- ✗ Errors (red X marks)

#### WSL Status
Check WSL status:
```cmd
wsl --status
wsl --list --verbose
```

## Advanced Usage

### Customizing Download Parameters

Edit `modis_downloader.py` to modify:
- Date ranges
- Geographic bounds
- Download limits
- Product types

### Running with Custom Parameters

The PowerShell script supports parameters:
```powershell
.\Run-ModisDownloader.ps1 -StartDate "2024-07-01" -EndDate "2024-07-31" -LimitPerProduct 10
```

### Using Different WSL Distributions

If using a different Linux distribution:
```cmd
wsl -d YourDistribution -- bash -c "cd /path/to/project && ./script.sh"
```

### Performance Optimization

For better performance:
1. Use WSL2 (not WSL1)
2. Store data in WSL filesystem (not Windows filesystem)
3. Use SSD storage
4. Ensure adequate RAM (8GB+ recommended)

### Batch Processing

Create a batch file for multiple downloads:
```batch
@echo off
wsl -d Ubuntu -- bash -c "cd /home/tofunori/saskatchewan-glacier-albedo-analysis/modis_data && source activate_modis_env.sh && python3 batch_download.py"
```

## File Reference

| File | Purpose |
|------|---------|
| `run_modis_downloader.bat` | Windows batch launcher |
| `Run-ModisDownloader.ps1` | PowerShell launcher with advanced options |
| `install_wsl_dependencies.sh` | Automated dependency installer |
| `activate_modis_env.sh` | Environment activation script |
| `modis_downloader.py` | Main MODIS downloader script |
| `requirements.txt` | Python dependencies |
| `USAGE_WSL.md` | Quick usage reference |

## Support

For issues specific to:
- **WSL:** Check Microsoft WSL documentation
- **MODIS Tools:** Check the modis-tools Python package documentation
- **NASA Earthdata:** Verify account and authentication
- **This Project:** Check error messages and logs for specific issues

Remember to keep your NASA Earthdata credentials secure and never commit them to version control!