#!/usr/bin/env python3
"""
Analyze spatial filtering effectiveness and propose solutions
"""

import os
from pathlib import Path
import geopandas as gpd
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import box

def analyze_downloaded_files():
    """Analyze what was actually downloaded"""
    print("🔍 Analyzing downloaded MODIS files...")
    
    download_dir = Path("D:/Downloads/MCD43A3_downloads")
    
    if not download_dir.exists():
        print(f"❌ Download directory not found: {download_dir}")
        return
    
    # Find HDF files
    hdf_files = list(download_dir.glob("*.hdf"))
    
    if not hdf_files:
        print("❌ No HDF files found in download directory")
        return
    
    print(f"✅ Found {len(hdf_files)} HDF files:")
    
    for i, file_path in enumerate(hdf_files, 1):
        print(f"   {i}. {file_path.name}")
        
        # Get file size
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"      Size: {size_mb:.1f} MB")
        
        # Try to get basic info about the file
        try:
            with rasterio.open(f"HDF4_EOS:EOS_GRID:{file_path}:MOD_Grid_BRDF:Albedo_WSA_shortwave") as src:
                print(f"      Dimensions: {src.width} x {src.height}")
                print(f"      Bounds: {src.bounds}")
                print(f"      CRS: {src.crs}")
        except Exception as e:
            print(f"      ⚠️  Could not read raster info: {e}")
    
    return hdf_files

def compare_glacier_mask_vs_granule_coverage():
    """Compare glacier mask with MODIS granule coverage"""
    print("\n🎯 Comparing glacier mask with MODIS granule coverage...")
    
    # Load glacier mask
    glacier_mask_path = r"D:\Downloads\saskatchewan_glacier_mask.geojson"
    
    try:
        glacier_gdf = gpd.read_file(glacier_mask_path)
        
        print(f"✅ Loaded glacier mask:")
        print(f"   Geometry type: {glacier_gdf.geometry.iloc[0].type}")
        print(f"   Bounds: {glacier_gdf.bounds.iloc[0].to_dict()}")
        print(f"   Area: {glacier_gdf.geometry.iloc[0].area:.6f} degrees²")
        
        # Convert to approximate area in km²
        # Rough conversion at 52°N latitude
        lat_km_per_degree = 111.0
        lon_km_per_degree = 111.0 * np.cos(np.radians(52.0))
        
        area_km2 = glacier_gdf.geometry.iloc[0].area * lat_km_per_degree * lon_km_per_degree
        print(f"   Approximate area: {area_km2:.2f} km²")
        
        # MODIS tile information
        modis_tile_size_km = 1200  # Approximate MODIS tile size
        modis_pixel_size_m = 500   # MCD43A3 pixel size
        
        print(f"\n📊 MODIS vs Glacier size comparison:")
        print(f"   Glacier area: {area_km2:.1f} km²")
        print(f"   MODIS tile area: ~{modis_tile_size_km * modis_tile_size_km:,} km²")
        print(f"   Glacier is {(area_km2 / (modis_tile_size_km * modis_tile_size_km)) * 100:.3f}% of a MODIS tile")
        
        # Explain the spatial filtering limitation
        print(f"\n💡 SPATIAL FILTERING EXPLANATION:")
        print(f"   • MODIS spatial filtering works at GRANULE level")
        print(f"   • If ANY part of your glacier intersects a granule, the ENTIRE granule is downloaded")
        print(f"   • Your glacier ({area_km2:.1f} km²) is much smaller than a MODIS tile")
        print(f"   • This is why you get 'extra' pixels around your glacier")
        
        return glacier_gdf
        
    except Exception as e:
        print(f"❌ Could not load glacier mask: {e}")
        return None

def demonstrate_pixel_level_clipping():
    """Demonstrate how to clip MODIS data to glacier pixels"""
    print("\n✂️  Demonstrating pixel-level clipping...")
    
    download_dir = Path("D:/Downloads/MCD43A3_downloads")
    hdf_files = list(download_dir.glob("*.hdf"))
    glacier_mask_path = r"D:\Downloads\saskatchewan_glacier_mask.geojson"
    
    if not hdf_files:
        print("❌ No HDF files to process")
        return
    
    if not os.path.exists(glacier_mask_path):
        print("❌ Glacier mask not found")
        return
    
    try:
        # Load glacier mask
        glacier_gdf = gpd.read_file(glacier_mask_path)
        
        # Process first HDF file as example
        hdf_file = hdf_files[0]
        print(f"📂 Processing: {hdf_file.name}")
        
        # List available subdatasets
        with rasterio.open(str(hdf_file)) as src:
            subdatasets = src.subdatasets
            
        print(f"   Found {len(subdatasets)} subdatasets:")
        for i, subdataset in enumerate(subdatasets[:5], 1):  # Show first 5
            dataset_name = subdataset.split(':')[-1]
            print(f"     {i}. {dataset_name}")
        
        # Try to open albedo data
        albedo_datasets = [s for s in subdatasets if 'Albedo' in s and 'shortwave' in s]
        
        if albedo_datasets:
            albedo_dataset = albedo_datasets[0]
            print(f"\n📊 Opening albedo dataset: {albedo_dataset.split(':')[-1]}")
            
            with rasterio.open(albedo_dataset) as src:
                print(f"   Dimensions: {src.width} x {src.height}")
                print(f"   Data type: {src.dtypes[0]}")
                print(f"   No data value: {src.nodata}")
                
                # Read the data
                albedo_data = src.read(1)
                
                # Convert glacier mask to same CRS as raster
                glacier_gdf_proj = glacier_gdf.to_crs(src.crs)
                
                # Clip raster to glacier geometry
                from rasterio.mask import mask
                
                clipped_data, clipped_transform = mask(
                    src, 
                    glacier_gdf_proj.geometry, 
                    crop=True,
                    nodata=src.nodata
                )
                
                print(f"\n✂️  Clipping results:")
                print(f"   Original shape: {albedo_data.shape}")
                print(f"   Clipped shape: {clipped_data[0].shape}")
                
                # Calculate statistics
                valid_original = albedo_data[albedo_data != src.nodata]
                valid_clipped = clipped_data[0][clipped_data[0] != src.nodata]
                
                print(f"   Original valid pixels: {len(valid_original):,}")
                print(f"   Clipped valid pixels: {len(valid_clipped):,}")
                print(f"   Reduction: {(1 - len(valid_clipped)/len(valid_original))*100:.1f}%")
                
                # Save clipped result
                output_path = download_dir / f"clipped_{hdf_file.stem}_albedo.tif"
                
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
                    nodata=src.nodata
                ) as dst:
                    dst.write(clipped_data[0], 1)
                
                print(f"   ✅ Saved clipped raster: {output_path}")
                
                return output_path
        else:
            print("   ❌ No albedo datasets found")
            
    except Exception as e:
        print(f"❌ Clipping failed: {e}")
        import traceback
        traceback.print_exc()
    
    return None

def create_clipping_script():
    """Create a reusable script for clipping MODIS data"""
    print("\n📝 Creating reusable clipping script...")
    
    script_content = '''#!/usr/bin/env python3
"""
Clip MODIS HDF files to glacier geometry
"""

import os
import glob
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from pathlib import Path

def clip_modis_files(hdf_directory, glacier_mask_path, output_directory):
    """Clip all MODIS HDF files to glacier geometry"""
    
    # Load glacier mask
    glacier_gdf = gpd.read_file(glacier_mask_path)
    print(f"✅ Loaded glacier mask: {glacier_mask_path}")
    
    # Find HDF files
    hdf_files = glob.glob(os.path.join(hdf_directory, "*.hdf"))
    print(f"📂 Found {len(hdf_files)} HDF files")
    
    # Create output directory
    Path(output_directory).mkdir(exist_ok=True)
    
    for hdf_file in hdf_files:
        print(f"\\n🔄 Processing: {os.path.basename(hdf_file)}")
        
        try:
            # Open HDF file to find subdatasets
            with rasterio.open(hdf_file) as src:
                subdatasets = src.subdatasets
            
            # Process albedo datasets
            albedo_datasets = [s for s in subdatasets if 'Albedo' in s]
            
            for dataset in albedo_datasets:
                dataset_name = dataset.split(':')[-1]
                print(f"   📊 Processing: {dataset_name}")
                
                with rasterio.open(dataset) as src:
                    # Reproject glacier to raster CRS
                    glacier_proj = glacier_gdf.to_crs(src.crs)
                    
                    # Clip
                    clipped_data, clipped_transform = mask(
                        src, glacier_proj.geometry, crop=True, nodata=src.nodata
                    )
                    
                    # Save clipped raster
                    output_filename = f"clipped_{os.path.basename(hdf_file)[:-4]}_{dataset_name}.tif"
                    output_path = os.path.join(output_directory, output_filename)
                    
                    with rasterio.open(
                        output_path, 'w', 
                        driver='GTiff',
                        height=clipped_data.shape[1], width=clipped_data.shape[2], count=1,
                        dtype=clipped_data.dtype, crs=src.crs, transform=clipped_transform,
                        nodata=src.nodata
                    ) as dst:
                        dst.write(clipped_data[0], 1)
                    
                    print(f"   ✅ Saved: {output_filename}")
                    
        except Exception as e:
            print(f"   ❌ Error processing {hdf_file}: {e}")

if __name__ == "__main__":
    # Configuration
    hdf_directory = "D:/Downloads/MCD43A3_downloads"
    glacier_mask_path = r"D:\\Downloads\\saskatchewan_glacier_mask.geojson"
    output_directory = "D:/Downloads/MCD43A3_clipped"
    
    clip_modis_files(hdf_directory, glacier_mask_path, output_directory)
    print("\\n🎉 Clipping complete!")
'''
    
    script_path = Path("D:/Downloads/clip_modis_to_glacier.py")
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"✅ Created clipping script: {script_path}")
    print(f"📖 Usage: python {script_path}")
    
    return script_path

def main():
    """Main analysis function"""
    print("🔍 MODIS Spatial Filtering Analysis")
    print("=" * 50)
    
    # Analyze what was downloaded
    hdf_files = analyze_downloaded_files()
    
    # Explain spatial filtering limitations
    glacier_gdf = compare_glacier_mask_vs_granule_coverage()
    
    # Demonstrate pixel-level clipping
    if hdf_files and glacier_gdf is not None:
        clipped_file = demonstrate_pixel_level_clipping()
        
        if clipped_file:
            print(f"\n🎉 SUCCESS: Pixel-level clipping works!")
            print(f"   Clipped file: {clipped_file}")
    
    # Create reusable script
    script_path = create_clipping_script()
    
    print(f"\n" + "=" * 50)
    print("📋 SUMMARY:")
    print("1. ✅ MODIS spatial filtering downloads entire granules (this is normal)")
    print("2. ✅ For pixel-level precision, you need post-processing clipping")
    print("3. ✅ Clipping script created for processing all your files")
    print(f"4. 🚀 Run: python {script_path}")

if __name__ == "__main__":
    main()