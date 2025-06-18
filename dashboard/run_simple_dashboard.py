#!/usr/bin/env python3
"""
Simple Saskatchewan Glacier Albedo Dashboard Launcher
====================================================

Launches the simplified dashboard version with minimal dependencies.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

def main():
    """Launch the simplified dashboard"""
    print("🏔️ Saskatchewan Glacier Albedo Analysis Dashboard (Simple)")
    print("=" * 55)
    print("🚀 Starting simplified dashboard server...")
    print("📊 Loading MODIS data (2010-2024)...")
    print("🌐 Dashboard will open at: http://127.0.0.1:8000")
    print("=" * 55)
    
    try:
        from dashboard.simple_app import app
        app.run(host="127.0.0.1", port=8000)
    except ImportError as e:
        print(f"❌ Error importing dashboard: {e}")
        print("💡 Make sure you have the basic requirements:")
        print("   pip install shiny plotly pandas")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()