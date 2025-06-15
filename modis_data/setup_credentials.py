#!/usr/bin/env python3
"""
Setup NASA Earthdata credentials for MODIS data download
"""

import getpass
from modis_tools.auth import add_earthdata_netrc, remove_earthdata_netrc

def setup_netrc_credentials():
    """Set up NASA Earthdata credentials in .netrc file"""
    print("🛡️  NASA Earthdata Credentials Setup")
    print("=" * 50)
    print("This will store your credentials in ~/.netrc for automatic authentication")
    print("You need a NASA Earthdata account: https://earthdata.nasa.gov/")
    print()
    
    username = input("Enter your NASA Earthdata username: ")
    password = getpass.getpass("Enter your NASA Earthdata password: ")
    
    try:
        add_earthdata_netrc(username, password)
        print("✅ Credentials saved successfully!")
        print("You can now run the MODIS downloader without entering credentials each time.")
    except Exception as e:
        print(f"❌ Error saving credentials: {e}")

def remove_netrc_credentials():
    """Remove NASA Earthdata credentials from .netrc file"""
    try:
        remove_earthdata_netrc()
        print("✅ NASA Earthdata credentials removed from .netrc")
    except Exception as e:
        print(f"❌ Error removing credentials: {e}")

def main():
    """Main credential setup interface"""
    print("NASA Earthdata Credential Manager")
    print("=" * 40)
    print("1. Set up credentials")
    print("2. Remove credentials")
    print("3. Exit")
    
    choice = input("\nSelect an option (1-3): ").strip()
    
    if choice == "1":
        setup_netrc_credentials()
    elif choice == "2":
        remove_netrc_credentials()
    elif choice == "3":
        print("Goodbye!")
    else:
        print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()