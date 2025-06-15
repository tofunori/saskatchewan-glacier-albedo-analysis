#!/usr/bin/env python3
"""
Quick setup for NASA Earthdata credentials without interactive input
"""

from modis_tools.auth import add_earthdata_netrc

def setup_credentials():
    """Set up credentials using .netrc (modify this script with your credentials)"""
    
    # TODO: Add your credentials here
    username = "tofunori"
    password = "ASDqwe1234!"  # Replace with your actual password
    
    if password == "YOUR_PASSWORD_HERE":
        print("❌ Please edit this script and add your actual password")
        print("   1. Open quick_setup.py")
        print("   2. Replace 'YOUR_PASSWORD_HERE' with your actual password")
        print("   3. Run the script again")
        return False
    
    try:
        add_earthdata_netrc(username, password)
        print("✅ Credentials saved to .netrc file!")
        print("You can now run the downloader without entering credentials.")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    setup_credentials()