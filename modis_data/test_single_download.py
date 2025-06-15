#!/usr/bin/env python3
"""
Test single file download to debug stalling issues
"""

from modis_tools.auth import ModisSession
from modis_tools.resources import CollectionApi, GranuleApi
from modis_tools.granule_handler import GranuleHandler
import time

def test_minimal_download():
    """Test downloading just one small file"""
    print("🧪 Testing minimal download...")
    
    # Authentication
    username = "tofunori"
    password = "ASDqwe1234!"
    session = ModisSession(username=username, password=password)
    print("✅ Authenticated")
    
    # Get collections
    collection_client = CollectionApi(session=session)
    collections = collection_client.query(short_name="MCD43A3", version="061")
    collections_list = list(collections)
    
    if not collections_list:
        print("❌ No collections found")
        return
    
    print(f"✅ Found {len(collections_list)} collections")
    
    # Get just one granule
    granule_client = GranuleApi.from_collection(collections_list[0], session=session)
    
    # Very small query
    granules = granule_client.query(
        start_date="2024-08-01",
        end_date="2024-08-01",  # Single day
        bounding_box=[-117.3, 52.1, -117.1, 52.3],  # Your glacier area
        limit=1  # Just one file
    )
    
    granules_list = list(granules)
    print(f"✅ Found {len(granules_list)} granules")
    
    if granules_list:
        print("📥 Starting download with timeout monitoring...")
        
        start_time = time.time()
        
        try:
            # Download with very conservative settings
            file_paths = GranuleHandler.download_from_granules(
                granules_list,
                modis_session=session,
                path="test_download",
                threads=1,  # Single thread
                ext=("hdf",),  # Only HDF
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ Download completed in {duration:.1f} seconds")
            print(f"   Files downloaded: {len(file_paths)}")
            
            for path in file_paths:
                print(f"   📄 {path}")
                
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            print(f"❌ Download failed after {duration:.1f} seconds")
            print(f"   Error: {e}")
            print(f"   Error type: {type(e).__name__}")

def test_with_timeout():
    """Test download with explicit timeout handling"""
    print("\n⏱️ Testing with timeout handling...")
    
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Download timeout")
    
    # Set 60 second timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60)
    
    try:
        test_minimal_download()
        signal.alarm(0)  # Cancel timeout
    except TimeoutError:
        print("❌ Download timed out after 60 seconds")
        print("💡 Server may be overloaded or network issues")
    except Exception as e:
        signal.alarm(0)
        print(f"❌ Other error: {e}")

if __name__ == "__main__":
    test_minimal_download()
    
    print("\n" + "="*50)
    print("💡 TROUBLESHOOTING TIPS:")
    print("1. If download stalls: NASA servers may be overloaded")
    print("2. Try downloading at different times of day")
    print("3. Use threads=1 to reduce server load")
    print("4. Try smaller date ranges (single day)")
    print("5. Check NASA Earthdata server status online")