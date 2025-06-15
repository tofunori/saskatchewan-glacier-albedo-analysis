#!/usr/bin/env python3
"""
Fix NASA Earthdata authentication issues
"""

import os
import requests
from pathlib import Path
from modis_tools.auth import ModisSession, add_earthdata_netrc

def test_credentials():
    """Test different authentication methods"""
    print("🔐 Testing NASA Earthdata Authentication")
    print("=" * 50)
    
    username = "tofunori"
    password = "ASDqwe1234567890!"
    
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password)}")
    
    # Test 1: Direct API authentication
    print("\n1️⃣ Testing direct NASA Earthdata login...")
    
    try:
        response = requests.post(
            "https://urs.earthdata.nasa.gov/api/users/tokens",
            auth=(username, password),
            timeout=15
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Direct authentication successful!")
            token_data = response.json()
            print(f"   Token info: {list(token_data.keys())}")
        else:
            print(f"   ❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            
            if response.status_code == 401:
                print("   💡 This suggests username/password is incorrect")
            elif response.status_code == 403:
                print("   💡 Account may be locked or need verification")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Check if account exists
    print("\n2️⃣ Testing account existence...")
    
    try:
        response = requests.get(
            f"https://urs.earthdata.nasa.gov/api/users/{username}",
            auth=(username, password),
            timeout=15
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("   ✅ Account found!")
            print(f"   User ID: {user_data.get('uid', 'Unknown')}")
            print(f"   Email: {user_data.get('email_address', 'Unknown')}")
            print(f"   First Name: {user_data.get('first_name', 'Unknown')}")
        else:
            print(f"   ❌ Account check failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: ModisSession authentication
    print("\n3️⃣ Testing ModisSession authentication...")
    
    try:
        session = ModisSession(username=username, password=password)
        print("   ✅ ModisSession created successfully")
        
        # Test if session can make authenticated requests
        from modis_tools.resources import CollectionApi
        collection_client = CollectionApi(session=session)
        
        collections = collection_client.query(short_name="MCD43A3", version="061", limit=1)
        collections_list = list(collections)
        
        if collections_list:
            print("   ✅ ModisSession can access collections")
        else:
            print("   ⚠️  ModisSession created but can't access collections")
            
    except Exception as e:
        print(f"   ❌ ModisSession failed: {e}")
        print(f"   Error type: {type(e).__name__}")

def setup_netrc():
    """Set up .netrc file for authentication"""
    print("\n4️⃣ Setting up .netrc authentication...")
    
    username = "tofunori"
    password = "ASDqwe1234!"
    
    try:
        # Use modis-tools helper to set up .netrc
        add_earthdata_netrc(username, password)
        print("   ✅ .netrc file created/updated")
        
        # Check .netrc file
        netrc_path = Path.home() / ".netrc"
        if netrc_path.exists():
            print(f"   📁 .netrc location: {netrc_path}")
            
            # Check permissions
            stat = netrc_path.stat()
            perms = oct(stat.st_mode)[-3:]
            print(f"   🔒 Permissions: {perms}")
            
            if perms != "600":
                print("   ⚠️  Fixing .netrc permissions...")
                netrc_path.chmod(0o600)
                print("   ✅ Permissions fixed to 600")
        
        # Test .netrc authentication
        print("\n   Testing .netrc authentication...")
        session = ModisSession()  # No credentials - should use .netrc
        print("   ✅ .netrc authentication successful")
        
        return True
        
    except Exception as e:
        print(f"   ❌ .netrc setup failed: {e}")
        return False

def check_account_status():
    """Check if account needs additional setup"""
    print("\n5️⃣ Checking account status and requirements...")
    
    print("   📋 NASA Earthdata Account Checklist:")
    print("   □ Account created at https://urs.earthdata.nasa.gov/")
    print("   □ Email verified")
    print("   □ Profile completed")
    print("   □ Agreed to data use terms")
    print("   □ Applied for MODIS data access (if required)")
    
    print("\n   💡 Common Issues:")
    print("   1. Account not verified - Check email for verification link")
    print("   2. Password recently changed - Update credentials")
    print("   3. Account suspended - Contact NASA support")
    print("   4. Need data access approval - Some datasets require application")
    
    print("\n   🌐 Useful Links:")
    print("   • Account management: https://urs.earthdata.nasa.gov/profile")
    print("   • Data access applications: https://urs.earthdata.nasa.gov/approve_app")
    print("   • Support: https://disc.gsfc.nasa.gov/earthdata-login")

def test_alternative_credentials():
    """Test if we need to update credentials"""
    print("\n6️⃣ Testing credential variations...")
    
    # In case there are special characters or encoding issues
    username = "tofunori"
    passwords_to_try = [
        "ASDqwe1234!",  # Original
        "ASDqwe1234",   # Without !
        # Add other variations if needed
    ]
    
    for i, password in enumerate(passwords_to_try, 1):
        print(f"\n   Test {i}: Trying password variation...")
        try:
            response = requests.get(
                "https://urs.earthdata.nasa.gov/api/users/tokens",
                auth=(username, password),
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"   ✅ Success with password variation {i}")
                print(f"   Use this password: {'*' * len(password)}")
                return password
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("   ❌ No working password variations found")
    return None

def main():
    """Run all authentication tests"""
    test_credentials()
    
    # Try to fix with .netrc
    netrc_success = setup_netrc()
    
    if not netrc_success:
        # Check account status
        check_account_status()
        
        # Try password variations
        working_password = test_alternative_credentials()
        
        if working_password:
            print(f"\n🎉 Found working credentials!")
            setup_netrc()  # Update .netrc with working credentials
    
    print("\n" + "=" * 50)
    print("📋 NEXT STEPS:")
    print("1. If authentication still fails:")
    print("   • Log into https://urs.earthdata.nasa.gov/profile")
    print("   • Verify your account and complete profile")
    print("   • Check for any pending verifications")
    print("2. Try downloading again with:")
    print("   python mcd43a3_downloader.py")
    print("3. If still failing, you may need to apply for data access")

if __name__ == "__main__":
    main()