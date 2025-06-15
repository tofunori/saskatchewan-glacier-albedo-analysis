#!/bin/bash
# WSL Dependency Installation Script for Saskatchewan Glacier MODIS Analysis
# This script installs all necessary dependencies in WSL for running the MODIS downloader

set -e  # Exit on any error

echo "================================================================="
echo "Saskatchewan Glacier MODIS Analysis - WSL Dependency Installer"
echo "================================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if running in WSL
check_wsl() {
    if [[ -f /proc/version ]] && grep -qi "microsoft\|wsl" /proc/version; then
        print_status "Running in WSL environment"
        if grep -qi "wsl2" /proc/version; then
            print_info "WSL2 detected"
        else
            print_info "WSL1 detected"
        fi
        return 0
    else
        print_warning "Not running in WSL, proceeding with Linux installation"
        return 1
    fi
}

# Check if script is run from the correct directory
check_directory() {
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    if [[ ! -f "$SCRIPT_DIR/modis_downloader.py" ]]; then
        print_error "modis_downloader.py not found in current directory"
        print_error "Please run this script from the modis_data directory"
        exit 1
    fi
    
    print_status "Script running from correct directory: $SCRIPT_DIR"
}

# Update package lists
update_packages() {
    print_info "Updating package lists..."
    sudo apt update
    print_status "Package lists updated"
}

# Install system dependencies
install_system_deps() {
    print_info "Installing system dependencies..."
    
    # Essential build tools and Python development headers
    sudo apt install -y \
        build-essential \
        python3-dev \
        python3-pip \
        python3-venv \
        python3-setuptools \
        python3-wheel
    
    # GDAL and spatial libraries
    sudo apt install -y \
        gdal-bin \
        libgdal-dev \
        libproj-dev \
        libgeos-dev \
        libspatialindex-dev
    
    # Additional useful tools
    sudo apt install -y \
        curl \
        wget \
        unzip \
        git
    
    print_status "System dependencies installed"
}

# Set up Python virtual environment
setup_venv() {
    print_info "Setting up Python virtual environment..."
    
    VENV_DIR="venv_modis"
    
    if [[ -d "$VENV_DIR" ]]; then
        print_warning "Virtual environment already exists, removing old one..."
        rm -rf "$VENV_DIR"
    fi
    
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    print_status "Virtual environment created: $VENV_DIR"
}

# Install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."
    
    # Activate virtual environment
    source venv_modis/bin/activate
    
    # Install GDAL Python bindings first (can be tricky)
    GDAL_VERSION=$(gdal-config --version)
    print_info "Installing GDAL Python bindings (version $GDAL_VERSION)..."
    pip install "GDAL==$GDAL_VERSION"
    
    # Install requirements from file
    if [[ -f "requirements.txt" ]]; then
        print_info "Installing packages from requirements.txt..."
        pip install -r requirements.txt
    else
        print_warning "requirements.txt not found, installing core packages..."
        pip install \
            modis-tools \
            numpy \
            pandas \
            matplotlib \
            seaborn \
            jupyter \
            netCDF4 \
            xarray \
            h5py \
            geopandas \
            rasterio \
            shapely \
            pyproj \
            folium \
            plotly
    fi
    
    print_status "Python dependencies installed"
}

# Verify installation
verify_installation() {
    print_info "Verifying installation..."
    
    source venv_modis/bin/activate
    
    # Test critical imports
    python3 -c "
import sys
import modis_tools
import geopandas
import rasterio
import numpy
import pandas
print('✓ All critical packages imported successfully')
print(f'Python version: {sys.version.split()[0]}')
print(f'modis-tools version: {modis_tools.__version__}')
print(f'geopandas version: {geopandas.__version__}')
print(f'numpy version: {numpy.__version__}')
print(f'pandas version: {pandas.__version__}')
"
    
    if [[ $? -eq 0 ]]; then
        print_status "Installation verification successful"
    else
        print_error "Installation verification failed"
        return 1
    fi
}

# Create activation script
create_activation_script() {
    print_info "Creating activation script..."
    
    cat > activate_modis_env.sh << 'EOF'
#!/bin/bash
# Activation script for MODIS analysis environment
# Source this file to activate the virtual environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv_modis"

if [[ -d "$VENV_DIR" ]]; then
    source "$VENV_DIR/bin/activate"
    echo "✓ MODIS analysis environment activated"
    echo "  Python: $(which python3)"
    echo "  Virtual environment: $VENV_DIR"
    echo ""
    echo "To run the MODIS downloader:"
    echo "  python3 modis_downloader.py"
    echo ""
    echo "To deactivate:"
    echo "  deactivate"
else
    echo "✗ Virtual environment not found: $VENV_DIR"
    echo "Please run install_wsl_dependencies.sh first"
fi
EOF
    
    chmod +x activate_modis_env.sh
    print_status "Activation script created: activate_modis_env.sh"
}

# Create usage instructions
create_usage_instructions() {
    print_info "Creating usage instructions..."
    
    cat > USAGE_WSL.md << 'EOF'
# Using MODIS Downloader in WSL

## Quick Start

1. **Activate the environment:**
   ```bash
   source activate_modis_env.sh
   ```

2. **Run the downloader:**
   ```bash
   python3 modis_downloader.py
   ```

## From Windows

### Using Batch File
Double-click `run_modis_downloader.bat` or run from Command Prompt:
```cmd
run_modis_downloader.bat
```

### Using PowerShell
```powershell
.\Run-ModisDownloader.ps1
```

## Manual WSL Commands

From Windows Command Prompt or PowerShell:
```cmd
wsl -d Ubuntu -- bash -c "cd /home/tofunori/saskatchewan-glacier-albedo-analysis/modis_data && source activate_modis_env.sh && python3 modis_downloader.py"
```

## Accessing Downloaded Data

- **WSL Path:** `/home/tofunori/saskatchewan-glacier-albedo-analysis/modis_data/modis_data/`
- **Windows Path:** `\\wsl.localhost\Ubuntu\home\tofunori\saskatchewan-glacier-albedo-analysis\modis_data\modis_data\`

## Environment Management

- **Activate:** `source activate_modis_env.sh`
- **Deactivate:** `deactivate`
- **Reinstall:** `./install_wsl_dependencies.sh`

## Troubleshooting

1. **Permission Issues:** Make sure scripts are executable
   ```bash
   chmod +x install_wsl_dependencies.sh activate_modis_env.sh
   ```

2. **GDAL Issues:** If GDAL installation fails, try:
   ```bash
   sudo apt install python3-gdal
   ```

3. **Network Issues:** Check NASA Earthdata credentials in `modis_downloader.py`

4. **WSL Access:** Ensure WSL is running and Ubuntu distribution is installed
EOF
    
    print_status "Usage instructions created: USAGE_WSL.md"
}

# Main installation process
main() {
    echo "Starting WSL dependency installation..."
    echo ""
    
    check_wsl
    check_directory
    
    echo ""
    print_info "This script will install the following:"
    print_info "• System dependencies (build tools, GDAL, etc.)"
    print_info "• Python virtual environment"
    print_info "• Python packages for MODIS analysis"
    print_info "• Helper scripts for easy usage"
    echo ""
    
    read -p "Continue with installation? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installation cancelled by user"
        exit 0
    fi
    
    echo ""
    print_info "Starting installation process..."
    
    update_packages
    install_system_deps
    setup_venv
    install_python_deps
    verify_installation
    create_activation_script
    create_usage_instructions
    
    echo ""
    echo "================================================================="
    print_status "Installation completed successfully!"
    echo "================================================================="
    echo ""
    print_info "Next steps:"
    echo "1. Review your NASA Earthdata credentials in modis_downloader.py"
    echo "2. Activate the environment: source activate_modis_env.sh"
    echo "3. Run the downloader: python3 modis_downloader.py"
    echo ""
    print_info "Or run from Windows using:"
    echo "• run_modis_downloader.bat"
    echo "• Run-ModisDownloader.ps1"
    echo ""
    print_info "See USAGE_WSL.md for detailed instructions"
    echo ""
}

# Run main function
main "$@"