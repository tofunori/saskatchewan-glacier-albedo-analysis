#!/usr/bin/env python3
"""
Debug script to check MODIS collections and troubleshoot issues
"""

from modis_tools.auth import ModisSession
from modis_tools.resources import CollectionApi, GranuleApi

def debug_collections():
    """Debug collection queries"""
    print("🔍 Debugging MODIS Collections")
    print("=" * 50)
    
    # Create session
    session = ModisSession()
    collection_client = CollectionApi(session=session)
    
    print("1. Testing MCD10A1 queries...")
    
    # Try different version approaches
    test_queries = [
        {"short_name": "MCD10A1", "version": "061"},
        {"short_name": "MCD10A1", "version": "6"},
        {"short_name": "MCD10A1"},  # No version specified
        {"keyword": "MCD10A1"},
    ]
    
    for i, query in enumerate(test_queries, 1):
        try:
            print(f"   Query {i}: {query}")
            collections = collection_client.query(**query)
            collections_list = list(collections)
            print(f"   ✅ Found {len(collections_list)} collections")
            
            if collections_list:
                for j, collection in enumerate(collections_list[:3]):  # Show first 3
                    print(f"      Collection {j+1}:")
                    print(f"        Title: {getattr(collection, 'title', 'N/A')}")
                    print(f"        Short Name: {getattr(collection, 'short_name', 'N/A')}")
                    print(f"        Version: {getattr(collection, 'version', 'N/A')}")
                    print(f"        Concept ID: {getattr(collection, 'concept_id', 'N/A')}")
                break
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n2. Testing MCD43A3 queries...")
    
    test_queries_43a3 = [
        {"short_name": "MCD43A3", "version": "061"},
        {"short_name": "MCD43A3", "version": "6"},
        {"short_name": "MCD43A3"},
        {"keyword": "MCD43A3"},
    ]
    
    for i, query in enumerate(test_queries_43a3, 1):
        try:
            print(f"   Query {i}: {query}")
            collections = collection_client.query(**query)
            collections_list = list(collections)
            print(f"   ✅ Found {len(collections_list)} collections")
            
            if collections_list:
                for j, collection in enumerate(collections_list[:3]):
                    print(f"      Collection {j+1}:")
                    print(f"        Title: {getattr(collection, 'title', 'N/A')}")
                    print(f"        Short Name: {getattr(collection, 'short_name', 'N/A')}")
                    print(f"        Version: {getattr(collection, 'version', 'N/A')}")
                    print(f"        Concept ID: {getattr(collection, 'concept_id', 'N/A')}")
                break
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_general_search():
    """Test general MODIS searches"""
    print("\n3. Testing general MODIS searches...")
    
    session = ModisSession()
    collection_client = CollectionApi(session=session)
    
    try:
        # Search for any MODIS collections
        collections = collection_client.query(keyword="MODIS")
        collections_list = list(collections)
        print(f"   ✅ Found {len(collections_list)} MODIS collections total")
        
        if collections_list:
            print("   Sample MODIS collections:")
            for i, collection in enumerate(collections_list[:5]):
                print(f"      {i+1}. {getattr(collection, 'short_name', 'Unknown')} v{getattr(collection, 'version', 'Unknown')}")
                
    except Exception as e:
        print(f"   ❌ Error searching MODIS: {e}")

def test_authentication():
    """Test if authentication is working properly"""
    print("\n4. Testing authentication...")
    
    try:
        session = ModisSession()
        print("   ✅ Session created successfully")
        
        # Try to access session attributes
        if hasattr(session, 'session'):
            print("   ✅ Internal session object exists")
        
        # Test with collection client
        collection_client = CollectionApi(session=session)
        print("   ✅ Collection client created successfully")
        
    except Exception as e:
        print(f"   ❌ Authentication error: {e}")
        print("   💡 Tip: Run 'python setup_credentials.py' to set up credentials")

if __name__ == "__main__":
    test_authentication()
    debug_collections()
    test_general_search()
    
    print("\n" + "=" * 50)
    print("🔧 Troubleshooting Tips:")
    print("1. Verify NASA Earthdata credentials are correct")
    print("2. Check if you have access to MODIS data")
    print("3. Try different collection versions (v6 vs v061)")
    print("4. Check NASA Earthdata server status")
    print("5. Verify internet connectivity")