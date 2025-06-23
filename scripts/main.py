#!/usr/bin/env python3
"""
Saskatchewan Glacier Albedo Analysis - Main Entry Point
======================================================

Main script for interactive analysis of Saskatchewan Glacier albedo trends
using MODIS satellite data (2010-2024).

Usage:
    python scripts/main.py

The script provides an interactive menu system for:
- MCD43A3 (General albedo analysis)
- MOD10A1 (Snow albedo analysis)  
- Comparative analysis between datasets
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Setup project environment
script_dir = Path(__file__).parent.absolute()
project_dir = script_dir.parent
sys.path.insert(0, str(project_dir))
os.chdir(project_dir)

print(f"📂 Working directory: {Path.cwd()}")
print(f"📁 Project directory: {project_dir}")

# Import core modules
try:
    from config import print_config_summary
    from scripts.analysis_functions import check_datasets_availability
    from scripts.menu_system import MenuController
    print("✅ Modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def initialize_application() -> bool:
    """Initialize application and verify prerequisites."""
    print("\n" + "="*70)
    print("🚀 SASKATCHEWAN GLACIER ALBEDO TREND ANALYSIS")
    print("="*70)
    print("📅 Session started:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Display configuration summary
    print_config_summary()
    
    # Verify dataset availability
    if not check_datasets_availability():
        print("\n❌ No valid datasets found.")
        return False
    
    return True


def main() -> None:
    """Main application entry point."""
    try:
        # Initialize application
        if not initialize_application():
            return
        
        # Start menu controller
        menu_controller = MenuController()
        menu_controller.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("📝 Check logs for more details.")


if __name__ == "__main__":
    main()