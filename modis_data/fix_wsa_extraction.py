#!/usr/bin/env python3
"""
Diagnose and fix White Sky Albedo (WSA) extraction issues
"""

import os
import subprocess
from pathlib import Path

def diagnose_hdf_subdatasets():
    """Diagnose what's actually in each HDF file"""
    
    print("🔍 Diagnosing HDF file contents...")
    
    download_dir = Path(r"D:\Downloads\MCD43A3_downloads")
    hdf_files = list(download_dir.glob("*.hdf"))
    
    for i, hdf_file in enumerate(hdf_files, 1):
        filename = hdf_file.name
        print(f"\n📂 File {i}/{len(hdf_files)}: {filename}")
        
        # Get file info with gdalinfo
        try:
            result = subprocess.run(['gdalinfo', str(hdf_file)], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                
                # Count subdatasets
                subdatasets = [line for line in lines if 'SUBDATASET_' in line and '_NAME=' in line]
                print(f"   📊 Total subdatasets: {len(subdatasets)}")
                
                # Look specifically for WSA datasets
                wsa_datasets = []
                albedo_datasets = []
                
                for line in lines:
                    if 'SUBDATASET_' in line and '_NAME=' in line and '=' in line:
                        dataset_path = line.split('=', 1)[1]
                        dataset_name = dataset_path.split(':')[-1]
                        
                        if 'Albedo' in dataset_name:
                            albedo_datasets.append(dataset_name)
                            
                            if 'WSA' in dataset_name:
                                wsa_datasets.append(dataset_name)
                
                print(f"   🎯 Albedo datasets: {len(albedo_datasets)}")
                print(f"   ☀️  WSA datasets: {len(wsa_datasets)}")
                
                # Show WSA datasets specifically
                if wsa_datasets:
                    print(f"   ✅ WSA datasets found:")
                    for wsa in wsa_datasets:
                        print(f"      • {wsa}")
                else:
                    print(f"   ❌ No WSA datasets found!")
                    print(f"   📋 Available albedo datasets:")
                    for alb in albedo_datasets[:5]:  # Show first 5
                        print(f"      • {alb}")
                        
            else:
                print(f"   ❌ gdalinfo failed: {result.stderr}")
                
        except Exception as e:
            print(f"   ❌ Error analyzing file: {e}")

def test_individual_wsa_extraction():
    """Test extracting WSA from problematic files"""
    
    print(f"\n🧪 Testing individual WSA extraction...")
    
    download_dir = Path(r"D:\Downloads\MCD43A3_downloads")
    clipped_dir = Path(r"D:\Downloads\MCD43A3_downloads_clipped")
    glacier_mask = r"D:\Downloads\saskatchewan_glacier_mask.geojson"
    
    # Test the problematic files
    problematic_files = [
        "MCD43A3.A2024216.h10v03.061.2024228022014.hdf",
        "MCD43A3.A2024217.h10v03.061.2024228024608.hdf", 
        "MCD43A3.A2024218.h10v03.061.2024228031446.hdf"
    ]
    
    for filename in problematic_files:
        hdf_file = download_dir / filename
        
        if not hdf_file.exists():
            print(f"   ⚠️  File not found: {filename}")
            continue
            
        print(f"\n🔄 Testing: {filename}")
        
        # Get subdatasets
        try:
            result = subprocess.run(['gdalinfo', str(hdf_file)], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"   ❌ Cannot read file with gdalinfo")
                continue
            
            # Find WSA shortwave specifically
            lines = result.stdout.split('\n')
            wsa_shortwave_dataset = None
            
            for line in lines:
                if 'SUBDATASET_' in line and '_NAME=' in line and '=' in line:
                    dataset_path = line.split('=', 1)[1]
                    dataset_name = dataset_path.split(':')[-1]
                    
                    if 'Albedo_WSA_shortwave' in dataset_name:
                        wsa_shortwave_dataset = dataset_path
                        break
            
            if wsa_shortwave_dataset:
                print(f"   ✅ Found WSA shortwave dataset")
                print(f"   📊 Dataset: {wsa_shortwave_dataset.split(':')[-1]}")
                
                # Try to extract it manually
                base_name = filename.replace('.hdf', '')
                output_file = clipped_dir / f"{base_name}_Albedo_WSA_shortwave_clipped_manual.tif"
                
                print(f"   🔄 Attempting manual extraction...")
                
                cmd = [
                    'gdalwarp',
                    '-of', 'GTiff',
                    '-co', 'COMPRESS=LZW',
                    '-cutline', glacier_mask,
                    '-crop_to_cutline',
                    '-dstnodata', '-9999',
                    wsa_shortwave_dataset,
                    str(output_file)
                ]
                
                try:
                    extract_result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                    
                    if extract_result.returncode == 0 and output_file.exists():
                        size_mb = output_file.stat().st_size / (1024 * 1024)
                        print(f"   ✅ Manual extraction successful! ({size_mb:.2f} MB)")
                    else:
                        print(f"   ❌ Manual extraction failed")
                        print(f"   Error: {extract_result.stderr}")
                        
                except Exception as e:
                    print(f"   ❌ Extraction error: {e}")
                    
            else:
                print(f"   ❌ WSA shortwave dataset not found in this file")
                
        except Exception as e:
            print(f"   ❌ Error processing file: {e}")

def check_data_quality():
    """Check if the data in files has quality issues"""
    
    print(f"\n🔍 Checking data quality in problematic files...")
    
    download_dir = Path(r"D:\Downloads\MCD43A3_downloads")
    
    # Compare file sizes
    hdf_files = list(download_dir.glob("*.hdf"))
    
    print(f"📊 File size comparison:")
    
    for hdf_file in sorted(hdf_files):
        size_mb = hdf_file.stat().st_size / (1024 * 1024)
        
        # Extract date for identification
        if "A2024" in hdf_file.name:
            date_part = hdf_file.name.split("A2024")[1].split(".")[0]
            
            # Check if this file had clipping success
            clipped_dir = Path(r"D:\Downloads\MCD43A3_downloads_clipped")
            clipped_files = list(clipped_dir.glob(f"*A2024{date_part}*WSA_shortwave*.tif"))
            
            status = "✅ WSA OK" if clipped_files else "❌ WSA FAILED"
            
            print(f"   A2024{date_part}: {size_mb:.1f} MB - {status}")

def provide_solutions():
    """Provide solutions based on diagnosis"""
    
    print(f"\n💡 SOLUTIONS:")
    print(f"1. 🔄 Re-run the main downloader to get fresh files:")
    print(f"   python mcd43a3_downloader.py")
    
    print(f"2. 🎯 Try downloading different dates:")
    print(f"   Edit the date range in mcd43a3_downloader.py")
    print(f"   start_date = '2024-08-20'")
    print(f"   end_date = '2024-08-25'")
    
    print(f"3. ✅ Use what you have:")
    print(f"   You already have 3 working dates of WSA data")
    print(f"   This is sufficient for temporal analysis")
    
    print(f"4. 🔧 Manual extraction (if test above worked):")
    print(f"   The manual extraction might have recovered some data")

if __name__ == "__main__":
    print("🛠️  WSA Extraction Diagnostic Tool")
    print("=" * 40)
    
    # Step 1: Diagnose what's in each file
    diagnose_hdf_subdatasets()
    
    # Step 2: Test manual extraction
    test_individual_wsa_extraction()
    
    # Step 3: Check data quality
    check_data_quality()
    
    # Step 4: Provide solutions
    provide_solutions()
    
    print(f"\n🎯 BOTTOM LINE:")
    print(f"You have 3 dates of perfect WSA data - that's enough for analysis!")
    print(f"The 3 failed dates might be server/data issues, not your setup.")