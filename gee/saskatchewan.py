"""
Saskatchewan-specific MODIS data fetcher for Google Earth Engine
"""

import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from .client import GEEClient


class SaskatchewanMODISFetcher:
    """
    Fetch MODIS albedo and snow cover data for Saskatchewan glacier regions
    """
    
    # Saskatchewan approximate bounding box
    SASKATCHEWAN_BOUNDS = {
        'west': -110.0,
        'east': -101.0, 
        'south': 49.0,
        'north': 60.0
    }
    
    # Glacier region of interest (can be refined)
    GLACIER_REGION = {
        'west': -108.0,
        'east': -105.0,
        'south': 51.5,
        'north': 53.0
    }
    
    def __init__(self, gee_client: GEEClient, region: str = 'glacier'):
        """
        Initialize MODIS fetcher
        
        Args:
            gee_client: Authenticated GEE client
            region: 'saskatchewan' or 'glacier' for area of interest
        """
        self.client = gee_client
        self.logger = logging.getLogger(__name__)
        
        if not self.client.is_authenticated():
            raise RuntimeError("GEE client must be authenticated")
        
        self.ee = self.client.get_ee()
        
        # Set region of interest
        if region == 'saskatchewan':
            self.bounds = self.SASKATCHEWAN_BOUNDS
        else:
            self.bounds = self.GLACIER_REGION
        
        self.region_geometry = self.ee.Geometry.Rectangle([
            self.bounds['west'], self.bounds['south'],
            self.bounds['east'], self.bounds['north']
        ])
        
        self.logger.info(f"📍 Initialized for {region} region: {self.bounds}")
    
    def fetch_albedo_data(self, 
                         start_date: str, 
                         end_date: str,
                         max_cloud_cover: int = 20) -> pd.DataFrame:
        """
        Fetch MODIS albedo data (MCD43A3)
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD) 
            max_cloud_cover: Maximum cloud cover percentage
            
        Returns:
            pandas.DataFrame with albedo data
        """
        self.logger.info(f"🛰️ Fetching albedo data: {start_date} to {end_date}")
        
        try:
            # MCD43A3 Collection 6.1 - MODIS/Terra+Aqua BRDF/Albedo
            collection = (self.ee.ImageCollection("MODIS/061/MCD43A3")
                         .filterDate(start_date, end_date)
                         .filterBounds(self.region_geometry))
            
            # Apply cloud masking if available
            if max_cloud_cover < 100:
                collection = collection.filter(
                    self.ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_cloud_cover)
                )
            
            # Select albedo bands
            albedo_bands = [
                'Albedo_WSA_vis',      # White-sky albedo visible
                'Albedo_BSA_vis',      # Black-sky albedo visible  
                'Albedo_WSA_nir',      # White-sky albedo near-infrared
                'Albedo_BSA_nir',      # Black-sky albedo near-infrared
                'Albedo_WSA_shortwave', # White-sky albedo shortwave
                'Albedo_BSA_shortwave'  # Black-sky albedo shortwave
            ]
            
            # Process collection
            def process_image(image):
                """Process individual image"""
                # Scale factor for MCD43A3 is 0.001
                albedo = image.select(albedo_bands).multiply(0.001)
                
                # Add date information
                date = image.date()
                year = date.get('year')
                month = date.get('month') 
                day = date.get('day')
                doy = date.getRelative('day', 'year').add(1)
                
                # Calculate decimal year
                year_start = self.ee.Date.fromYMD(year, 1, 1)
                year_length = self.ee.Date.fromYMD(year.add(1), 1, 1).difference(year_start, 'day')
                decimal_year = year.add(doy.subtract(1).divide(year_length))
                
                return albedo.set({
                    'system:time_start': image.get('system:time_start'),
                    'date': date.format('YYYY-MM-dd'),
                    'year': year,
                    'month': month,
                    'day': day,
                    'doy': doy,
                    'decimal_year': decimal_year
                })
            
            processed_collection = collection.map(process_image)
            
            # Get time series data
            time_series = self._extract_time_series(processed_collection, albedo_bands)
            
            self.logger.info(f"✅ Retrieved {len(time_series)} albedo observations")
            return time_series
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching albedo data: {e}")
            raise
    
    def fetch_snow_cover_data(self,
                             start_date: str,
                             end_date: str) -> pd.DataFrame:
        """
        Fetch MODIS snow cover data (MOD10A1)
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame with snow cover data
        """
        self.logger.info(f"❄️ Fetching snow cover data: {start_date} to {end_date}")
        
        try:
            # MOD10A1 Collection 6.1 - Terra Snow Cover Daily
            collection = (self.ee.ImageCollection("MODIS/061/MOD10A1")
                         .filterDate(start_date, end_date)
                         .filterBounds(self.region_geometry))
            
            # Select snow cover band
            snow_bands = ['NDSI_Snow_Cover', 'Snow_Albedo_Daily_Tile']
            
            def process_snow_image(image):
                """Process snow cover image"""
                # Apply snow cover quality mask
                snow_cover = image.select('NDSI_Snow_Cover')
                snow_albedo = image.select('Snow_Albedo_Daily_Tile').multiply(0.01)  # Scale factor
                
                # Add date information
                date = image.date()
                year = date.get('year')
                month = date.get('month')
                day = date.get('day')
                doy = date.getRelative('day', 'year').add(1)
                
                return image.select(snow_bands).set({
                    'system:time_start': image.get('system:time_start'),
                    'date': date.format('YYYY-MM-dd'),
                    'year': year,
                    'month': month, 
                    'day': day,
                    'doy': doy
                })
            
            processed_collection = collection.map(process_snow_image)
            
            # Get time series data
            time_series = self._extract_time_series(processed_collection, snow_bands)
            
            self.logger.info(f"✅ Retrieved {len(time_series)} snow cover observations")
            return time_series
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching snow cover data: {e}")
            raise
    
    def _extract_time_series(self, 
                           collection, 
                           bands: List[str]) -> pd.DataFrame:
        """
        Extract time series data from image collection
        
        Args:
            collection: GEE ImageCollection
            bands: List of bands to extract
            
        Returns:
            pandas.DataFrame with time series data
        """
        try:
            # Get the size of collection
            size = collection.size()
            collection_list = collection.toList(size)
            
            # Prepare to collect data
            data_rows = []
            
            # Sample the collection (limit to prevent timeout)
            sample_size = self.ee.Number(size).min(1000)  # Limit to 1000 images
            sampled_list = collection_list.slice(0, sample_size)
            
            # Get collection info for iteration
            collection_info = sampled_list.getInfo()
            
            for i, image_info in enumerate(collection_info):
                try:
                    image = self.ee.Image(collection_list.get(i))
                    
                    # Get mean values over region
                    stats = image.select(bands).reduceRegion(
                        reducer=self.ee.Reducer.mean(),
                        geometry=self.region_geometry,
                        scale=500,  # 500m MODIS resolution
                        maxPixels=1e9
                    )
                    
                    # Get image properties
                    props = image.getInfo()['properties']
                    
                    # Combine stats and properties
                    row_data = {
                        'date': props.get('date'),
                        'year': props.get('year'),
                        'month': props.get('month'),
                        'day': props.get('day'),
                        'doy': props.get('doy'),
                        'decimal_year': props.get('decimal_year')
                    }
                    
                    # Add band values
                    stats_info = stats.getInfo()
                    for band in bands:
                        row_data[band] = stats_info.get(band)
                    
                    data_rows.append(row_data)
                    
                    # Progress logging
                    if (i + 1) % 50 == 0:
                        self.logger.info(f"📊 Processed {i + 1}/{len(collection_info)} images")
                        
                except Exception as img_error:
                    self.logger.warning(f"⚠️ Error processing image {i}: {img_error}")
                    continue
            
            # Convert to DataFrame
            df = pd.DataFrame(data_rows)
            
            if not df.empty:
                # Convert date column to datetime
                df['date'] = pd.to_datetime(df['date'])
                # Sort by date
                df = df.sort_values('date').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting time series: {e}")
            raise
    
    def get_region_info(self) -> Dict[str, Any]:
        """
        Get information about the current region
        
        Returns:
            Dict with region information
        """
        return {
            'bounds': self.bounds,
            'area_km2': self._calculate_area(),
            'geometry_type': 'Rectangle',
            'coordinates': [
                [self.bounds['west'], self.bounds['south']],
                [self.bounds['east'], self.bounds['north']]
            ]
        }
    
    def _calculate_area(self) -> float:
        """Calculate approximate area in km²"""
        # Simple calculation for rectangular region
        width_deg = self.bounds['east'] - self.bounds['west']
        height_deg = self.bounds['north'] - self.bounds['south']
        
        # Rough conversion: 1 degree ≈ 111 km at this latitude
        area_km2 = width_deg * height_deg * 111 * 111
        return round(area_km2, 2)