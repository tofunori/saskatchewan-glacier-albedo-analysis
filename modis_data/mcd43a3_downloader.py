#!/usr/bin/env python3
"""
Simple MCD43A3 Albedo Data Downloader
Focus only on the working product
"""

import os
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
        
        # Simple directory setup
        self.output_dir = Path("MCD43A3_downloads")
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
    start_date = "2024-08-01"
    end_date = "2024-08-05"  # Just 4 days
    
    files = downloader.download_mcd43a3(start_date, end_date, max_files=3)
    
    if files:
        print(f"\n🎉 Success! Downloaded {len(files)} MCD43A3 files")
        print(f"📁 Check folder: {downloader.output_dir}")
    else:
        print(f"\n❌ No files downloaded")
        print("💡 Try running debug_granule_details.py for more info")

if __name__ == "__main__":
    main()