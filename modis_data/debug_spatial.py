#!/usr/bin/env python3
"""
Debug script to test spatial file loading and MODIS connections
"""

import os
import sys
from pathlib import Path

def test_python_environment():
    """Test Python environment and basic setup"""
    print("🐍 Python Environment Information:")
    print(f"   Python version: {sys.version}")
    print(f"   Python executable: {sys.executable}")
    print(f"   Current working directory: {os.getcwd()}")
    print(f"   Script location: {Path(__file__).parent}")
    
def test_spatial_libraries():
    """Test if spatial libraries are available"""
    print("🔍 Testing spatial library imports...")
    
    try:
        import geopandas as gpd
        print("✅ geopandas available")
    except ImportError as e:
        print(f"❌ geopandas not available: {e}")
        return False
    
    try:
        import shapely.geometry
        print("✅ shapely available")
    except ImportError as e:
        print(f"❌ shapely not available: {e}")
        return False
    
    try:
        from osgeo import ogr
        print("✅ GDAL/OGR available")
    except ImportError as e:
        print(f"❌ GDAL/OGR not available: {e}")
        print("   Install with: pip install gdal")
        return False
    
    return True

def test_file_paths():
    """Test if glacier mask files exist and are readable"""
    print("\n📁 Testing file paths...")
    
    # Use absolute paths to the mask directory
    project_dir = Path("/home/tofunori/saskatchewan-glacier-albedo-analysis/modis_data")
    mask_dir = project_dir / "mask"
    
    print(f"🔍 Looking for mask directory at: {mask_dir}")
    
    if not mask_dir.exists():
        print(f"❌ Mask directory not found: {mask_dir}")
        return None
    
    print(f"✅ Mask directory exists: {mask_dir}")
    
    # List all files in mask directory
    print("\n📋 Files in mask directory:")
    for file in mask_dir.iterdir():
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"   {file.name} ({size_mb:.2f} MB)")
    
    # Test different file formats using absolute paths
    test_files = [
        mask_dir / "saskatchewan_glacier_shapefile.shp",
        mask_dir / "saskatchewan_glacier_mask.geojson"
    ]
    
    available_files = []
    for file_path in test_files:
        if file_path.exists():
            print(f"✅ Found: {file_path}")
            available_files.append(str(file_path))
        else:
            print(f"❌ Not found: {file_path}")
    
    return available_files

def test_file_loading(file_path):
    """Test loading a specific file"""
    print(f"\n🔍 Testing file loading: {file_path}")
    
    try:
        import geopandas as gpd
        gdf = gpd.read_file(file_path)
        
        print(f"✅ Successfully loaded {file_path}")
        print(f"   Rows: {len(gdf)}")
        print(f"   Columns: {list(gdf.columns)}")
        print(f"   CRS: {gdf.crs}")
        print(f"   Geometry type: {gdf.geometry.iloc[0].type if len(gdf) > 0 else 'No geometry'}")
        
        if len(gdf) > 0:
            bounds = gdf.bounds
            print(f"   Bounds: {bounds.iloc[0].to_dict()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return False

def test_modis_connection():
    """Test basic MODIS connection without spatial filtering"""
    print("\n🌍 Testing MODIS connection...")
    
    try:
        from modis_tools.auth import ModisSession
        from modis_tools.resources import CollectionApi
        
        # Test basic connection
        session = ModisSession()
        print("✅ MODIS session created")
        
        collection_client = CollectionApi(session=session)
        print("✅ Collection client created")
        
        # Test a simple query (no spatial filtering)
        print("🔍 Testing simple collection query...")
        collections = collection_client.query(short_name="MOD10A1", version="061")
        collections_list = list(collections)
        print(f"✅ Found {len(collections_list)} MOD10A1 collections")
        
        if collections_list:
            return True
        else:
            print("❌ No collections found")
            return False
            
    except Exception as e:
        print(f"❌ MODIS connection error: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    print("🛠️  MODIS Spatial Debugging Tool")
    print("=" * 50)
    
    # Test 0: Python environment
    test_python_environment()
    
    # Test 1: Spatial libraries
    spatial_ok = test_spatial_libraries()
    
    # Test 2: File paths
    available_files = test_file_paths()
    
    # Test 3: File loading
    if spatial_ok and available_files:
        for file_path in available_files:
            test_file_loading(file_path)
    
    # Test 4: Basic MODIS connection
    modis_ok = test_modis_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY:")
    print(f"✅ Spatial libraries: {'OK' if spatial_ok else 'FAILED'}")
    print(f"✅ Glacier mask files: {'OK' if available_files else 'FAILED'}")
    print(f"✅ MODIS connection: {'OK' if modis_ok else 'FAILED'}")
    
    if spatial_ok and available_files and modis_ok:
        print("\n🎯 Everything looks good! Your setup should work.")
        print("   Try using the GeoJSON file if shapefile has issues:")
        print("   glacier_mask_path = 'mask/saskatchewan_glacier_mask.geojson'")
    else:
        print("\n🔧 Issues found. Install missing dependencies:")
        print("   pip install geopandas shapely gdal")

if __name__ == "__main__":
    main()