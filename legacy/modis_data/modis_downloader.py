#!/usr/bin/env python3
"""
MODIS Data Downloader for Saskatchewan Glacier Analysis
Download MOD10A1 (snow cover) and MCD43A3 (albedo) data for glacier research
"""

import os
import sys
import platform
import subprocess
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

def detect_wsl_environment():
    """
    Detect if running in WSL (Windows Subsystem for Linux)
    Returns: (is_wsl, wsl_version, windows_user)
    """
    is_wsl = False
    wsl_version = None
    windows_user = None
    
    try:
        # Check for WSL-specific environment variables
        if os.environ.get('WSL_DISTRO_NAME'):
            is_wsl = True
            wsl_version = "WSL2" if os.environ.get('WSL_INTEROP') else "WSL1"
        
        # Alternative check: look for WSL in /proc/version
        if not is_wsl and os.path.exists('/proc/version'):
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
                if 'microsoft' in version_info or 'wsl' in version_info:
                    is_wsl = True
                    wsl_version = "WSL2" if 'wsl2' in version_info else "WSL1"
        
        # Try to get Windows username
        if is_wsl:
            try:
                # Get Windows user from environment or path
                wsl_interop = os.environ.get('WSL_INTEROP', '')
                if wsl_interop:
                    # Extract from WSL_INTEROP path
                    parts = wsl_interop.split('/')
                    for part in parts:
                        if part.startswith('temp-'):
                            # Skip temp directories
                            continue
                        if part and part not in ['run', 'WSL', 'temp']:
                            windows_user = part
                            break
                
                # Alternative: try to get from Windows PATH
                if not windows_user:
                    windows_path = os.environ.get('PATH', '')
                    if '/mnt/c/Users/' in windows_path:
                        for path_part in windows_path.split(':'):
                            if '/mnt/c/Users/' in path_part:
                                user_part = path_part.split('/mnt/c/Users/')[1].split('/')[0]
                                if user_part and user_part != 'All Users':
                                    windows_user = user_part
                                    break
            except Exception:
                pass
    
    except Exception:
        pass
    
    return is_wsl, wsl_version, windows_user

def get_optimal_data_directory():
    """
    Get the optimal data directory based on the environment
    Returns the best path for storing MODIS data
    """
    is_wsl, wsl_version, windows_user = detect_wsl_environment()
    script_dir = Path(__file__).parent
    
    if is_wsl:
        # In WSL, prefer to use a path that's easily accessible from Windows
        # but still within the WSL filesystem for performance
        base_dir = script_dir / "modis_data"
        
        # Also create Windows-accessible path info
        wsl_path = base_dir.resolve()
        windows_path = f"\\\\wsl.localhost\\Ubuntu{wsl_path.as_posix()}"
        
        print(f"🔍 WSL Environment Detected:")
        print(f"   Version: {wsl_version}")
        if windows_user:
            print(f"   Windows User: {windows_user}")
        print(f"   WSL Path: {wsl_path}")
        print(f"   Windows Path: {windows_path}")
        
        return base_dir, {"wsl_path": wsl_path, "windows_path": windows_path}
    else:
        # Regular Linux or other Unix-like system
        base_dir = script_dir / "modis_data"
        print(f"🔍 Linux Environment Detected:")
        print(f"   Data Directory: {base_dir.resolve()}")
        
        return base_dir, {"linux_path": base_dir.resolve()}

def print_environment_info():
    """Print information about the current environment"""
    print(f"🖥️  Environment Information:")
    print(f"   Python: {sys.version.split()[0]}")
    print(f"   Platform: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.machine()}")
    
    is_wsl, wsl_version, windows_user = detect_wsl_environment()
    if is_wsl:
        print(f"   WSL: {wsl_version}")
        if windows_user:
            print(f"   Windows User: {windows_user}")
    
    print(f"   Working Directory: {os.getcwd()}")
    print(f"   Script Directory: {Path(__file__).parent.resolve()}")
    print("")

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
        
        # Get optimal data directory based on environment
        self.data_dir, self.path_info = get_optimal_data_directory()
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
            print("⚠️  Spatial libraries not available.")
            print("   Install with: sudo apt install python3-geopandas python3-shapely python3-gdal")
            print("   Or: python3 -m pip install --user geopandas shapely modis-tools")
            print("   Falling back to bounding box filtering")
            return
        
        try:
            # Handle relative paths by making them absolute to the script directory
            mask_path = Path(self.glacier_mask_path)
            if not mask_path.is_absolute():
                script_dir = Path(__file__).parent
                mask_path = script_dir / mask_path
            
            print(f"🔍 Looking for glacier mask at: {mask_path}")
            
            if not mask_path.exists():
                print(f"❌ Glacier mask file not found: {mask_path}")
                print("   Falling back to bounding box filtering")
                return
            
            # Try to load with geopandas first (supports many formats)
            try:
                gdf = gpd.read_file(mask_path)
                
                # Combine all geometries into a single geometry
                if len(gdf) > 1:
                    # Use union_all() to avoid deprecation warning
                    try:
                        self.glacier_geometry = gdf.geometry.union_all()
                    except AttributeError:
                        # Fallback for older geopandas versions
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
        
        # Query collections - try different versions
        collection_client = CollectionApi(session=self.session)
        
        # Try version 061 first, then fallback to version 6
        collections = None
        for version in ["061", "6"]:
            try:
                print(f"   Trying MOD10A1 version {version}...")
                collections = collection_client.query(short_name="MOD10A1", version=version)
                collections_list = list(collections)
                if collections_list:
                    print(f"   ✅ Found collections with version {version}")
                    collections = collections_list
                    break
            except Exception as e:
                print(f"   ⚠️  Version {version} failed: {e}")
                continue
        
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
            print(f"   Using conservative download settings to avoid timeout...")
            file_paths = GranuleHandler.download_from_granules(
                granules_list, 
                modis_session=self.session, 
                path=str(self.snow_dir),
                threads=2,  # Reduced threads to avoid overwhelming server
                ext=("hdf",)  # Only HDF files to reduce download size
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
            print(f"   Using conservative download settings to avoid timeout...")
            file_paths = GranuleHandler.download_from_granules(
                granules_list, 
                modis_session=self.session, 
                path=str(self.albedo_dir),
                threads=2,  # Reduced threads to avoid overwhelming server
                ext=("hdf",)  # Only HDF files to reduce download size
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
    """Main function for MODIS data download"""
    print("🏔️  Saskatchewan Glacier MODIS Data Downloader")
    print("=" * 60)
    
    try:
        # Update these with your NASA Earthdata credentials
        # Or set up .netrc file using: add_earthdata_netrc(username, password)
        username = "tofunori"  # Your username
        password = "ASDqwe1234!"  # Add your password here or use .netrc
        
        # Option 1: Use glacier mask for precise spatial filtering (Windows path)
        glacier_mask_path = r"D:\Downloads\saskatchewan_glacier_mask.geojson"  # Your glacier mask
        
        print("🚀 Initializing MODIS downloader...")
        downloader = SaskatchewanGlacierModisDownloader(username, password, glacier_mask_path)
        
        # Option 2: Use bounding box (default)
        # downloader = SaskatchewanGlacierModisDownloader(username, password)
        
        # Print path information
        print("\n📁 Data Storage Paths:")
        if 'windows_path' in downloader.path_info:
            print(f"   Windows Access: {downloader.path_info['windows_path']}")
        if 'wsl_path' in downloader.path_info:
            print(f"   WSL Path: {downloader.path_info['wsl_path']}")
        if 'linux_path' in downloader.path_info:
            print(f"   Linux Path: {downloader.path_info['linux_path']}")
        print("")
        
        # Download data for mid-August 2024 (small test window)
        start_date = "2024-08-01"
        end_date = "2024-08-15"
        
        print(f"📅 Downloading data for: {start_date} to {end_date}")
        print("⏳ This may take several minutes depending on data availability...")
        print("")
        
        # Download with limit for testing (remove limit for full download)
        results = downloader.download_glacier_data(
            start_date=start_date,
            end_date=end_date,
            limit_per_product=5  # Remove this line for unlimited download
        )
        
        # Final summary
        print(f"\n🎉 Download completed successfully!")
        print(f"📊 Summary:")
        print(f"   Snow cover files: {len(results['snow_cover'])}")
        print(f"   Albedo files: {len(results['albedo'])}")
        print(f"   Total files: {len(results['snow_cover']) + len(results['albedo'])}")
        
        if 'windows_path' in downloader.path_info:
            print(f"\n💡 Access your data from Windows:")
            print(f"   {downloader.path_info['windows_path']}")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️  Download interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Error during download: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        
        # Print more detailed error information
        import traceback
        print(f"\n🔍 Detailed error information:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()