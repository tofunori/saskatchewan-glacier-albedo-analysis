#!/usr/bin/env python3
"""
Launch script for Saskatchewan Glacier Albedo Analysis Dashboard
============================================================

This script launches the Streamlit dashboard with proper configuration.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available"""
    
    required_packages = [
        'streamlit',
        'pandas', 
        'numpy',
        'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies"""
    
    print("🔧 Installing dashboard dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_dashboard.txt"
        ])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    
    print("🚀 Launching Saskatchewan Glacier Albedo Analysis Dashboard...")
    print("📱 The dashboard will open in your default web browser")
    print("🔧 Use Ctrl+C to stop the dashboard")
    print()
    
    # Set environment variables for Streamlit
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

def main():
    """Main function"""
    
    print("🏔️  Saskatchewan Glacier Albedo Analysis Dashboard")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("dashboard.py").exists():
        print("❌ Error: dashboard.py not found in current directory")
        print("💡 Please run this script from the project root directory")
        return
    
    # Check dependencies
    missing = check_dependencies()
    
    if missing:
        print(f"⚠️  Missing dependencies: {', '.join(missing)}")
        
        # Ask user if they want to install
        response = input("🤔 Would you like to install missing dependencies? (y/n): ").strip().lower()
        
        if response in ['y', 'yes']:
            if not install_dependencies():
                print("❌ Failed to install dependencies. Please install manually:")
                print(f"   pip install {' '.join(missing)}")
                return
        else:
            print("💡 Please install missing dependencies manually:")
            print(f"   pip install {' '.join(missing)}")
            return
    
    # Launch dashboard
    launch_dashboard()

if __name__ == "__main__":
    main()