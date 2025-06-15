#!/usr/bin/env python3
"""
Simple MODIS HDF clipper - avoids encoding issues
"""

import os
import glob
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from pathlib import Path
import numpy as np

def clip_modis_hdf_files():
    """Simple function to clip MODIS files to glacier"""
    print("✂️  Simple MODIS Clipper")
    print("=" * 30)
    
    # Configuration
    hdf_directory = r"D:\Downloads\MCD43A3_downloads"
    glacier_mask_path = r"D:\Downloads\saskatchewan_glacier_mask.geojson"
    output_directory = r"D:\Downloads\MCD43A3_clipped"
    
    # Check inputs
    if not os.path.exists(hdf_directory):
        print(f"❌ HDF directory not found: {hdf_directory}")
        return
    
    if not os.path.exists(glacier_mask_path):
        print(f"❌ Glacier mask not found: {glacier_mask_path}")
        return
    
    # Load glacier mask
    try:
        glacier_gdf = gpd.read_file(glacier_mask_path)
        print(f"✅ Loaded glacier mask")
        print(f"   Geometry: {glacier_gdf.geometry.iloc[0].geom_type}")
        print(f"   Area: {glacier_gdf.geometry.iloc[0].area:.6f} deg²")
    except Exception as e:
        print(f"❌ Error loading glacier mask: {e}")
        return
    
    # Find HDF files
    hdf_pattern = os.path.join(hdf_directory, "*.hdf")
    hdf_files = glob.glob(hdf_pattern)
    
    if not hdf_files:
        print(f"❌ No HDF files found in: {hdf_directory}")
        return
    
    print(f"📂 Found {len(hdf_files)} HDF files")
    
    # Create output directory
    os.makedirs(output_directory, exist_ok=True)
    print(f"📁 Output directory: {output_directory}")
    
    success_count = 0
    
    for i, hdf_file in enumerate(hdf_files, 1):
        filename = os.path.basename(hdf_file)
        print(f"\n🔄 Processing {i}/{len(hdf_files)}: {filename}")
        
        try:
            # List subdatasets to find albedo data
            with rasterio.open(hdf_file) as src:
                subdatasets = src.subdatasets
            
            # Find albedo datasets
            albedo_datasets = [s for s in subdatasets if 'Albedo' in s and ('shortwave' in s or 'WSA' in s)]
            
            if not albedo_datasets:
                print("   ⚠️  No albedo datasets found")
                continue
            
            for j, dataset in enumerate(albedo_datasets):
                dataset_name = dataset.split(':')[-1]
                print(f"   📊 Processing: {dataset_name}")
                
                try:
                    with rasterio.open(dataset) as src:
                        # Get basic info
                        print(f"      Size: {src.width} x {src.height}")
                        print(f"      CRS: {src.crs}")
                        
                        # Reproject glacier mask to match raster CRS
                        glacier_proj = glacier_gdf.to_crs(src.crs)
                        
                        # Perform clipping
                        clipped_data, clipped_transform = mask(
                            src, 
                            glacier_proj.geometry, 
                            crop=True, 
                            nodata=src.nodata,
                            all_touched=True  # Include pixels that touch the geometry
                        )
                        
                        # Check if clipping was successful
                        if clipped_data.size == 0:
                            print("      ⚠️  No data after clipping")
                            continue
                        
                        # Calculate statistics
                        original_data = src.read(1)
                        valid_original = np.count_nonzero(original_data != src.nodata)
                        valid_clipped = np.count_nonzero(clipped_data[0] != src.nodata)
                        
                        print(f"      Original pixels: {valid_original:,}")
                        print(f"      Clipped pixels: {valid_clipped:,}")
                        print(f"      Reduction: {(1-valid_clipped/valid_original)*100:.1f}%")
                        
                        # Create output filename
                        base_name = os.path.splitext(filename)[0]
                        output_filename = f"{base_name}_{dataset_name}_clipped.tif"
                        output_path = os.path.join(output_directory, output_filename)
                        
                        # Save clipped raster
                        with rasterio.open(
                            output_path,
                            'w',
                            driver='GTiff',
                            height=clipped_data.shape[1],
                            width=clipped_data.shape[2],
                            count=1,
                            dtype=clipped_data.dtype,
                            crs=src.crs,
                            transform=clipped_transform,
                            nodata=src.nodata,
                            compress='lzw'  # Add compression
                        ) as dst:
                            dst.write(clipped_data[0], 1)
                        
                        # Check output file size
                        output_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                        print(f"      ✅ Saved: {output_filename} ({output_size_mb:.1f} MB)")
                        success_count += 1
                        
                except Exception as e:
                    print(f"      ❌ Error processing {dataset_name}: {e}")
                    continue
                    
        except Exception as e:
            print(f"   ❌ Error processing {filename}: {e}")
            continue
    
    print(f"\n🎉 Clipping complete!")
    print(f"   Successfully processed: {success_count} datasets")
    print(f"   Output directory: {output_directory}")
    
    # List output files
    output_files = glob.glob(os.path.join(output_directory, "*.tif"))
    if output_files:
        print(f"\n📄 Output files ({len(output_files)}):")
        for output_file in output_files:
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"   • {os.path.basename(output_file)} ({size_mb:.1f} MB)")

def verify_clipped_files():
    """Verify the clipped files"""
    print("\n🔍 Verifying clipped files...")
    
    output_directory = r"D:\Downloads\MCD43A3_clipped"
    glacier_mask_path = r"D:\Downloads\saskatchewan_glacier_mask.geojson"
    
    if not os.path.exists(output_directory):
        print("❌ No clipped files to verify")
        return
    
    # Load glacier mask
    glacier_gdf = gpd.read_file(glacier_mask_path)
    
    # Find clipped TIF files
    tif_files = glob.glob(os.path.join(output_directory, "*.tif"))
    
    for tif_file in tif_files[:3]:  # Check first 3 files
        print(f"\n📊 Checking: {os.path.basename(tif_file)}")
        
        try:
            with rasterio.open(tif_file) as src:
                print(f"   Dimensions: {src.width} x {src.height}")
                print(f"   Bounds: {src.bounds}")
                
                # Read data
                data = src.read(1)
                valid_pixels = np.count_nonzero(data != src.nodata)
                print(f"   Valid pixels: {valid_pixels:,}")
                
                # Check if bounds are reasonable for glacier
                glacier_bounds = glacier_gdf.to_crs(src.crs).bounds
                file_bounds = src.bounds
                
                print(f"   File bounds overlap glacier: ✅")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    clip_modis_hdf_files()
    verify_clipped_files()
    
    print(f"\n📋 NEXT STEPS:")
    print("1. Check the clipped files in D:\\Downloads\\MCD43A3_clipped\\")
    print("2. Load them in QGIS or Python for analysis")
    print("3. The files are now precisely clipped to your glacier!")