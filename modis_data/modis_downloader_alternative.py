#!/usr/bin/env python3
"""
Alternative MODIS Data Downloader with different products and approaches
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from modis_tools.auth import ModisSession
from modis_tools.resources import CollectionApi, GranuleApi
from modis_tools.granule_handler import GranuleHandler

# Optional spatial processing imports
try:
    import geopandas as gpd
    import shapely.geometry
    SPATIAL_SUPPORT = True
except ImportError:
    SPATIAL_SUPPORT = False

class AlternativeModisDownloader:
    """Alternative MODIS downloader with working products"""
    
    def __init__(self, username=None, password=None, glacier_mask_path=None):
        self.username = username
        self.password = password
        self.session = None
        self.glacier_mask_path = glacier_mask_path
        self.glacier_geometry = None
        
        # Saskatchewan Glacier bounding box
        self.saskatchewan_bbox = [-117.3, 52.1, -117.1, 52.3]
        
        # Set up directories
        self.data_dir = Path("modis_data_alternative")
        self.snow_dir = self.data_dir / "MOD10A2_snow_8day"  # 8-day instead of daily
        self.albedo_dir = self.data_dir / "MCD43A3_albedo"
        self.surface_dir = self.data_dir / "MOD09A1_surface"  # Alternative product
        
        self._create_directories()
        self._load_glacier_mask()
    
    def _create_directories(self):
        """Create directories"""
        self.data_dir.mkdir(exist_ok=True)
        self.snow_dir.mkdir(exist_ok=True)
        self.albedo_dir.mkdir(exist_ok=True)
        self.surface_dir.mkdir(exist_ok=True)
        print(f"📁 Data directories created")
    
    def _load_glacier_mask(self):
        """Load glacier mask - simplified version"""
        if not self.glacier_mask_path or not SPATIAL_SUPPORT:
            print("ℹ️  Using bounding box filtering")
            return
        
        try:
            mask_path = Path(self.glacier_mask_path)
            if mask_path.exists():
                gdf = gpd.read_file(mask_path)
                
                if len(gdf) > 1:
                    try:
                        self.glacier_geometry = gdf.geometry.union_all()
                    except AttributeError:
                        self.glacier_geometry = gdf.geometry.unary_union
                else:
                    self.glacier_geometry = gdf.geometry.iloc[0]
                
                print(f"✅ Loaded glacier mask: {mask_path}")
                
        except Exception as e:
            print(f"⚠️  Could not load mask: {e}")
    
    def authenticate(self):
        """Authenticate"""
        if self.username and self.password:
            self.session = ModisSession(username=self.username, password=self.password)
        else:
            self.session = ModisSession()
        print("✅ Authenticated")
    
    def get_spatial_filter(self):
        """Get spatial filter"""
        if self.glacier_geometry is not None:
            return {"spatial": self.glacier_geometry}
        else:
            return {"bounding_box": self.saskatchewan_bbox}
    
    def test_available_products(self):
        """Test which products are actually available"""
        print("🔍 Testing available MODIS products...")
        
        if not self.session:
            self.authenticate()
        
        collection_client = CollectionApi(session=self.session)
        
        # Test products that might work
        test_products = [
            ("MOD10A2", "061", "8-day Snow Cover"),
            ("MOD10A2", "6", "8-day Snow Cover v6"),
            ("MCD43A3", "061", "Daily Albedo"),
            ("MOD09A1", "061", "8-day Surface Reflectance"),
            ("MOD11A1", "061", "Daily Land Surface Temperature"),
            ("MCD43A1", "061", "Daily BRDF/Albedo"),
        ]
        
        available_products = []
        
        for short_name, version, description in test_products:
            try:
                collections = collection_client.query(short_name=short_name, version=version)
                collections_list = list(collections)
                
                if collections_list:
                    print(f"  ✅ {short_name} v{version}: {description}")
                    available_products.append((short_name, version, description))
                    
                    # Test granule availability
                    try:
                        granule_client = GranuleApi.from_collection(collections_list[0], session=self.session)
                        spatial_filter = self.get_spatial_filter()
                        
                        granules = granule_client.query(
                            start_date="2024-08-01",
                            end_date="2024-08-02",
                            limit=1,
                            **spatial_filter
                        )
                        granules_list = list(granules)
                        print(f"     📦 {len(granules_list)} granules available")
                        
                    except Exception as e:
                        print(f"     ⚠️  Granule query failed: {e}")
                else:
                    print(f"  ❌ {short_name} v{version}: Not available")
                    
            except Exception as e:
                print(f"  ❌ {short_name} v{version}: Error - {e}")
        
        return available_products
    
    def download_alternative_snow_data(self, start_date, end_date, limit=None):
        """Download MOD10A2 (8-day snow cover) instead of daily"""
        print(f"🔍 Downloading MOD10A2 8-day snow cover data...")
        
        collection_client = CollectionApi(session=self.session)
        
        # Try MOD10A2 (8-day composites)
        collections = None
        for version in ["061", "6"]:
            try:
                collections = collection_client.query(short_name="MOD10A2", version=version)
                collections_list = list(collections)
                if collections_list:
                    collections = collections_list
                    print(f"✅ Using MOD10A2 version {version}")
                    break
            except:
                continue
        
        if not collections:
            print("❌ No MOD10A2 collections found")
            return []
        
        # Query granules
        granule_client = GranuleApi.from_collection(collections[0], session=self.session)
        spatial_filter = self.get_spatial_filter()
        
        query_params = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit
        }
        query_params.update(spatial_filter)
        
        granules = granule_client.query(**query_params)
        granules_list = list(granules)
        print(f"✅ Found {len(granules_list)} MOD10A2 granules")
        
        if granules_list:
            print("📥 Downloading MOD10A2 data...")
            try:
                file_paths = GranuleHandler.download_from_granules(
                    granules_list, 
                    modis_session=self.session, 
                    path=str(self.snow_dir),
                    threads=1,  # Very conservative
                    ext=("hdf",)
                )
                print(f"✅ Downloaded {len(file_paths)} files")
                return file_paths
            except Exception as e:
                print(f"❌ Download failed: {e}")
                
                # Try even more conservative approach
                print("🔄 Retrying with single file...")
                try:
                    file_paths = GranuleHandler.download_from_granules(
                        granules_list[:1],  # Just one file
                        modis_session=self.session,
                        path=str(self.snow_dir),
                        threads=1
                    )
                    print(f"✅ Downloaded {len(file_paths)} files (reduced)")
                    return file_paths
                except Exception as e2:
                    print(f"❌ Retry also failed: {e2}")
        
        return []
    
    def download_surface_reflectance(self, start_date, end_date, limit=None):
        """Download MOD09A1 surface reflectance as alternative"""
        print(f"🔍 Downloading MOD09A1 surface reflectance data...")
        
        collection_client = CollectionApi(session=self.session)
        collections = collection_client.query(short_name="MOD09A1", version="061")
        collections_list = list(collections)
        
        if not collections_list:
            print("❌ No MOD09A1 collections found")
            return []
        
        print(f"✅ Found MOD09A1 collections")
        
        # Query granules
        granule_client = GranuleApi.from_collection(collections_list[0], session=self.session)
        spatial_filter = self.get_spatial_filter()
        
        query_params = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit
        }
        query_params.update(spatial_filter)
        
        granules = granule_client.query(**query_params)
        granules_list = list(granules)
        print(f"✅ Found {len(granules_list)} MOD09A1 granules")
        
        if granules_list:
            print("📥 Downloading MOD09A1 data...")
            try:
                file_paths = GranuleHandler.download_from_granules(
                    granules_list[:2],  # Limit to 2 files
                    modis_session=self.session,
                    path=str(self.surface_dir),
                    threads=1,
                    ext=("hdf",)
                )
                print(f"✅ Downloaded {len(file_paths)} files")
                return file_paths
            except Exception as e:
                print(f"❌ Download failed: {e}")
        
        return []
    
    def run_alternative_download(self, start_date, end_date):
        """Run alternative download strategy"""
        if not self.session:
            self.authenticate()
        
        print(f"🏔️  Alternative MODIS Download for Saskatchewan Glacier")
        print(f"📅 Date range: {start_date} to {end_date}")
        
        # Test what's available first
        available = self.test_available_products()
        
        results = {}
        
        # Try alternative snow data (8-day instead of daily)
        snow_files = self.download_alternative_snow_data(start_date, end_date, limit=3)
        results['snow_8day'] = snow_files
        
        # Try surface reflectance as alternative
        surface_files = self.download_surface_reflectance(start_date, end_date, limit=2)
        results['surface_reflectance'] = surface_files
        
        # Still try albedo (this seemed to work in diagnostics)
        # albedo_files = self.download_albedo_data(start_date, end_date, limit=2)
        # results['albedo'] = albedo_files
        
        print(f"\n📊 Download Summary:")
        for product, files in results.items():
            print(f"   {product}: {len(files)} files")
        
        total_files = sum(len(files) for files in results.values())
        print(f"   Total: {total_files} files")
        
        if total_files > 0:
            print(f"\n🎉 Success! Files saved to: {self.data_dir}")
        else:
            print(f"\n❌ No files downloaded successfully")
            print("💡 Try running debug_granule_details.py for more diagnostics")
        
        return results

def main():
    """Test alternative approach"""
    print("🔄 Alternative MODIS Downloader")
    print("=" * 50)
    
    username = "tofunori"
    password = "ASDqwe1234!"
    glacier_mask_path = r"D:\Downloads\saskatchewan_glacier_mask.geojson"
    
    downloader = AlternativeModisDownloader(username, password, glacier_mask_path)
    
    # Try smaller date range
    results = downloader.run_alternative_download("2024-08-01", "2024-08-05")

if __name__ == "__main__":
    main()