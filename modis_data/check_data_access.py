#!/usr/bin/env python3
"""
Check and configure NASA Earthdata application access
"""

import requests
import webbrowser
from modis_tools.auth import ModisSession

def check_approved_applications():
    """Check what applications are approved for data access"""
    print("🔍 Checking approved applications...")
    
    username = "tofunori"
    password = "ASDqwe1234!"
    
    try:
        # Check approved applications
        response = requests.get(
            "https://urs.earthdata.nasa.gov/api/users/user/approved_applications",
            auth=(username, password),
            timeout=15
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                apps = response.json()
                print(f"   ✅ Found {len(apps)} approved applications:")
                
                for app in apps:
                    name = app.get('name', 'Unknown')
                    client_id = app.get('client_id', 'Unknown')
                    print(f"     • {name} (ID: {client_id})")
                
                # Check if MODIS-related applications are approved
                modis_apps = [app for app in apps if 'modis' in app.get('name', '').lower() or 'earthdata' in app.get('name', '').lower()]
                
                if modis_apps:
                    print(f"   ✅ Found {len(modis_apps)} MODIS-related applications")
                else:
                    print("   ⚠️  No MODIS-related applications found")
                    print("   💡 You may need to approve data access applications")
                
                return apps
                
            except Exception as e:
                print(f"   ❌ JSON parsing error: {e}")
                print(f"   Raw response: {response.text[:200]}")
        else:
            print(f"   ❌ Failed to get applications: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return []

def check_pending_applications():
    """Check for pending application approvals"""
    print("\n🔄 Checking pending applications...")
    
    username = "tofunori"
    password = "ASDqwe1234!"
    
    try:
        response = requests.get(
            "https://urs.earthdata.nasa.gov/api/users/user/pending_applications",
            auth=(username, password),
            timeout=15
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                pending = response.json()
                print(f"   📋 Found {len(pending)} pending applications")
                
                for app in pending:
                    name = app.get('name', 'Unknown')
                    print(f"     • {name} (needs approval)")
                
                if pending:
                    print("   💡 You have pending applications that need approval")
                    return True
                else:
                    print("   ✅ No pending applications")
                    return False
                    
            except Exception as e:
                print(f"   ❌ JSON parsing error: {e}")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return False

def test_specific_data_access():
    """Test access to specific NASA data services"""
    print("\n🛰️ Testing specific data service access...")
    
    username = "tofunori"
    password = "ASDqwe1234!"
    
    # Test different NASA data endpoints
    test_endpoints = [
        {
            "name": "CMR Collections",
            "url": "https://cmr.earthdata.nasa.gov/search/collections.json?short_name=MCD43A3",
            "auth_required": False
        },
        {
            "name": "CMR Granules", 
            "url": "https://cmr.earthdata.nasa.gov/search/granules.json?short_name=MCD43A3&page_size=1",
            "auth_required": False
        },
        {
            "name": "LAADS DAAC",
            "url": "https://ladsweb.modaps.eosdis.nasa.gov/archive/orders.json",
            "auth_required": True
        }
    ]
    
    for endpoint in test_endpoints:
        print(f"\n   🔍 Testing {endpoint['name']}...")
        
        try:
            if endpoint['auth_required']:
                response = requests.get(endpoint['url'], auth=(username, password), timeout=15)
            else:
                response = requests.get(endpoint['url'], timeout=15)
            
            print(f"     Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"     ✅ Access successful")
                
                # Try to parse response
                try:
                    data = response.json()
                    if 'feed' in data and 'entry' in data['feed']:
                        entries = data['feed']['entry']
                        print(f"     📦 Found {len(entries)} entries")
                    elif isinstance(data, list):
                        print(f"     📦 Found {len(data)} items")
                    else:
                        print(f"     📋 Response type: {type(data)}")
                except:
                    print(f"     📄 Non-JSON response ({len(response.text)} chars)")
                    
            elif response.status_code == 401:
                print(f"     ❌ Authentication required")
            elif response.status_code == 403:
                print(f"     ❌ Access forbidden - may need application approval")
            else:
                print(f"     ⚠️  Status: {response.status_code}")
                
        except Exception as e:
            print(f"     ❌ Error: {e}")

def guide_application_approval():
    """Guide user through application approval process"""
    print("\n📋 Application Approval Guide")
    print("=" * 40)
    
    print("🎯 Based on the diagnostic, you need to approve data access applications.")
    print("\n📝 Steps to approve applications:")
    
    print("\n1️⃣ Visit NASA Earthdata Applications:")
    print("   https://urs.earthdata.nasa.gov/approve_app")
    
    print("\n2️⃣ Look for these applications to approve:")
    applications_to_approve = [
        "NASA GESDISC DATA ARCHIVE",
        "LAADS DAAC",
        "LP DAAC",
        "MODIS Atmosphere Science Data Applications",
        "Earthdata Login"
    ]
    
    for app in applications_to_approve:
        print(f"   □ {app}")
    
    print("\n3️⃣ For each application:")
    print("   • Click 'Approve More Applications'")
    print("   • Search for the application name")
    print("   • Click 'Approve' for MODIS/Land data applications")
    
    print("\n4️⃣ After approval:")
    print("   • Wait 5-10 minutes for changes to take effect")
    print("   • Try downloading again")
    
    print("\n💡 Alternative - Open approval page now?")
    answer = input("Open https://urs.earthdata.nasa.gov/approve_app in browser? (y/n): ")
    
    if answer.lower() in ['y', 'yes']:
        try:
            webbrowser.open("https://urs.earthdata.nasa.gov/approve_app")
            print("✅ Opened approval page in browser")
        except:
            print("❌ Could not open browser - visit URL manually")

def test_after_approval():
    """Test download after application approval"""
    print("\n🧪 Testing download after approval...")
    
    try:
        from modis_tools.auth import ModisSession
        from modis_tools.resources import CollectionApi
        
        session = ModisSession()  # Use .netrc
        collection_client = CollectionApi(session=session)
        
        print("   🔍 Testing collection access...")
        collections = collection_client.query(short_name="MCD43A3", version="061", limit=1)
        collections_list = list(collections)
        
        if collections_list:
            print("   ✅ Collection access successful!")
            print("   🎉 Try running your downloader again:")
            print("      python mcd43a3_downloader.py")
            return True
        else:
            print("   ❌ Still no collection access")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def main():
    """Main diagnostic and fix process"""
    print("🔧 NASA Earthdata Data Access Diagnostic")
    print("=" * 50)
    
    # Check current application status
    approved_apps = check_approved_applications()
    has_pending = check_pending_applications()
    
    # Test data service access
    test_specific_data_access()
    
    # Guide through approval if needed
    if len(approved_apps) < 3:  # Arbitrary threshold
        print("\n🚨 DIAGNOSIS: You need to approve more data access applications")
        guide_application_approval()
        
        print("\n⏳ After completing approvals, test again:")
        print("   python check_data_access.py")
        
    else:
        print("\n✅ You have sufficient application approvals")
        test_success = test_after_approval()
        
        if not test_success:
            print("\n💡 If still failing, try:")
            print("   1. Wait 10-15 minutes after approval")
            print("   2. Clear browser cache and re-login") 
            print("   3. Contact NASA Earthdata support")

if __name__ == "__main__":
    main()