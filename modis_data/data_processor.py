#!/usr/bin/env python3
"""
MODIS Data Processor for Saskatchewan Glacier Analysis
Process downloaded MCD10A1 and MOD43A3 data for glacier research
"""

import os
import glob
import numpy as np
import pandas as pd
import rasterio
import xarray as xr
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class ModisDataProcessor:
    """Process MODIS data for glacier analysis"""
    
    def __init__(self, data_dir="modis_data"):
        """
        Initialize data processor
        
        Args:
            data_dir: Directory containing MODIS data
        """
        self.data_dir = Path(data_dir)
        self.snow_dir = self.data_dir / "MCD10A1_snow_cover"
        self.albedo_dir = self.data_dir / "MOD43A3_albedo"
        self.output_dir = self.data_dir / "processed"
        
        self.output_dir.mkdir(exist_ok=True)
    
    def list_downloaded_files(self):
        """List all downloaded MODIS files"""
        print("📁 Downloaded MODIS Files:")
        print("=" * 50)
        
        # Snow cover files
        snow_files = list(self.snow_dir.glob("*.hdf"))
        print(f"MCD10A1 Snow Cover Files: {len(snow_files)}")
        for f in snow_files[:5]:  # Show first 5
            print(f"   {f.name}")
        if len(snow_files) > 5:
            print(f"   ... and {len(snow_files) - 5} more")
        
        print()
        
        # Albedo files
        albedo_files = list(self.albedo_dir.glob("*.hdf"))
        print(f"MOD43A3 Albedo Files: {len(albedo_files)}")
        for f in albedo_files[:5]:  # Show first 5
            print(f"   {f.name}")
        if len(albedo_files) > 5:
            print(f"   ... and {len(albedo_files) - 5} more")
        
        return {
            'snow_files': snow_files,
            'albedo_files': albedo_files
        }
    
    def extract_file_metadata(self, file_path):
        """
        Extract metadata from MODIS filename
        
        Args:
            file_path: Path to MODIS file
            
        Returns:
            dict: Extracted metadata
        """
        filename = Path(file_path).name
        
        try:
            # MODIS filename format: PRODUCT.AYYYYDDD.HXXVXX.VVV.YYYYDDDHHMMSS.hdf
            parts = filename.split('.')
            
            product = parts[0]
            date_part = parts[1][1:]  # Remove 'A' prefix
            tile = parts[2]
            version = parts[3]
            
            # Parse date (YYYYDDD format)
            year = int(date_part[:4])
            doy = int(date_part[4:])  # Day of year
            date = datetime.strptime(f"{year}{doy:03d}", "%Y%j")
            
            return {
                'product': product,
                'date': date,
                'tile': tile,
                'version': version,
                'filename': filename,
                'file_path': str(file_path)
            }
        except Exception as e:
            print(f"❌ Error parsing filename {filename}: {e}")
            return None
    
    def create_file_inventory(self):
        """Create inventory of all downloaded files"""
        files = self.list_downloaded_files()
        
        inventory = []
        
        # Process snow cover files
        for file_path in files['snow_files']:
            metadata = self.extract_file_metadata(file_path)
            if metadata:
                metadata['data_type'] = 'snow_cover'
                inventory.append(metadata)
        
        # Process albedo files
        for file_path in files['albedo_files']:
            metadata = self.extract_file_metadata(file_path)
            if metadata:
                metadata['data_type'] = 'albedo'
                inventory.append(metadata)
        
        # Create DataFrame
        df = pd.DataFrame(inventory)
        
        if not df.empty:
            df = df.sort_values('date')
            
            # Save inventory
            inventory_file = self.output_dir / "file_inventory.csv"
            df.to_csv(inventory_file, index=False)
            print(f"📋 File inventory saved to: {inventory_file}")
            
            # Print summary
            print(f"\n📊 Inventory Summary:")
            print(f"   Total files: {len(df)}")
            print(f"   Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
            print(f"   Products: {', '.join(df['product'].unique())}")
            print(f"   Data types: {', '.join(df['data_type'].unique())}")
        
        return df
    
    def plot_data_availability(self, inventory_df=None):
        """
        Plot data availability timeline
        
        Args:
            inventory_df: DataFrame with file inventory (optional)
        """
        if inventory_df is None:
            inventory_df = self.create_file_inventory()
        
        if inventory_df.empty:
            print("❌ No data to plot")
            return
        
        plt.figure(figsize=(12, 6))
        
        # Create timeline plot
        for data_type, color in [('snow_cover', 'blue'), ('albedo', 'red')]:
            subset = inventory_df[inventory_df['data_type'] == data_type]
            if not subset.empty:
                plt.scatter(subset['date'], [data_type] * len(subset), 
                           c=color, alpha=0.7, s=50, label=f"{data_type.replace('_', ' ').title()}")
        
        plt.xlabel('Date')
        plt.ylabel('Data Type')
        plt.title('MODIS Data Availability for Saskatchewan Glacier')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save plot
        plot_file = self.output_dir / "data_availability.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        print(f"📈 Data availability plot saved to: {plot_file}")
        
        plt.show()
    
    def read_modis_hdf_info(self, file_path):
        """
        Read basic information from MODIS HDF file
        
        Args:
            file_path: Path to HDF file
            
        Returns:
            dict: File information
        """
        try:
            with rasterio.open(file_path) as src:
                info = {
                    'filename': Path(file_path).name,
                    'driver': src.driver,
                    'count': src.count,
                    'width': src.width,
                    'height': src.height,
                    'crs': src.crs,
                    'bounds': src.bounds,
                    'subdatasets': src.subdatasets if hasattr(src, 'subdatasets') else None
                }
                return info
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return None
    
    def analyze_sample_files(self, max_files=3):
        """
        Analyze a few sample files to understand data structure
        
        Args:
            max_files: Maximum number of files to analyze per type
        """
        files = self.list_downloaded_files()
        
        print("🔍 Analyzing Sample Files:")
        print("=" * 50)
        
        # Analyze snow cover files
        print("MCD10A1 Snow Cover Files:")
        for i, file_path in enumerate(files['snow_files'][:max_files]):
            info = self.read_modis_hdf_info(file_path)
            if info:
                print(f"   File {i+1}: {info['filename']}")
                print(f"     Dimensions: {info['width']} x {info['height']} pixels")
                print(f"     Bands: {info['count']}")
                print(f"     CRS: {info['crs']}")
                if info['subdatasets']:
                    print(f"     Subdatasets: {len(info['subdatasets'])}")
                print()
        
        # Analyze albedo files
        print("MOD43A3 Albedo Files:")
        for i, file_path in enumerate(files['albedo_files'][:max_files]):
            info = self.read_modis_hdf_info(file_path)
            if info:
                print(f"   File {i+1}: {info['filename']}")
                print(f"     Dimensions: {info['width']} x {info['height']} pixels")
                print(f"     Bands: {info['count']}")
                print(f"     CRS: {info['crs']}")
                if info['subdatasets']:
                    print(f"     Subdatasets: {len(info['subdatasets'])}")
                print()

def main():
    """Example usage"""
    processor = ModisDataProcessor()
    
    # List downloaded files
    files = processor.list_downloaded_files()
    
    if files['snow_files'] or files['albedo_files']:
        # Create inventory
        inventory = processor.create_file_inventory()
        
        # Plot data availability
        processor.plot_data_availability(inventory)
        
        # Analyze sample files
        processor.analyze_sample_files()
    else:
        print("❌ No MODIS files found. Run the downloader first.")

if __name__ == "__main__":
    main()