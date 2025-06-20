#!/usr/bin/env python3
"""
Interactive Academic Saskatchewan Glacier Albedo Dashboard Launcher
=================================================================

Launches the fully interactive academic dashboard with Plotly integration.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

def main():
    """Launch the interactive academic dashboard"""
    print("🚀 Interactive Saskatchewan Glacier Albedo Dashboard")
    print("=" * 60)
    print("🎓 Professional Academic Research Interface")
    print("📊 Full Plotly Interactivity • Zoom • Pan • Hover • Select")
    print("🛰️ MODIS Datasets: MCD43A3 & MOD10A1 (2010-2024)")
    print("📈 Advanced Statistical Analysis & Trend Detection")
    print("🌐 Dashboard accessible at: http://127.0.0.1:8000")
    print("=" * 60)
    print("🎯 Interactive Features:")
    print("   • Zoom: Mouse wheel or zoom controls")
    print("   • Pan: Click and drag to navigate")
    print("   • Hover: Rich data tooltips with context")
    print("   • Select: Lasso/box selection for data filtering")
    print("   • Range Selector: Quick time period selection")
    print("   • Crossfilter: Linked selection across plots")
    print("   • Export: Download interactive plots as HTML/PNG")
    print("=" * 60)
    print("📋 Analysis Modules:")
    print("   • Temporal Analysis: Time series with trend detection")
    print("   • Statistical Analysis: Distributions & correlations")
    print("   • Comparative Analysis: Multi-dataset comparison")
    print("   • Data Quality: Coverage & reliability assessment")
    print("=" * 60)
    
    try:
        from dashboard.interactive_academic_dashboard import app
        print("✅ Interactive dashboard loaded successfully!")
        print("🔗 Launching in browser...")
        print("💡 Tip: Use the sidebar controls to customize your analysis")
        print("🎨 Academic styling optimized for research presentations")
        print("=" * 60)
        app.run(host="127.0.0.1", port=8000)
    except ImportError as e:
        print(f"❌ Error importing dashboard: {e}")
        print("💡 Required packages:")
        print("   pip install shiny shinywidgets plotly pandas scipy ipywidgets")
        print("   or run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("💡 Troubleshooting:")
        print("   • Check that data files exist in data/csv/")
        print("   • Verify all dependencies are installed")
        print("   • Ensure port 8000 is available")
        sys.exit(1)

if __name__ == "__main__":
    main()