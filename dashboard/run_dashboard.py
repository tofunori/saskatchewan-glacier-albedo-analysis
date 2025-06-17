"""
Simple script to run the Saskatchewan Glacier Albedo Dashboard
===========================================================

This script handles the dashboard startup with proper error handling.
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['shiny', 'pandas', 'plotly']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is available")
        except ImportError:
            missing.append(package)
            print(f"✗ {package} is missing")
    
    if missing:
        print(f"\nMissing packages: {missing}")
        print("Install them with: pip install " + " ".join(missing))
        return False
    
    return True

def run_dashboard():
    """Run the dashboard with proper error handling"""
    
    print("=" * 60)
    print("🏔️  Saskatchewan Glacier Albedo Analysis Dashboard")
    print("=" * 60)
    
    # Check dependencies
    print("\nChecking dependencies...")
    if not check_dependencies():
        return False
    
    # Get the current directory
    dashboard_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(dashboard_dir, "app.py")
    
    if not os.path.exists(app_path):
        print(f"Error: Dashboard app not found at {app_path}")
        return False
    
    print(f"\nStarting dashboard from: {dashboard_dir}")
    print("Dashboard will be available at: http://localhost:8000")
    print("\nPress Ctrl+C to stop the dashboard")
    print("-" * 60)
    
    try:
        # Run the dashboard
        os.chdir(dashboard_dir)
        result = subprocess.run([
            sys.executable, "-m", "shiny", "run", "app.py",
            "--host", "0.0.0.0", "--port", "8000"
        ], check=True)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error running dashboard: {e}")
        return False
    except KeyboardInterrupt:
        print("\n\nDashboard stopped by user")
        return True
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = run_dashboard()
    if not success:
        print("\n❌ Dashboard failed to start")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the correct directory")
        print("2. Install missing dependencies: pip install shiny pandas plotly")
        print("3. Check that data files exist in ../data/csv/")
        sys.exit(1)
    else:
        print("\n✅ Dashboard completed successfully")