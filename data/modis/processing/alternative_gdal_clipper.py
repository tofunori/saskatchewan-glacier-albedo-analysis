#!/usr/bin/env python3
"""
Alternative MODIS clipper using GDAL directly instead of rasterio
Avoids rasterio UTF-8 encoding issues
"""

import os
import glob
import geopandas as gpd
import subprocess
import tempfile
import numpy as np
from pathlib import Path

def check_gdal_installation():
    """Check if GDAL command line tools are available"""
    try:
        result = subprocess.run(['gdalinfo', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ GDAL available: {result.stdout.strip()}")
            return True
        else:
            print("❌ GDAL command line tools not found")
            return False
    except:
        print("❌ GDAL command line tools not found")
        return False

def list_hdf_subdatasets(hdf_file):
    """List subdatasets in HDF file using gdalinfo"""
    try:
        result = subprocess.run(['gdalinfo', hdf_file], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"   ❌ gdalinfo failed: {result.stderr}")
            return []
        
        # Parse subdatasets from gdalinfo output
        subdatasets = []
        lines = result.stdout.split('\n')
        
        for line in lines:
            if 'SUBDATASET_' in line and '_NAME=' in line:
                # Extract the HDF4_EOS path
                if '=' in line:
                    subdataset = line.split('=', 1)[1]
                    subdatasets.append(subdataset)
        
        return subdatasets
        
    except Exception as e:
        print(f"   ❌ Error listing subdatasets: {e}")
        return []

def clip_with_gdal_warp(input_dataset, output_file, glacier_geojson):
    """Clip using gdal_warp command line tool"""
    try:
        # Build gdal_warp command
        cmd = [
            'gdalwarp',
            '-of', 'GTiff',
            '-co', 'COMPRESS=LZW',
            '-cutline', glacier_geojson,
            '-crop_to_cutline',
            '-dstnodata', '-9999',
            input_dataset,
            output_file
        ]
        
        # Execute command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            if os.path.exists(output_file):
                size_mb = os.path.getsize(output_file) / (1024 * 1024)
                print(f"      ✅ Created: {os.path.basename(output_file)} ({size_mb:.2f} MB)")
                return True
            else:
                print("      ❌ Output file not created")
                return False
        else:
            print(f"      ❌ gdal_warp failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"      ❌ Error in gdal_warp: {e}")
        return False

def process_with_gdal():
    """Process MODIS files using pure GDAL command line tools"""
    print("🛠️  Alternative GDAL-based MODIS Clipper")
    print("=" * 45)
    
    # Configuration
    hdf_directory = r"D:\Downloads\MCD43A3_downloads"
    glacier_mask_path = r"D:\Downloads\saskatchewan_glacier_mask.geojson"
    output_directory = r"D:\Downloads\MCD43A3_clipped_gdal"
    
    # Check GDAL
    if not check_gdal_installation():
        print("\n💡 GDAL command line tools are needed!")
        print("Install with: conda install -c conda-forge gdal")
        return False
    
    # Check inputs
    if not os.path.exists(hdf_directory):
        print(f"❌ HDF directory not found: {hdf_directory}")
        return False
    
    if not os.path.exists(glacier_mask_path):
        print(f"❌ Glacier mask not found: {glacier_mask_path}")
        return False
    
    # Load and check glacier mask
    try:
        glacier_gdf = gpd.read_file(glacier_mask_path)
        print(f"✅ Loaded glacier mask")
        print(f"   Geometry: {glacier_gdf.geometry.iloc[0].geom_type}")
        print(f"   CRS: {glacier_gdf.crs}")
    except Exception as e:
        print(f"❌ Error loading glacier mask: {e}")
        return False
    
    # Find HDF files
    hdf_files = glob.glob(os.path.join(hdf_directory, "*.hdf"))
    print(f"📂 Found {len(hdf_files)} HDF files")
    
    if not hdf_files:
        print("❌ No HDF files found")
        return False
    
    # Create output directory
    os.makedirs(output_directory, exist_ok=True)
    print(f"📁 Output directory: {output_directory}")
    
    success_count = 0
    
    for i, hdf_file in enumerate(hdf_files, 1):
        filename = os.path.basename(hdf_file)
        print(f"\n🔄 Processing {i}/{len(hdf_files)}: {filename}")
        
        # List subdatasets using gdalinfo
        subdatasets = list_hdf_subdatasets(hdf_file)
        
        if not subdatasets:
            print("   ❌ No subdatasets found")
            continue
        
        print(f"   📊 Found {len(subdatasets)} subdatasets")
        
        # Find albedo datasets
        albedo_datasets = [s for s in subdatasets if 'Albedo' in s and ('shortwave' in s or 'WSA' in s)]
        
        if not albedo_datasets:
            # Try any albedo dataset
            albedo_datasets = [s for s in subdatasets if 'Albedo' in s]
        
        if not albedo_datasets:
            print("   ⚠️  No albedo datasets found")
            continue
        
        print(f"   🎯 Processing {len(albedo_datasets)} albedo dataset(s)")
        
        for j, dataset in enumerate(albedo_datasets):
            dataset_name = dataset.split(':')[-1] if ':' in dataset else f"dataset_{j}"
            print(f"   📈 Processing: {dataset_name}")
            
            # Create output filename
            base_name = os.path.splitext(filename)[0]
            output_filename = f"{base_name}_{dataset_name}_clipped.tif"
            output_path = os.path.join(output_directory, output_filename)
            
            # Clip using gdal_warp
            if clip_with_gdal_warp(dataset, output_path, glacier_mask_path):
                success_count += 1
    
    print(f"\n🎉 Processing complete!")
    print(f"   Successfully processed: {success_count} datasets")
    
    # List output files
    output_files = glob.glob(os.path.join(output_directory, "*.tif"))
    if output_files:
        print(f"\n📄 Created {len(output_files)} files:")
        total_size = 0
        for output_file in output_files:
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            total_size += size_mb
            print(f"   • {os.path.basename(output_file)} ({size_mb:.2f} MB)")
        print(f"   Total size: {total_size:.1f} MB")
        return True
    else:
        print("❌ No files created")
        return False

def verify_with_gdalinfo():
    """Verify output files using gdalinfo"""
    print("\n🔍 Verifying output files...")
    
    output_directory = r"D:\Downloads\MCD43A3_clipped_gdal"
    tif_files = glob.glob(os.path.join(output_directory, "*.tif"))
    
    if not tif_files:
        print("❌ No files to verify")
        return
    
    # Check first file
    first_file = tif_files[0]
    print(f"\n📊 Checking: {os.path.basename(first_file)}")
    
    try:
        result = subprocess.run(['gdalinfo', '-stats', first_file], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ File is valid")
            
            # Extract key info
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Size is' in line:
                    print(f"   {line.strip()}")
                elif 'Coordinate System is' in line:
                    print(f"   CRS: {line.split('is')[1].strip()}")
                elif 'STATISTICS_MINIMUM' in line:
                    print(f"   {line.strip()}")
                elif 'STATISTICS_MAXIMUM' in line:
                    print(f"   {line.strip()}")
        else:
            print(f"   ❌ gdalinfo failed: {result.stderr}")
            
    except Exception as e:
        print(f"   ❌ Error verifying: {e}")

def install_gdal_help():
    """Provide help for installing GDAL"""
    print("\n📖 GDAL Installation Help")
    print("=" * 30)
    print("If GDAL command line tools are missing:")
    print("\n1️⃣ In your conda environment:")
    print("   conda install -c conda-forge gdal")
    print("\n2️⃣ Or using conda-forge:")
    print("   conda install -c conda-forge libgdal")
    print("\n3️⃣ Verify installation:")
    print("   gdalinfo --version")
    print("\n4️⃣ If still issues, try:")
    print("   conda install -c conda-forge rasterio gdal")

if __name__ == "__main__":
    success = process_with_gdal()
    
    if success:
        verify_with_gdalinfo()
        print(f"\n🎯 SUCCESS!")
        print("Your MODIS files are clipped using GDAL!")
        print(f"Check: D:\\Downloads\\MCD43A3_clipped_gdal\\")
    else:
        install_gdal_help()
        print(f"\n💡 This approach avoids rasterio encoding issues completely!")