#!/usr/bin/env python3
"""
Debug MODIS connection and collection issues
"""

import os
from datetime import datetime
from modis_tools.auth import ModisSession
from modis_tools.resources import CollectionApi, GranuleApi
from modis_tools.granule_handler import GranuleHandler

def test_modis_authentication():
    """Test MODIS authentication"""
    print("🔐 Testing MODIS authentication...")
    
    try:
        # Try with explicit credentials
        username = "tofunori"
        password = "ASDqwe1234!"
        
        session = ModisSession(username=username, password=password)
        print("✅ Authentication successful")
        return session
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return None

def test_collection_queries(session):
    """Test different collection queries"""
    print("\n🔍 Testing collection queries...")
    
    collection_client = CollectionApi(session=session)
    
    # Test different products and versions
    products_to_test = [
        ("MOD10A1", "061"),
        ("MOD10A1", "6"),
        ("MCD43A3", "061"),
        ("MCD43A3", "6"),
        ("MOD09A1", "061"),  # Another product to test connectivity
    ]
    
    for product, version in products_to_test:
        try:
            print(f"  🔍 Searching {product} version {version}...")
            collections = collection_client.query(short_name=product, version=version)
            collections_list = list(collections)
            
            if collections_list:
                print(f"  ✅ Found {len(collections_list)} {product} collections")
                
                # Show collection details
                for i, collection in enumerate(collections_list):
                    print(f"    Collection {i+1}: {collection.get('concept_id', 'Unknown ID')}")
                    print(f"      Title: {collection.get('title', 'No title')}")
                    print(f"      Version: {collection.get('version_id', 'Unknown version')}")
                    
            else:
                print(f"  ❌ No {product} collections found")
                
        except Exception as e:
            print(f"  ❌ Error querying {product}: {e}")
    
    return collections_list if 'collections_list' in locals() else []

def test_granule_query(session, bbox=None):
    """Test granule queries with simplified parameters"""
    print("\n📦 Testing granule queries...")
    
    # Test with MCD43A3 since it worked
    collection_client = CollectionApi(session=session)
    
    try:
        collections = collection_client.query(short_name="MCD43A3", version="061")
        collections_list = list(collections)
        
        if not collections_list:
            print("❌ No MCD43A3 collections found for granule test")
            return
        
        print(f"✅ Using MCD43A3 collection for granule test")
        
        granule_client = GranuleApi.from_collection(collections_list[0], session=session)
        
        # Test simple query without spatial filtering first
        print("  🔍 Testing simple granule query (no spatial filter)...")
        simple_granules = granule_client.query(
            start_date="2024-08-01",
            end_date="2024-08-02",  # Very short date range
            limit=2
        )
        simple_list = list(simple_granules)
        print(f"  ✅ Found {len(simple_list)} granules without spatial filter")
        
        if bbox:
            # Test with bounding box
            print("  🔍 Testing granule query with bounding box...")
            bbox_granules = granule_client.query(
                start_date="2024-08-01",
                end_date="2024-08-02",
                bounding_box=bbox,
                limit=2
            )
            bbox_list = list(bbox_granules)
            print(f"  ✅ Found {len(bbox_list)} granules with bounding box")
        
    except Exception as e:
        print(f"❌ Granule query error: {e}")

def test_download_timeout(session):
    """Test download with timeout settings"""
    print("\n⏱️ Testing download with timeout settings...")
    
    try:
        collection_client = CollectionApi(session=session)
        collections = collection_client.query(short_name="MCD43A3", version="061")
        collections_list = list(collections)
        
        if not collections_list:
            print("❌ No collections for download test")
            return
        
        granule_client = GranuleApi.from_collection(collections_list[0], session=session)
        
        # Get just one small granule
        granules = granule_client.query(
            start_date="2024-08-01",
            end_date="2024-08-01",
            limit=1
        )
        granules_list = list(granules)
        
        if granules_list:
            print(f"  📥 Attempting download of 1 granule...")
            
            # Try download with conservative settings
            file_paths = GranuleHandler.download_from_granules(
                granules_list[:1],  # Just one file
                modis_session=session,
                path="test_download",
                threads=1,  # Single thread to avoid overwhelming
                ext=("hdf",)  # Only HDF files
            )
            
            print(f"  ✅ Successfully downloaded {len(file_paths)} files")
            
            # Show file info
            for path in file_paths:
                if os.path.exists(path):
                    size_mb = os.path.getsize(path) / (1024 * 1024)
                    print(f"    📄 {os.path.basename(path)} ({size_mb:.1f} MB)")
                    
        else:
            print("  ❌ No granules found for download test")
            
    except Exception as e:
        print(f"❌ Download test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        if hasattr(e, 'response'):
            print(f"   HTTP status: {e.response.status_code if hasattr(e.response, 'status_code') else 'Unknown'}")

def test_server_connectivity():
    """Test basic server connectivity"""
    print("\n🌐 Testing server connectivity...")
    
    import requests
    
    urls_to_test = [
        "https://cmr.earthdata.nasa.gov/search/collections",
        "https://urs.earthdata.nasa.gov/",
        "https://ladsweb.modaps.eosdis.nasa.gov/"
    ]
    
    for url in urls_to_test:
        try:
            response = requests.get(url, timeout=10)
            print(f"  ✅ {url}: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {url}: {e}")

def main():
    """Run all diagnostic tests"""
    print("🛠️  MODIS Connection Diagnostic Tool")
    print("=" * 50)
    
    # Test 1: Server connectivity
    test_server_connectivity()
    
    # Test 2: Authentication
    session = test_modis_authentication()
    if not session:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Test 3: Collection queries
    collections = test_collection_queries(session)
    
    # Test 4: Granule queries
    saskatchewan_bbox = [-117.3, 52.1, -117.1, 52.3]
    test_granule_query(session, saskatchewan_bbox)
    
    # Test 5: Download test
    test_download_timeout(session)
    
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC COMPLETE")
    print("\n💡 RECOMMENDATIONS:")
    print("1. If MOD10A1 collections not found: Try version '6' instead of '061'")
    print("2. If downloads stuck: Use threads=1 and smaller date ranges")
    print("3. If timeouts occur: Check NASA server status")
    print("4. If authentication fails: Verify credentials and .netrc file")

if __name__ == "__main__":
    main()