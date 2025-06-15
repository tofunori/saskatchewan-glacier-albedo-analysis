#!/usr/bin/env python3
"""
MODIS clipper with encoding fixes for Windows paths
"""

import os
import glob
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from pathlib import Path
import numpy as np
import shutil
import tempfile

def fix_path_encoding(path):
    """Fix path encoding issues"""
    # Convert to string and normalize
    path_str = str(path)
    # Replace problematic characters
    path_str = path_str.replace('\\', '/')
    return path_str

def copy_to_temp_and_process():
    """Copy HDF files to temporary directory with ASCII names"""
    print("🔧 Fixing encoding issues by copying to temp directory...")
    
    # Original paths
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
    glacier_gdf = gpd.read_file(glacier_mask_path)
    print(f"✅ Loaded glacier mask ({glacier_gdf.geometry.iloc[0].geom_type})")
    
    # Find HDF files
    hdf_files = glob.glob(os.path.join(hdf_directory, "*.hdf"))
    print(f"📂 Found {len(hdf_files)} HDF files")
    
    if not hdf_files:
        print("❌ No HDF files found")
        return
    
    # Create temp directory with ASCII path
    temp_dir = tempfile.mkdtemp(prefix="modis_", dir="C:/temp")
    print(f"📁 Temp directory: {temp_dir}")
    
    # Create output directory
    os.makedirs(output_directory, exist_ok=True)
    
    success_count = 0
    
    try:
        for i, original_hdf in enumerate(hdf_files, 1):
            filename = os.path.basename(original_hdf)
            print(f"\n🔄 Processing {i}/{len(hdf_files)}: {filename}")
            
            # Copy to temp with simple ASCII name
            temp_hdf = os.path.join(temp_dir, f"temp_{i}.hdf")
            print(f"   📋 Copying to: {temp_hdf}")
            
            try:
                shutil.copy2(original_hdf, temp_hdf)
                print(f"   ✅ Copied successfully")
            except Exception as e:
                print(f"   ❌ Copy failed: {e}")
                continue
            
            # Process the temp file
            try:
                # Open temp HDF file
                with rasterio.open(temp_hdf) as src:
                    subdatasets = src.subdatasets
                
                print(f"   📊 Found {len(subdatasets)} subdatasets")
                
                # Find albedo datasets
                albedo_datasets = [s for s in subdatasets if 'Albedo' in s and ('shortwave' in s or 'WSA' in s)]
                
                if not albedo_datasets:
                    print("   ⚠️  No albedo datasets found")
                    # Try any albedo dataset
                    albedo_datasets = [s for s in subdatasets if 'Albedo' in s]
                
                print(f"   🎯 Found {len(albedo_datasets)} albedo dataset(s)")
                
                for j, dataset in enumerate(albedo_datasets):
                    dataset_name = dataset.split(':')[-1]
                    print(f"   📈 Processing: {dataset_name}")
                    
                    try:
                        with rasterio.open(dataset) as src:
                            print(f"      Size: {src.width} x {src.height}")
                            print(f"      CRS: {src.crs}")
                            print(f"      NoData: {src.nodata}")
                            
                            # Reproject glacier mask
                            glacier_proj = glacier_gdf.to_crs(src.crs)
                            
                            # Perform clipping
                            clipped_data, clipped_transform = mask(
                                src, 
                                glacier_proj.geometry, 
                                crop=True, 
                                nodata=src.nodata,
                                all_touched=True
                            )
                            
                            if clipped_data.size == 0:
                                print("      ⚠️  No data after clipping")
                                continue
                            
                            # Calculate statistics
                            original_data = src.read(1)
                            valid_original = np.count_nonzero(original_data != src.nodata)
                            valid_clipped = np.count_nonzero(clipped_data[0] != src.nodata)
                            
                            if valid_original > 0:
                                reduction = (1 - valid_clipped/valid_original) * 100
                            else:
                                reduction = 0
                            
                            print(f"      Original pixels: {valid_original:,}")
                            print(f"      Clipped pixels: {valid_clipped:,}")
                            print(f"      Reduction: {reduction:.1f}%")
                            
                            # Create output filename (using original filename)
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
                                compress='lzw'
                            ) as dst:
                                dst.write(clipped_data[0], 1)
                            
                            # Verify output
                            if os.path.exists(output_path):
                                output_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                                print(f"      ✅ Saved: {output_filename} ({output_size_mb:.2f} MB)")
                                success_count += 1
                            else:
                                print(f"      ❌ Output file not created")
                    
                    except Exception as e:
                        print(f"      ❌ Error processing {dataset_name}: {e}")
                        continue
            
            except Exception as e:
                print(f"   ❌ Error processing temp file: {e}")
                continue
            
            finally:
                # Clean up temp file
                try:
                    os.remove(temp_hdf)
                except:
                    pass
    
    finally:
        # Clean up temp directory
        try:
            os.rmdir(temp_dir)
        except:
            pass
    
    print(f"\n🎉 Processing complete!")
    print(f"   Successfully processed: {success_count} datasets")
    print(f"   Output directory: {output_directory}")
    
    # List output files
    output_files = glob.glob(os.path.join(output_directory, "*.tif"))
    if output_files:
        print(f"\n📄 Created {len(output_files)} clipped files:")
        total_size = 0
        for output_file in output_files:
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            total_size += size_mb
            print(f"   • {os.path.basename(output_file)} ({size_mb:.2f} MB)")
        print(f"   Total size: {total_size:.1f} MB")
        
        return True
    else:
        print("❌ No output files created")
        return False

def quick_verify():
    """Quick verification of clipped files"""
    print("\n🔍 Quick verification...")
    
    output_directory = r"D:\Downloads\MCD43A3_clipped"
    tif_files = glob.glob(os.path.join(output_directory, "*.tif"))
    
    if not tif_files:
        print("❌ No TIF files to verify")
        return
    
    print(f"✅ Found {len(tif_files)} TIF files")
    
    # Check first file in detail
    first_file = tif_files[0]
    print(f"\n📊 Checking: {os.path.basename(first_file)}")
    
    try:
        with rasterio.open(first_file) as src:
            print(f"   Dimensions: {src.width} x {src.height}")
            print(f"   CRS: {src.crs}")
            
            # Read some data
            data = src.read(1)
            valid_pixels = np.count_nonzero(data != src.nodata)
            print(f"   Valid pixels: {valid_pixels:,}")
            
            if valid_pixels > 0:
                valid_data = data[data != src.nodata]
                print(f"   Value range: {valid_data.min():.3f} to {valid_data.max():.3f}")
                print(f"   Mean value: {valid_data.mean():.3f}")
            
            print("   ✅ File appears valid")
    
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")

if __name__ == "__main__":
    print("🛠️  MODIS Encoding Fix Clipper")
    print("=" * 40)
    
    # Create temp directory if needed
    temp_base = "C:/temp"
    if not os.path.exists(temp_base):
        try:
            os.makedirs(temp_base)
            print(f"📁 Created temp directory: {temp_base}")
        except:
            print("⚠️  Could not create C:/temp, using system temp")
    
    success = copy_to_temp_and_process()
    
    if success:
        quick_verify()
        
        print(f"\n🎯 SUCCESS!")
        print("Your MODIS files are now clipped to glacier boundaries!")
        print(f"Check: D:\\Downloads\\MCD43A3_clipped\\")
    else:
        print(f"\n❌ Processing failed")
        print("Try moving HDF files to a path without special characters")