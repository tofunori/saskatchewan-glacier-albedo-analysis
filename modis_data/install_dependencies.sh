#!/bin/bash
# Installation script for MODIS data processing dependencies

echo "🛠️  Installing MODIS Data Processing Dependencies"
echo "================================================="

echo "1. Installing system packages..."
sudo apt update
sudo apt install -y python3-pip python3-venv python3-geopandas python3-shapely python3-gdal

echo ""
echo "2. Installing Python packages..."
python3 -m pip install --user modis-tools

echo ""
echo "3. Testing installation..."
python3 -c "
try:
    import geopandas as gpd
    import shapely
    from modis_tools.auth import ModisSession
    print('✅ All dependencies installed successfully!')
except ImportError as e:
    print(f'❌ Installation error: {e}')
    print('Try running: sudo apt install python3-geopandas python3-shapely python3-gdal')
"

echo ""
echo "🎯 Installation complete! Now you can run:"
echo "   python3 modis_downloader.py"
echo "   or"
echo "   python3 debug_spatial.py"