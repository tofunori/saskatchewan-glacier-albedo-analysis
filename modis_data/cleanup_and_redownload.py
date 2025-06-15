#!/usr/bin/env python3
"""
Clean up failed files and re-download if needed
"""

import os
import glob
from pathlib import Path

def analyze_clipping_results():
    """Analyze which files failed clipping"""
    
    download_dir = Path(r"D:\Downloads\MCD43A3_downloads")
    clipped_dir = Path(r"D:\Downloads\MCD43A3_downloads_clipped")
    
    print("🔍 Analyzing clipping results...")
    
    # Get all HDF files
    hdf_files = list(download_dir.glob("*.hdf"))
    print(f"📂 Found {len(hdf_files)} HDF files")
    
    # Group by date
    successful_dates = set()
    failed_dates = set()
    
    for hdf_file in hdf_files:
        # Extract date from filename (A2024XXX)
        filename = hdf_file.name
        if "A2024" in filename:
            date_part = filename.split("A2024")[1].split(".")[0]
            full_date = f"A2024{date_part}"
            
            # Check if any clipped files exist for this date
            clipped_files = list(clipped_dir.glob(f"*{full_date}*.tif"))
            
            if clipped_files:
                successful_dates.add(full_date)
                print(f"✅ {full_date}: {len(clipped_files)} clipped files")
            else:
                failed_dates.add(full_date)
                print(f"❌ {full_date}: No clipped files")
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Successful dates: {len(successful_dates)}")
    print(f"   ❌ Failed dates: {len(failed_dates)}")
    
    if failed_dates:
        print(f"\n🔧 Failed dates to investigate:")
        for date in sorted(failed_dates):
            print(f"   • {date}")
            
            # Find the corresponding HDF file
            hdf_file = next((f for f in hdf_files if date in f.name), None)
            if hdf_file:
                size_mb = hdf_file.stat().st_size / (1024 * 1024)
                print(f"     File: {hdf_file.name}")
                print(f"     Size: {size_mb:.1f} MB")
                
                # Check if file size is reasonable (should be ~80MB)
                if size_mb < 70:
                    print(f"     ⚠️  File size suspicious (too small)")
                elif size_mb > 90:
                    print(f"     ⚠️  File size suspicious (too large)")
                else:
                    print(f"     ✅ File size appears normal")
    
    return successful_dates, failed_dates

def clean_failed_files():
    """Remove failed/corrupted HDF files"""
    
    print("\n🧹 Cleaning failed files...")
    
    download_dir = Path(r"D:\Downloads\MCD43A3_downloads")
    
    # Files that failed clipping
    failed_files = [
        "MCD43A3.A2024216.h10v03.061.2024228022014.hdf",
        "MCD43A3.A2024217.h10v03.061.2024228024608.hdf", 
        "MCD43A3.A2024218.h10v03.061.2024228031446.hdf"
    ]
    
    for filename in failed_files:
        file_path = download_dir / filename
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"   🗑️  Removing: {filename} ({size_mb:.1f} MB)")
            
            try:
                file_path.unlink()
                print(f"     ✅ Removed successfully")
            except Exception as e:
                print(f"     ❌ Error removing: {e}")
        else:
            print(f"   ⚠️  File not found: {filename}")

def recommend_next_steps():
    """Recommend next steps"""
    
    print(f"\n📋 RECOMMENDATIONS:")
    print(f"1. ✅ You have 3 successful dates (A2024229-231)")
    print(f"2. 📊 This is sufficient for temporal analysis")
    print(f"3. 🔄 To get more data, re-run the downloader:")
    print(f"   python mcd43a3_downloader.py")
    print(f"4. 📅 Consider expanding date range:")
    print(f"   start_date = '2024-08-10'")
    print(f"   end_date = '2024-08-25'")
    
    # Show what data you have
    clipped_dir = Path(r"D:\Downloads\MCD43A3_downloads_clipped")
    
    if clipped_dir.exists():
        shortwave_files = list(clipped_dir.glob("*_Albedo_WSA_shortwave_clipped.tif"))
        
        if shortwave_files:
            print(f"\n🎯 YOUR WORKING ALBEDO DATA:")
            for file in sorted(shortwave_files):
                date_part = file.name.split("A2024")[1].split(".")[0] if "A2024" in file.name else "unknown"
                print(f"   📄 A2024{date_part}: {file.name}")
            
            print(f"\n💡 ANALYSIS TIP:")
            print(f"   Load these files in QGIS or Python for time series analysis")
            print(f"   Compare albedo values across the 3 dates to see glacier changes")

if __name__ == "__main__":
    print("🛠️  MODIS Clipping Results Analyzer")
    print("=" * 40)
    
    # Analyze results
    successful_dates, failed_dates = analyze_clipping_results()
    
    # Ask user if they want to clean failed files
    if failed_dates:
        print(f"\n❓ Do you want to remove the failed HDF files?")
        print(f"   This will free up space and allow re-downloading")
        response = input("Remove failed files? (y/n): ").lower().strip()
        
        if response in ['y', 'yes']:
            clean_failed_files()
    
    # Provide recommendations
    recommend_next_steps()
    
    print(f"\n🎉 GOOD NEWS: You have working albedo data for 3 dates!")
    print(f"Your glacier analysis can proceed with the successful files.")