#!/usr/bin/env python3
"""
Saskatchewan Glacier Albedo Analysis Dashboard Launcher
======================================================

Simple launcher script for the interactive dashboard.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

def main():
    """Launch the dashboard application"""
    print("🏔️ Saskatchewan Glacier Albedo Analysis Dashboard")
    print("=" * 50)
    print("🚀 Starting dashboard server...")
    print("📊 Loading MODIS data (2010-2024)...")
    print("🌐 Dashboard will open in your browser")
    print("=" * 50)
    
    try:
        from dashboard.app import app
        # Run with auto-reload for development
        app.run(host="127.0.0.1", port=8000, debug=True, reload=True)
    except ImportError as e:
        print(f"❌ Error importing dashboard: {e}")
        print("💡 Make sure you have installed all requirements:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()