#!/usr/bin/env python3
"""
Test manual download approach to bypass modis-tools
"""

import requests
from modis_tools.auth import ModisSession
from modis_tools.resources import CollectionApi, GranuleApi

def test_manual_download():
    """Test manual download approach"""
    print("🔧 Testing manual download...")
    
    # Authentication
    username = "tofunori"
    password = "ASDqwe1234!"
    session = ModisSession(username=username, password=password)
    print("✅ Authenticated")
    
    # Get collections and granules
    collection_client = CollectionApi(session=session)
    collections = collection_client.query(short_name="MCD43A3", version="061")
    collections_list = list(collections)
    
    granule_client = GranuleApi.from_collection(collections_list[0], session=session)
    granules = granule_client.query(
        start_date="2024-08-01",
        end_date="2024-08-01",
        bounding_box=[-117.3, 52.1, -117.1, 52.3],
        limit=1
    )
    granules_list = list(granules)
    
    if not granules_list:
        print("❌ No granules found")
        return
    
    granule = granules_list[0]
    print(f"🔍 Analyzing granule...")
    
    # Try to extract download URLs manually
    download_urls = []
    
    # Check different attributes for URLs
    url_attributes = ['links', 'related_urls', 'online_access_urls']
    
    for attr in url_attributes:
        if hasattr(granule, attr):
            urls = getattr(granule, attr)
            if urls:
                print(f"   Found {attr}: {len(urls)} URLs")
                for i, url in enumerate(urls[:3]):  # Show first 3
                    print(f"     {i+1}: {url}")
                    if isinstance(url, dict) and 'href' in url:
                        download_urls.append(url['href'])
                    elif isinstance(url, str):
                        download_urls.append(url)
    
    # Test direct download
    if download_urls:
        print(f"\n📥 Testing direct download of first URL...")
        test_url = download_urls[0]
        print(f"   URL: {test_url}")
        
        try:
            # Get session for authenticated download
            auth_session = session.session  # Get the requests session
            
            response = auth_session.head(test_url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                content_length = response.headers.get('content-length')
                if content_length:
                    size_mb = int(content_length) / (1024 * 1024)
                    print(f"   File size: {size_mb:.1f} MB")
                
                # Try partial download
                print("   Testing partial download...")
                response = auth_session.get(test_url, stream=True, timeout=30)
                
                if response.status_code == 200:
                    # Download first chunk
                    chunk = next(iter(response.iter_content(chunk_size=1024)))
                    if chunk:
                        print(f"   ✅ Successfully downloaded {len(chunk)} bytes")
                        print(f"   Content type: {response.headers.get('content-type', 'Unknown')}")
                        return True
                    else:
                        print("   ❌ No content in response")
                else:
                    print(f"   ❌ Download failed: {response.status_code}")
            else:
                print(f"   ❌ File not accessible: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Download error: {e}")
    else:
        print("❌ No download URLs found in granule")
    
    return False

def test_earthdata_login():
    """Test if we can access NASA Earthdata login"""
    print("\n🔐 Testing NASA Earthdata access...")
    
    try:
        # Test basic authentication
        response = requests.get(
            "https://urs.earthdata.nasa.gov/api/users/find_or_create_token",
            auth=("tofunori", "ASDqwe1234!"),
            timeout=10
        )
        
        print(f"   Login test: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Authentication successful")
            return True
        else:
            print(f"   ❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
    
    return False

if __name__ == "__main__":
    print("🛠️  Manual Download Test")
    print("=" * 40)
    
    # Test authentication first
    auth_ok = test_earthdata_login()
    
    if auth_ok:
        # Test manual download
        download_ok = test_manual_download()
        
        if download_ok:
            print("\n✅ Manual download works - issue is with modis-tools")
        else:
            print("\n❌ Manual download also fails - deeper issue")
    
    print("\n💡 RECOMMENDATIONS:")
    print("1. Check NASA Earthdata server status")
    print("2. Verify account has data access permissions")
    print("3. Try different time of day (servers less busy)")
    print("4. Check if specific data access approval needed")