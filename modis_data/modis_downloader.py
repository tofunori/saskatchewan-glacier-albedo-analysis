#!/usr/bin/env python3
"""
MODIS Data Downloader for Saskatchewan Glacier Analysis
Download MOD10A1 (snow cover) and MCD43A3 (albedo) data for glacier research
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
    from osgeo import ogr
    SPATIAL_SUPPORT = True
except ImportError:
    SPATIAL_SUPPORT = False

class SaskatchewanGlacierModisDownloader:
    """Download MODIS data for Saskatchewan Glacier analysis"""
    
    def __init__(self, username=None, password=None, glacier_mask_path=None):
        """
        Initialize downloader with NASA Earthdata credentials
        
        Args:
            username: NASA Earthdata username (optional if using .netrc)
            password: NASA Earthdata password (optional if using .netrc)
            glacier_mask_path: Path to glacier mask file (GeoJSON, shapefile, etc.)
        """
        self.username = username
        self.password = password
        self.session = None
        self.glacier_mask_path = glacier_mask_path
        self.glacier_geometry = None
        
        # Saskatchewan Glacier approximate bounding box (lat/lon) - fallback
        # Adjust these coordinates based on your specific study area
        self.saskatchewan_bbox = [-117.3, 52.1, -117.1, 52.3]  # [west, south, east, north]
        
        # Create data directories
        self.data_dir = Path("modis_data")
        self.snow_dir = self.data_dir / "MOD10A1_snow_cover"
        self.albedo_dir = self.data_dir / "MCD43A3_albedo"
        
        self._create_directories()
        self._load_glacier_mask()
    
    def _create_directories(self):
        """Create necessary directories for data storage"""
        self.data_dir.mkdir(exist_ok=True)
        self.snow_dir.mkdir(exist_ok=True)
        self.albedo_dir.mkdir(exist_ok=True)
    
    def _load_glacier_mask(self):
        """Load glacier mask geometry for spatial filtering"""
        if not self.glacier_mask_path:
            print("ℹ️  No glacier mask provided, using bounding box for spatial filtering")
            return
        
        if not SPATIAL_SUPPORT:
            print("⚠️  Spatial libraries not available. Install with: pip install modis-tools[gdal]")
            print("   Falling back to bounding box filtering")
            return
        
        try:
            mask_path = Path(self.glacier_mask_path)
            
            if not mask_path.exists():
                print(f"❌ Glacier mask file not found: {mask_path}")
                print("   Falling back to bounding box filtering")
                return
            
            # Try to load with geopandas first (supports many formats)
            try:
                gdf = gpd.read_file(mask_path)
                
                # Combine all geometries into a single geometry
                if len(gdf) > 1:
                    self.glacier_geometry = gdf.geometry.unary_union
                else:
                    self.glacier_geometry = gdf.geometry.iloc[0]
                
                print(f"✅ Loaded glacier mask from: {mask_path}")
                print(f"   Geometry type: {type(self.glacier_geometry).__name__}")
                print(f"   Bounds: {self.glacier_geometry.bounds}")
                
                return
                
            except Exception as e:
                print(f"⚠️  Could not load with geopandas: {e}")
                
            # Try with GDAL/OGR as fallback
            try:
                ds = ogr.Open(str(mask_path))
                if ds is None:
                    raise Exception("Could not open file with GDAL")
                
                layer = ds.GetLayer()
                feature = layer.GetNextFeature()
                
                if feature:
                    geom = feature.GetGeometryRef()
                    # Convert OGR geometry to shapely
                    wkt = geom.ExportToWkt()
                    self.glacier_geometry = shapely.geometry.loads(wkt)
                    
                    print(f"✅ Loaded glacier mask with GDAL from: {mask_path}")
                    print(f"   Geometry type: {type(self.glacier_geometry).__name__}")
                    print(f"   Bounds: {self.glacier_geometry.bounds}")
                    
                else:
                    raise Exception("No features found in file")
                    
            except Exception as e:
                print(f"❌ Could not load glacier mask: {e}")
                print("   Falling back to bounding box filtering")
                
        except Exception as e:
            print(f"❌ Error loading glacier mask: {e}")
            print("   Falling back to bounding box filtering")
    
    def get_spatial_filter(self):
        """Get the appropriate spatial filter for granule queries"""
        if self.glacier_geometry is not None:
            return {"spatial": self.glacier_geometry}
        else:
            return {"bounding_box": self.saskatchewan_bbox}
    
    def authenticate(self):
        """Authenticate with NASA Earthdata"""
        if self.username and self.password:
            self.session = ModisSession(username=self.username, password=self.password)
        else:
            # Try using .netrc file
            self.session = ModisSession()
        print("✅ Authenticated with NASA Earthdata")
    
    def download_snow_cover_data(self, start_date, end_date, limit=None):
        """
        Download MOD10A1 snow cover data
        
        Args:
            start_date: Start date (YYYY-MM-DD or datetime)
            end_date: End date (YYYY-MM-DD or datetime)
            limit: Maximum number of granules to download
        """
        print(f"🔍 Searching for MOD10A1 snow cover data ({start_date} to {end_date})")
        
        # Query collections
        collection_client = CollectionApi(session=self.session)
        collections = collection_client.query(short_name="MOD10A1", version="061")
        
        if not collections:
            print("❌ No MOD10A1 collections found")
            return []
        
        print(f"✅ Found {len(collections)} MOD10A1 collection(s)")
        
        # Query granules with spatial filtering
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
        print(f"✅ Found {len(granules_list)} MOD10A1 granules")
        
        if granules_list:
            print("📥 Downloading MOD10A1 snow cover data...")
            file_paths = GranuleHandler.download_from_granules(
                granules_list, 
                modis_session=self.session, 
                path=str(self.snow_dir),
                threads=-1  # Use all available cores
            )
            print(f"✅ Downloaded {len(file_paths)} MOD10A1 files to {self.snow_dir}")
            return file_paths
        
        return []
    
    def download_albedo_data(self, start_date, end_date, limit=None):
        """
        Download MCD43A3 albedo data
        
        Args:
            start_date: Start date (YYYY-MM-DD or datetime)
            end_date: End date (YYYY-MM-DD or datetime)
            limit: Maximum number of granules to download
        """
        print(f"🔍 Searching for MCD43A3 albedo data ({start_date} to {end_date})")
        
        # Query collections
        collection_client = CollectionApi(session=self.session)
        collections = collection_client.query(short_name="MCD43A3", version="061")
        
        if not collections:
            print("❌ No MCD43A3 collections found")
            return []
        
        print(f"✅ Found {len(collections)} MCD43A3 collection(s)")
        
        # Query granules with spatial filtering
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
        print(f"✅ Found {len(granules_list)} MCD43A3 granules")
        
        if granules_list:
            print("📥 Downloading MCD43A3 albedo data...")
            file_paths = GranuleHandler.download_from_granules(
                granules_list, 
                modis_session=self.session, 
                path=str(self.albedo_dir),
                threads=-1  # Use all available cores
            )
            print(f"✅ Downloaded {len(file_paths)} MCD43A3 files to {self.albedo_dir}")
            return file_paths
        
        return []
    
    def download_glacier_data(self, start_date, end_date, limit_per_product=None):
        """
        Download both snow cover and albedo data for the glacier
        
        Args:
            start_date: Start date (YYYY-MM-DD or datetime)
            end_date: End date (YYYY-MM-DD or datetime)
            limit_per_product: Maximum granules per product type
        """
        if not self.session:
            self.authenticate()
        
        print(f"🏔️  Downloading MODIS data for Saskatchewan Glacier")
        print(f"📅 Date range: {start_date} to {end_date}")
        
        # Show spatial filtering info
        if self.glacier_geometry is not None:
            print(f"🎯 Using glacier mask for precise spatial filtering")
            print(f"   Geometry bounds: {self.glacier_geometry.bounds}")
        else:
            print(f"📍 Using bounding box: {self.saskatchewan_bbox}")
        
        # Download both products
        snow_files = self.download_snow_cover_data(start_date, end_date, limit_per_product)
        albedo_files = self.download_albedo_data(start_date, end_date, limit_per_product)
        
        print(f"\n📊 Download Summary:")
        print(f"   Snow cover files (MOD10A1): {len(snow_files)}")
        print(f"   Albedo files (MCD43A3): {len(albedo_files)}")
        print(f"   Total files: {len(snow_files) + len(albedo_files)}")
        
        return {
            'snow_cover': snow_files,
            'albedo': albedo_files
        }

def main():
    """Example usage"""
    # Update these with your NASA Earthdata credentials
    # Or set up .netrc file using: add_earthdata_netrc(username, password)
    username = "tofunori"  # Your username
    password = "ASDqwe1234!"  # Add your password here or use .netrc
    
    # Option 1: Use glacier mask for precise spatial filtering
    glacier_mask_path = "mask/saskatchewan_glacier_shapefile.shp"  # Your glacier mask
    downloader = SaskatchewanGlacierModisDownloader(username, password, glacier_mask_path)
    
    # Option 2: Use bounding box (default)
    # downloader = SaskatchewanGlacierModisDownloader(username, password)
    
    # Download data for mid-August 2024 (small test window)
    start_date = "2024-08-01"
    end_date = "2024-08-15"
    
    # Download with limit for testing (remove limit for full download)
    results = downloader.download_glacier_data(
        start_date=start_date,
        end_date=end_date,
        limit_per_product=5  # Remove this line for unlimited download
    )

if __name__ == "__main__":
    main()