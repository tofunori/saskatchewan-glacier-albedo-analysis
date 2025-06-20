#!/usr/bin/env python3
"""
Academic Saskatchewan Glacier Albedo Dashboard Launcher
======================================================

Launches the professional academic-style dashboard.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

def main():
    """Launch the academic dashboard"""
    print("🎓 Saskatchewan Glacier Albedo Analysis - Academic Dashboard")
    print("=" * 60)
    print("🚀 Starting professional research dashboard...")
    print("📊 Loading MODIS datasets (MCD43A3 & MOD10A1)")
    print("📈 Initializing statistical analysis modules...")
    print("🌐 Dashboard accessible at: http://127.0.0.1:8000")
    print("=" * 60)
    print("📋 Features:")
    print("   • Professional academic styling")
    print("   • Comprehensive temporal analysis")
    print("   • Statistical trend detection")
    print("   • Multi-dataset comparison")
    print("   • Publication-ready visualizations")
    print("=" * 60)
    
    try:
        from dashboard.academic_dashboard import app
        print("✅ Dashboard loaded successfully!")
        print("🔗 Opening in browser...")
        app.run(host="127.0.0.1", port=8000)
    except ImportError as e:
        print(f"❌ Error importing dashboard: {e}")
        print("💡 Required packages: shiny matplotlib seaborn pandas scipy")
        print("   Install with: pip install shiny matplotlib seaborn pandas scipy")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()