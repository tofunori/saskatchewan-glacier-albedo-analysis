#!/usr/bin/env python3
"""
Find actual NASA Earthdata applications available for approval
"""

import requests
import re
from bs4 import BeautifulSoup

def find_available_applications():
    """Scrape the approval page to find actual application names"""
    print("🔍 Finding available applications...")
    
    username = "tofunori"
    password = "ASDqwe1234!"
    
    try:
        # Create session for web scraping
        session = requests.Session()
        
        # First, login to get cookies
        login_url = "https://urs.earthdata.nasa.gov/login"
        response = session.get(login_url, timeout=15)
        
        if response.status_code == 200:
            print("   ✅ Accessed login page")
            
            # Parse login form to get CSRF token
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = None
            
            # Look for CSRF token in various places
            csrf_input = soup.find('input', {'name': 'authenticity_token'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
                print(f"   🔐 Found CSRF token")
            
            # Prepare login data
            login_data = {
                'username': username,
                'password': password,
            }
            
            if csrf_token:
                login_data['authenticity_token'] = csrf_token
            
            # Submit login
            login_response = session.post(
                "https://urs.earthdata.nasa.gov/login",
                data=login_data,
                timeout=15,
                allow_redirects=True
            )
            
            if login_response.status_code == 200 and 'profile' in login_response.url:
                print("   ✅ Login successful")
                
                # Now access the approve applications page
                approve_url = "https://urs.earthdata.nasa.gov/approve_app"
                approve_response = session.get(approve_url, timeout=15)
                
                if approve_response.status_code == 200:
                    print("   ✅ Accessed approve applications page")
                    
                    # Parse the page to find applications
                    soup = BeautifulSoup(approve_response.text, 'html.parser')
                    
                    # Look for application listings
                    applications = []
                    
                    # Method 1: Look for application cards/divs
                    app_elements = soup.find_all(['div', 'li', 'tr'], class_=re.compile(r'app|application', re.I))
                    
                    for element in app_elements:
                        text = element.get_text(strip=True)
                        if len(text) > 10 and len(text) < 200:  # Reasonable length
                            applications.append(text)
                    
                    # Method 2: Look for buttons with "Approve" text
                    approve_buttons = soup.find_all('button', string=re.compile(r'approve', re.I))
                    approve_links = soup.find_all('a', string=re.compile(r'approve', re.I))
                    
                    for button in approve_buttons + approve_links:
                        parent = button.parent
                        if parent:
                            app_name = parent.get_text(strip=True)
                            if app_name and len(app_name) < 200:
                                applications.append(app_name)
                    
                    # Method 3: Look for form inputs with application names
                    forms = soup.find_all('form')
                    for form in forms:
                        inputs = form.find_all('input', {'name': re.compile(r'app', re.I)})
                        for inp in inputs:
                            value = inp.get('value', '')
                            if value and len(value) > 5:
                                applications.append(value)
                    
                    # Clean and deduplicate applications
                    clean_apps = []
                    for app in applications:
                        app = app.strip()
                        if app and len(app) > 5 and app not in clean_apps:
                            # Filter out HTML artifacts
                            if not any(char in app for char in ['<', '>', '{', '}', 'function']):
                                clean_apps.append(app)
                    
                    print(f"\n📋 Found {len(clean_apps)} potential applications:")
                    for i, app in enumerate(clean_apps[:20], 1):  # Show first 20
                        print(f"   {i:2d}. {app}")
                    
                    # Look specifically for MODIS-related terms
                    modis_related = [app for app in clean_apps if any(term in app.lower() for term in 
                                   ['modis', 'laads', 'gesdisc', 'lp daac', 'earthdata', 'atmosphere', 'land'])]
                    
                    if modis_related:
                        print(f"\n🎯 MODIS-related applications found:")
                        for app in modis_related:
                            print(f"   • {app}")
                    
                    return clean_apps
                    
                else:
                    print(f"   ❌ Could not access approve page: {approve_response.status_code}")
            else:
                print(f"   ❌ Login failed: {login_response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return []

def suggest_search_terms():
    """Suggest search terms for finding MODIS applications"""
    print("\n🔍 Search terms to try on the approval page:")
    
    search_terms = [
        "MODIS",
        "LAADS",
        "GESDISC", 
        "LP DAAC",
        "Land Processes",
        "Atmosphere",
        "Terra",
        "Aqua",
        "NASA",
        "Earthdata",
        "EOSDIS",
        "DAAC"
    ]
    
    for term in search_terms:
        print(f"   • {term}")
    
    print("\n💡 Strategy:")
    print("1. Go to: https://urs.earthdata.nasa.gov/approve_app")
    print("2. Click 'Approve More Applications'")
    print("3. Search for each term above")
    print("4. Approve any applications related to NASA data access")

def manual_guidance():
    """Provide manual guidance for finding applications"""
    print("\n📖 Manual Application Approval Guide")
    print("=" * 45)
    
    print("🎯 Since automatic detection is tricky, here's the manual process:")
    
    print("\n1️⃣ Visit: https://urs.earthdata.nasa.gov/approve_app")
    
    print("\n2️⃣ Look for a section like:")
    print("   • 'My Applications'")
    print("   • 'Approved Applications'") 
    print("   • 'Approve More Applications' button")
    
    print("\n3️⃣ Click 'Approve More Applications' or similar")
    
    print("\n4️⃣ You should see a search interface. Search for:")
    print("   • 'NASA' - approve any NASA data services")
    print("   • 'LAADS' - MODIS Atmosphere data")
    print("   • 'LP DAAC' - Land data")
    print("   • 'GESDISC' - Goddard data")
    
    print("\n5️⃣ Approve ALL NASA/EOSDIS data applications you find")
    
    print("\n6️⃣ Wait 5-10 minutes, then test:")
    print("   python mcd43a3_downloader.py")
    
    print("\n💡 If you can't find specific applications:")
    print("   • Approve ANY NASA-related applications")
    print("   • Look for 'EOSDIS' (Earth Observing System Data)")
    print("   • When in doubt, approve it!")

if __name__ == "__main__":
    print("🔍 NASA Earthdata Application Finder")
    print("=" * 45)
    
    # Try to find applications automatically
    apps = find_available_applications()
    
    if not apps:
        print("\n⚠️  Automatic detection failed")
    
    # Provide search terms and manual guidance
    suggest_search_terms()
    manual_guidance()
    
    print("\n" + "=" * 45)
    print("🎯 KEY POINT: Approve ANY NASA data-related applications!")
    print("Better to approve too many than too few.")