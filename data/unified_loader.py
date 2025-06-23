"""
Unified Data Loader for Saskatchewan Glacier Albedo Analysis
==========================================================

This module provides a unified interface that can load data from either
CSV files (legacy mode) or PostgreSQL database (new mode) based on configuration.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATA_MODE

def get_albedo_handler(*args, **kwargs):
    """
    Get appropriate AlbedoDataHandler based on configuration
    
    Returns:
        AlbedoDataHandler: Either CSV-based or database-based handler
    """
    if DATA_MODE.lower() == "database":
        from data.db_handler import AlbedoDataHandler
        print("🗄️  Using PostgreSQL database mode")
        return AlbedoDataHandler(*args, **kwargs)
    else:
        from data.handler import AlbedoDataHandler
        print("📄 Using CSV file mode")
        return AlbedoDataHandler(*args, **kwargs)

# For backward compatibility
AlbedoDataHandler = get_albedo_handler

if __name__ == "__main__":
    print(f"Data mode configured: {DATA_MODE}")
    
    # Test the loader
    if DATA_MODE.lower() == "database":
        handler = get_albedo_handler("MCD43A3")
        handler.load_data()
        print(f"✅ Database mode test: {len(handler)} observations loaded")
    else:
        print("📄 CSV mode configured - would need CSV path for testing")