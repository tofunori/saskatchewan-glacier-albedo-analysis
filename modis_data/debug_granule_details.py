#!/usr/bin/env python3
"""
Debug granule details to understand download failures
"""

from modis_tools.auth import ModisSession
from modis_tools.resources import CollectionApi, GranuleApi
from modis_tools.granule_handler import GranuleHandler
import json

def inspect_granule_details():
    """Inspect granule details to understand download issues"""
    print("🔍 Inspecting granule details...")
    
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
    
    # Inspect collection details
    collection = collections_list[0]
    print(f"\n📋 Collection Details:")
    print(f"   Type: {type(collection)}")
    
    # Try different ways to access collection attributes
    if hasattr(collection, '__dict__'):
        attrs = [attr for attr in collection.__dict__.keys() if not attr.startswith('_')]
        print(f"   Attributes: {attrs}")
    
    if hasattr(collection, 'concept_id'):
        print(f"   Concept ID: {collection.concept_id}")
    
    if hasattr(collection, 'short_name'):
        print(f"   Short Name: {collection.short_name}")
        
    if hasattr(collection, 'version_id'):
        print(f"   Version: {collection.version_id}")
    
    # Get granules
    granule_client = GranuleApi.from_collection(collection, session=session)
    
    # Get granules for analysis
    granules = granule_client.query(
        start_date="2024-08-01",
        end_date="2024-08-01",
        bounding_box=[-117.3, 52.1, -117.1, 52.3],
        limit=1
    )
    
    granules_list = list(granules)
    print(f"\n📦 Found {len(granules_list)} granules")
    
    if granules_list:
        granule = granules_list[0]
        print(f"\n📋 Granule Details:")
        print(f"   Type: {type(granule)}")
        
        # Inspect granule attributes
        if hasattr(granule, '__dict__'):
            attrs = [attr for attr in granule.__dict__.keys() if not attr.startswith('_')]
            print(f"   Attributes: {attrs}")
            
        # Try to access common granule properties
        granule_properties = [
            'concept_id', 'granule_ur', 'title', 'producer_granule_id',
            'collection_concept_id', 'data_center', 'day_night_flag',
            'temporal', 'links', 'related_urls'
        ]
        
        for prop in granule_properties:
            if hasattr(granule, prop):
                value = getattr(granule, prop)
                if prop == 'links' and value:
                    print(f"   {prop}: {len(value)} links found")
                    for i, link in enumerate(value[:3]):  # Show first 3 links
                        print(f"     Link {i+1}: {link}")
                elif prop == 'related_urls' and value:
                    print(f"   {prop}: {len(value)} URLs found")
                    for i, url in enumerate(value[:3]):  # Show first 3 URLs
                        print(f"     URL {i+1}: {url}")
                else:
                    print(f"   {prop}: {value}")
        
        # Try to inspect download URLs
        print(f"\n🔗 Investigating download URLs...")
        
        try:
            # Method 1: Direct granule links
            if hasattr(granule, 'links') and granule.links:
                print(f"   Found {len(granule.links)} links in granule")
                for i, link in enumerate(granule.links):
                    print(f"     Link {i+1}: {link}")
                    
                    # Check if link has href
                    if isinstance(link, dict) and 'href' in link:
                        print(f"       -> Download URL: {link['href']}")
            
            # Method 2: Related URLs
            if hasattr(granule, 'related_urls') and granule.related_urls:
                print(f"   Found {len(granule.related_urls)} related URLs")
                for i, url in enumerate(granule.related_urls):
                    print(f"     URL {i+1}: {url}")
                    
        except Exception as e:
            print(f"   ❌ Error accessing URLs: {e}")
        
        # Try manual download inspection
        print(f"\n🛠️ Testing download preparation...")
        
        try:
            import tempfile
            import os
            
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f"   Using temp directory: {temp_dir}")
                
                # Try to see what GranuleHandler does with our granule
                try:
                    print("   Attempting download...")
                    file_paths = GranuleHandler.download_from_granules(
                        [granule],
                        modis_session=session,
                        path=temp_dir,
                        threads=1
                    )
                    print(f"   ✅ Download successful: {file_paths}")
                    
                    # Check file details
                    for path in file_paths:
                        if os.path.exists(path):
                            size = os.path.getsize(path)
                            print(f"     📄 {os.path.basename(path)}: {size} bytes")
                        
                except Exception as download_error:
                    print(f"   ❌ Download error: {download_error}")
                    print(f"   Error type: {type(download_error).__name__}")
                    
                    # More detailed error info
                    if hasattr(download_error, 'args'):
                        print(f"   Error args: {download_error.args}")
                        
        except Exception as e:
            print(f"   ❌ Error in download test: {e}")

def test_different_granule_queries():
    """Test different ways to query granules"""
    print("\n🧪 Testing different granule query methods...")
    
    username = "tofunori"
    password = "ASDqwe1234!"
    session = ModisSession(username=username, password=password)
    
    collection_client = CollectionApi(session=session)
    collections = collection_client.query(short_name="MCD43A3", version="061")
    collections_list = list(collections)
    
    if not collections_list:
        print("❌ No collections for granule tests")
        return
    
    granule_client = GranuleApi.from_collection(collections_list[0], session=session)
    
    # Test different query parameters
    test_queries = [
        {
            "name": "Simple date range",
            "params": {
                "start_date": "2024-08-01",
                "end_date": "2024-08-01",
                "limit": 1
            }
        },
        {
            "name": "With bounding box",
            "params": {
                "start_date": "2024-08-01",
                "end_date": "2024-08-01",
                "bounding_box": [-117.3, 52.1, -117.1, 52.3],
                "limit": 1
            }
        },
        {
            "name": "Larger date range",
            "params": {
                "start_date": "2024-08-01",
                "end_date": "2024-08-05",
                "limit": 2
            }
        }
    ]
    
    for test in test_queries:
        try:
            print(f"  🔍 {test['name']}...")
            granules = granule_client.query(**test['params'])
            granules_list = list(granules)
            print(f"    ✅ Found {len(granules_list)} granules")
            
            if granules_list:
                granule = granules_list[0]
                # Check if granule has download links
                has_links = hasattr(granule, 'links') and granule.links
                has_urls = hasattr(granule, 'related_urls') and granule.related_urls
                print(f"    Links: {has_links}, URLs: {has_urls}")
                
        except Exception as e:
            print(f"    ❌ Query failed: {e}")

if __name__ == "__main__":
    inspect_granule_details()
    test_different_granule_queries()
    
    print("\n" + "="*60)
    print("💡 ANALYSIS SUMMARY:")
    print("1. Check if granules have valid download links/URLs")
    print("2. Verify download URLs are accessible")
    print("3. Look for authentication or permission issues")
    print("4. Check if files exist on NASA servers")