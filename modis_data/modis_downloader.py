#!/usr/bin/env python3
"""
MODIS Data Downloader for Saskatchewan Glacier Analysis
Download MCD10A1 (snow cover) and MOD43A3 (albedo) data for glacier research
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from modis_tools.auth import ModisSession
from modis_tools.resources import CollectionApi, GranuleApi
from modis_tools.granule_handler import GranuleHandler

class SaskatchewanGlacierModisDownloader:
    """Download MODIS data for Saskatchewan Glacier analysis"""
    
    def __init__(self, username=None, password=None):
        """
        Initialize downloader with NASA Earthdata credentials
        
        Args:
            username: NASA Earthdata username (optional if using .netrc)
            password: NASA Earthdata password (optional if using .netrc)
        """
        self.username = username
        self.password = password
        self.session = None
        
        # Saskatchewan Glacier approximate bounding box (lat/lon)
        # Adjust these coordinates based on your specific study area
        self.saskatchewan_bbox = [-117.3, 52.1, -117.1, 52.3]  # [west, south, east, north]
        
        # Create data directories
        self.data_dir = Path("modis_data")
        self.snow_dir = self.data_dir / "MCD10A1_snow_cover"
        self.albedo_dir = self.data_dir / "MOD43A3_albedo"
        
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories for data storage"""
        self.data_dir.mkdir(exist_ok=True)
        self.snow_dir.mkdir(exist_ok=True)
        self.albedo_dir.mkdir(exist_ok=True)
    
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
        Download MCD10A1 snow cover data
        
        Args:
            start_date: Start date (YYYY-MM-DD or datetime)
            end_date: End date (YYYY-MM-DD or datetime)
            limit: Maximum number of granules to download
        """
        print(f"🔍 Searching for MCD10A1 snow cover data ({start_date} to {end_date})")
        
        # Query collections
        collection_client = CollectionApi(session=self.session)
        collections = collection_client.query(short_name="MCD10A1", version="061")
        
        if not collections:
            print("❌ No MCD10A1 collections found")
            return []
        
        print(f"✅ Found {len(collections)} MCD10A1 collection(s)")
        
        # Query granules
        granule_client = GranuleApi.from_collection(collections[0], session=self.session)
        granules = granule_client.query(
            start_date=start_date,
            end_date=end_date,
            bounding_box=self.saskatchewan_bbox,
            limit=limit
        )
        
        granules_list = list(granules)
        print(f"✅ Found {len(granules_list)} MCD10A1 granules")
        
        if granules_list:
            print("📥 Downloading MCD10A1 snow cover data...")
            file_paths = GranuleHandler.download_from_granules(
                granules_list, 
                session=self.session, 
                path=str(self.snow_dir),
                threads=-1  # Use all available cores
            )
            print(f"✅ Downloaded {len(file_paths)} MCD10A1 files to {self.snow_dir}")
            return file_paths
        
        return []
    
    def download_albedo_data(self, start_date, end_date, limit=None):
        """
        Download MOD43A3 albedo data
        
        Args:
            start_date: Start date (YYYY-MM-DD or datetime)
            end_date: End date (YYYY-MM-DD or datetime)
            limit: Maximum number of granules to download
        """
        print(f"🔍 Searching for MOD43A3 albedo data ({start_date} to {end_date})")
        
        # Query collections
        collection_client = CollectionApi(session=self.session)
        collections = collection_client.query(short_name="MOD43A3", version="061")
        
        if not collections:
            print("❌ No MOD43A3 collections found")
            return []
        
        print(f"✅ Found {len(collections)} MOD43A3 collection(s)")
        
        # Query granules
        granule_client = GranuleApi.from_collection(collections[0], session=self.session)
        granules = granule_client.query(
            start_date=start_date,
            end_date=end_date,
            bounding_box=self.saskatchewan_bbox,
            limit=limit
        )
        
        granules_list = list(granules)
        print(f"✅ Found {len(granules_list)} MOD43A3 granules")
        
        if granules_list:
            print("📥 Downloading MOD43A3 albedo data...")
            file_paths = GranuleHandler.download_from_granules(
                granules_list, 
                session=self.session, 
                path=str(self.albedo_dir),
                threads=-1  # Use all available cores
            )
            print(f"✅ Downloaded {len(file_paths)} MOD43A3 files to {self.albedo_dir}")
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
        print(f"📍 Bounding box: {self.saskatchewan_bbox}")
        
        # Download both products
        snow_files = self.download_snow_cover_data(start_date, end_date, limit_per_product)
        albedo_files = self.download_albedo_data(start_date, end_date, limit_per_product)
        
        print(f"\n📊 Download Summary:")
        print(f"   Snow cover files (MCD10A1): {len(snow_files)}")
        print(f"   Albedo files (MOD43A3): {len(albedo_files)}")
        print(f"   Total files: {len(snow_files) + len(albedo_files)}")
        
        return {
            'snow_cover': snow_files,
            'albedo': albedo_files
        }

def main():
    """Example usage"""
    # Update these with your NASA Earthdata credentials
    # Or set up .netrc file using: add_earthdata_netrc(username, password)
    username = ""  # Update this
    password = ""  # Update this
    
    downloader = SaskatchewanGlacierModisDownloader(username, password)
    
    # Download data for summer 2023 (adjust dates as needed)
    start_date = "2023-06-01"
    end_date = "2023-09-30"
    
    # Download with limit for testing (remove limit for full download)
    results = downloader.download_glacier_data(
        start_date=start_date,
        end_date=end_date,
        limit_per_product=5  # Remove this line for unlimited download
    )

if __name__ == "__main__":
    main()