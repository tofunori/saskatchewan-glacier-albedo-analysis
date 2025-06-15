#!/usr/bin/env python3
"""
Simple MCD43A3 Albedo Data Downloader
Focus only on the working product
"""

import os
import glob
import subprocess
from pathlib import Path
from modis_tools.auth import ModisSession
from modis_tools.resources import CollectionApi, GranuleApi
from modis_tools.granule_handler import GranuleHandler

# Optional spatial processing
try:
    import geopandas as gpd
    SPATIAL_SUPPORT = True
except ImportError:
    SPATIAL_SUPPORT = False

class MCD43A3Downloader:
    """Simple downloader for MCD43A3 albedo data only"""
    
    def __init__(self, username, password, glacier_mask_path=None):
        self.username = username
        self.password = password
        self.session = None
        self.glacier_geometry = None
        
        # Saskatchewan Glacier bounding box
        self.saskatchewan_bbox = [-117.3, 52.1, -117.1, 52.3]
        
        # Use Windows Downloads directory
        self.output_dir = Path("D:/Downloads/MCD43A3_downloads")
        self.output_dir.mkdir(exist_ok=True)
        
        # Load glacier mask if provided
        if glacier_mask_path:
            self._load_glacier_mask(glacier_mask_path)
        
        print(f"📁 Downloads will be saved to: {self.output_dir}")
    
    def _load_glacier_mask(self, mask_path):
        """Load glacier mask"""
        if not SPATIAL_SUPPORT:
            print("⚠️  No spatial libraries, using bounding box")
            return
        
        try:
            gdf = gpd.read_file(mask_path)
            if len(gdf) > 1:
                try:
                    self.glacier_geometry = gdf.geometry.union_all()
                except AttributeError:
                    self.glacier_geometry = gdf.geometry.unary_union
            else:
                self.glacier_geometry = gdf.geometry.iloc[0]
            
            print(f"✅ Loaded glacier mask")
            print(f"   Bounds: {self.glacier_geometry.bounds}")
        except Exception as e:
            print(f"⚠️  Could not load mask: {e}")
    
    def authenticate(self):
        """Authenticate with NASA"""
        self.session = ModisSession(username=self.username, password=self.password)
        print("✅ Authenticated with NASA Earthdata")
    
    def get_spatial_filter(self):
        """Get spatial filter"""
        if self.glacier_geometry is not None:
            return {"spatial": self.glacier_geometry}
        else:
            return {"bounding_box": self.saskatchewan_bbox}
    
    def download_mcd43a3(self, start_date, end_date, max_files=5):
        """Download MCD43A3 albedo data"""
        if not self.session:
            self.authenticate()
        
        print(f"🔍 Searching MCD43A3 albedo data ({start_date} to {end_date})")
        
        # Get collection
        collection_client = CollectionApi(session=self.session)
        collections = collection_client.query(short_name="MCD43A3", version="061")
        collections_list = list(collections)
        
        if not collections_list:
            print("❌ No MCD43A3 collections found")
            return []
        
        print(f"✅ Found MCD43A3 collection")
        
        # Query granules
        granule_client = GranuleApi.from_collection(collections_list[0], session=self.session)
        spatial_filter = self.get_spatial_filter()
        
        query_params = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": max_files
        }
        query_params.update(spatial_filter)
        
        print(f"🔍 Querying granules...")
        granules = granule_client.query(**query_params)
        granules_list = list(granules)
        
        print(f"✅ Found {len(granules_list)} granules")
        
        if not granules_list:
            print("❌ No granules found for your criteria")
            return []
        
        # Download with very conservative settings
        print(f"📥 Starting download of {len(granules_list)} files...")
        print(f"   Using single thread to avoid timeout")
        
        try:
            file_paths = GranuleHandler.download_from_granules(
                granules_list,
                modis_session=self.session,
                path=str(self.output_dir),
                threads=1,  # Single thread
                ext=("hdf",)  # Only HDF files
            )
            
            print(f"✅ Successfully downloaded {len(file_paths)} files!")
            
            # Show downloaded files
            for i, path in enumerate(file_paths, 1):
                if os.path.exists(path):
                    size_mb = os.path.getsize(path) / (1024 * 1024)
                    filename = os.path.basename(path)
                    print(f"   {i}. {filename} ({size_mb:.1f} MB)")
            
            return file_paths
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            
            # Try with just one file
            if len(granules_list) > 1:
                print(f"🔄 Retrying with just 1 file...")
                try:
                    file_paths = GranuleHandler.download_from_granules(
                        granules_list[:1],
                        modis_session=self.session,
                        path=str(self.output_dir),
                        threads=1
                    )
                    print(f"✅ Downloaded {len(file_paths)} file(s) on retry")
                    return file_paths
                except Exception as e2:
                    print(f"❌ Retry also failed: {e2}")
            
            return []
    
    def check_gdal_availability(self):
        """Check if GDAL command line tools are available"""
        try:
            result = subprocess.run(['gdalinfo', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ GDAL available: {result.stdout.strip()}")
                return True
            else:
                print("⚠️  GDAL command line tools not found")
                return False
        except:
            print("⚠️  GDAL command line tools not found")
            return False
    
    def list_hdf_subdatasets(self, hdf_file):
        """List subdatasets in HDF file using gdalinfo"""
        try:
            result = subprocess.run(['gdalinfo', str(hdf_file)], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return []
            
            # Parse subdatasets from gdalinfo output
            subdatasets = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'SUBDATASET_' in line and '_NAME=' in line:
                    if '=' in line:
                        subdataset = line.split('=', 1)[1]
                        subdatasets.append(subdataset)
            
            return subdatasets
            
        except Exception:
            return []
    
    def clip_with_gdal_warp(self, input_dataset, output_file, glacier_geojson):
        """Clip using gdal_warp command line tool"""
        try:
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
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and os.path.exists(output_file):
                size_mb = os.path.getsize(output_file) / (1024 * 1024)
                print(f"      ✅ Clipped: {os.path.basename(output_file)} ({size_mb:.2f} MB)")
                return True
            else:
                print(f"      ❌ Clipping failed")
                return False
                
        except Exception as e:
            print(f"      ❌ Error in clipping: {e}")
            return False
    
    def auto_clip_downloaded_files(self):
        """Automatically clip downloaded HDF files to glacier geometry"""
        print(f"\n✂️  Auto-clipping downloaded files to glacier geometry...")
        
        # Check if we have the required tools and files
        if not self.check_gdal_availability():
            print("⚠️  GDAL tools not available - skipping auto-clipping")
            print("   Install with: conda install -c conda-forge gdal")
            return False
        
        # Find downloaded HDF files
        hdf_files = list(self.output_dir.glob("*.hdf"))
        
        if not hdf_files:
            print("❌ No HDF files found to clip")
            return False
        
        # Check for glacier mask file
        possible_masks = [
            r"D:\Downloads\saskatchewan_glacier_mask.geojson",
            "mask/saskatchewan_glacier_mask.geojson",
            "saskatchewan_glacier_mask.geojson"
        ]
        
        glacier_mask_path = None
        for mask_path in possible_masks:
            if os.path.exists(mask_path):
                glacier_mask_path = mask_path
                break
        
        if not glacier_mask_path:
            print("⚠️  Glacier mask not found - skipping auto-clipping")
            print(f"   Looked for: {possible_masks}")
            return False
        
        print(f"✅ Using glacier mask: {glacier_mask_path}")
        
        # Create clipped output directory
        clipped_dir = self.output_dir.parent / f"{self.output_dir.name}_clipped"
        clipped_dir.mkdir(exist_ok=True)
        
        print(f"📁 Clipped files will be saved to: {clipped_dir}")
        
        success_count = 0
        
        for i, hdf_file in enumerate(hdf_files, 1):
            filename = hdf_file.name
            print(f"\n🔄 Clipping {i}/{len(hdf_files)}: {filename}")
            
            # Get subdatasets
            subdatasets = self.list_hdf_subdatasets(hdf_file)
            
            if not subdatasets:
                print("   ❌ No subdatasets found")
                continue
            
            # Find albedo datasets
            albedo_datasets = [s for s in subdatasets if 'Albedo' in s and ('shortwave' in s or 'WSA' in s)]
            
            if not albedo_datasets:
                albedo_datasets = [s for s in subdatasets if 'Albedo' in s]
            
            if not albedo_datasets:
                print("   ⚠️  No albedo datasets found")
                continue
            
            print(f"   📊 Processing {len(albedo_datasets)} albedo dataset(s)")
            
            for j, dataset in enumerate(albedo_datasets):
                dataset_name = dataset.split(':')[-1] if ':' in dataset else f"dataset_{j}"
                print(f"   📈 Clipping: {dataset_name}")
                
                # Create output filename
                base_name = filename.replace('.hdf', '')
                output_filename = f"{base_name}_{dataset_name}_clipped.tif"
                output_path = clipped_dir / output_filename
                
                # Clip using gdal_warp
                if self.clip_with_gdal_warp(dataset, str(output_path), glacier_mask_path):
                    success_count += 1
        
        print(f"\n🎉 Auto-clipping complete!")
        print(f"   Successfully clipped: {success_count} datasets")
        print(f"   Clipped files location: {clipped_dir}")
        
        # List clipped files
        clipped_files = list(clipped_dir.glob("*.tif"))
        if clipped_files:
            print(f"\n📄 Clipped files ({len(clipped_files)}):")
            total_size = 0
            for clipped_file in clipped_files:
                size_mb = clipped_file.stat().st_size / (1024 * 1024)
                total_size += size_mb
                print(f"   • {clipped_file.name} ({size_mb:.2f} MB)")
            print(f"   Total size: {total_size:.1f} MB")
        
        return success_count > 0

def main():
    """Simple test of MCD43A3 downloader"""
    print("🛰️  MCD43A3 Albedo Downloader")
    print("=" * 40)
    
    # Your credentials
    username = "tofunori"
    password = "ASDqwe1234567890!"
    glacier_mask_path = r"D:\Downloads\saskatchewan_glacier_mask.geojson"
    
    # Create downloader
    downloader = MCD43A3Downloader(username, password, glacier_mask_path)
    
    # Download for a small date range
    start_date = "2024-09-15"
    end_date = "2024-09-18"  # Just 4 days
    
    files = downloader.download_mcd43a3(start_date, end_date, max_files=3)
    
    if files:
        print(f"\n🎉 Success! Downloaded {len(files)} MCD43A3 files")
        print(f"📁 Check folder: {downloader.output_dir}")
        
        # Automatically clip the downloaded files
        clipping_success = downloader.auto_clip_downloaded_files()
        
        if clipping_success:
            print(f"\n✂️  Clipping completed successfully!")
            print(f"📁 Clipped files available in: {downloader.output_dir.parent}/{downloader.output_dir.name}_clipped")
            print(f"🎯 Your data is now precisely clipped to the glacier boundaries!")
        else:
            print(f"\n⚠️  Auto-clipping skipped")
            print(f"💡 You can manually clip using: python alternative_gdal_clipper.py")
            
    else:
        print(f"\n❌ No files downloaded")
        print("💡 Try running debug_granule_details.py for more info")

if __name__ == "__main__":
    main()