#!/usr/bin/env python3
"""
Academic Dashboard Runner for Saskatchewan Glacier Albedo Analysis
================================================================

Enhanced runner script for the academic-grade dashboard with comprehensive
statistical analysis integration.

Features:
- Dependency validation
- Academic modules verification
- Configuration checking
- Cross-platform support
- Enhanced error handling
"""

import sys
import os
import importlib
import subprocess
from pathlib import Path

def check_academic_dependencies():
    """Check if all academic dashboard dependencies are available"""
    print("🔍 Checking academic dashboard dependencies...")
    
    required_packages = {
        'shiny': 'Shiny for Python',
        'pandas': 'Data manipulation',
        'plotly': 'Interactive plotting', 
        'numpy': 'Numerical computing',
        'scipy': 'Statistical functions',
        'sklearn': 'Machine learning utilities'
    }
    
    missing_packages = []
    
    for package, description in required_packages.items():
        try:
            importlib.import_module(package)
            print(f"  ✅ {package}: {description}")
        except ImportError:
            print(f"  ❌ {package}: {description} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages are available!")
    return True

def check_academic_modules():
    """Check if custom academic modules are available"""
    print("\n🔍 Checking academic analysis modules...")
    
    # Add dashboard directory to path
    dashboard_dir = Path(__file__).parent
    sys.path.insert(0, str(dashboard_dir))
    
    academic_modules = {
        'dashboard.statistical_analysis': 'Statistical Analysis Module',
        'dashboard.academic_plots': 'Academic Visualization Module',
        'dashboard.export_manager': 'Export Management Module'
    }
    
    missing_modules = []
    
    for module, description in academic_modules.items():
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}: {description}")
        except ImportError as e:
            print(f"  ❌ {module}: {description} - MISSING")
            print(f"     Error: {e}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Missing academic modules: {len(missing_modules)}")
        print("🔧 Please ensure all academic modules are properly installed")
        return False
    
    print("✅ All academic modules are available!")
    return True

def check_project_configuration():
    """Check if project configuration is accessible"""
    print("\n🔍 Checking project configuration...")
    
    try:
        # Try to import project configuration
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from config import (FRACTION_CLASSES, CLASS_LABELS, MCD43A3_CONFIG, 
                           MOD10A1_CONFIG, ANALYSIS_CONFIG)
        
        print("  ✅ Configuration imported successfully")
        print(f"  ✅ Fraction classes: {len(FRACTION_CLASSES)} defined")
        print(f"  ✅ Analysis config: Bootstrap iterations = {ANALYSIS_CONFIG.get('bootstrap_iterations', 'Not set')}")
        
        # Check data paths
        data_paths = {
            'MCD43A3': MCD43A3_CONFIG.get('csv_path'),
            'MOD10A1': MOD10A1_CONFIG.get('csv_path')
        }
        
        for dataset, path in data_paths.items():
            if path and os.path.exists(os.path.join(project_root, path)):
                print(f"  ✅ {dataset} data: {path}")
            else:
                print(f"  ⚠️  {dataset} data: {path} - FILE NOT FOUND")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Configuration import failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Configuration check failed: {e}")
        return False

def run_academic_dashboard():
    """Run the academic dashboard"""
    print("\n🚀 Starting Academic Dashboard...")
    print("=" * 60)
    print("🏔️  SASKATCHEWAN GLACIER ALBEDO ANALYSIS")
    print("📊 Academic Dashboard with Statistical Analysis")
    print("=" * 60)
    
    try:
        # Import and run the enhanced dashboard
        from dashboard.app_enhanced import app
        
        print("\n📈 Academic features enabled:")
        print("  • Mann-Kendall trend tests")
        print("  • Sen's slope with bootstrap confidence intervals")
        print("  • Comprehensive seasonal analysis")
        print("  • Publication-quality visualizations")
        print("  • Statistical results export")
        print("  • Academic methodology reports")
        
        print(f"\n🌐 Dashboard will be available at: http://localhost:8000")
        print("📝 Use Ctrl+C to stop the dashboard")
        print("🔬 Academic-grade statistical analysis ready!")
        print("-" * 60)
        
        # Run the app
        app.run(host="0.0.0.0", port=8000, reload=False)
        
    except KeyboardInterrupt:
        print("\n\n👋 Academic dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error running academic dashboard: {e}")
        print("\n🔧 Troubleshooting:")
        print("  1. Check that all dependencies are installed")
        print("  2. Verify project configuration")
        print("  3. Ensure data files are available")
        print("  4. Try running the basic dashboard first")
        sys.exit(1)

def main():
    """Main function with comprehensive validation"""
    print("🔬 Saskatchewan Glacier Albedo - Academic Dashboard")
    print("=" * 55)
    
    # Change to project directory
    project_dir = Path(__file__).parent.parent
    os.chdir(project_dir)
    print(f"📂 Working directory: {project_dir}")
    
    # Validation steps
    validation_steps = [
        ("Dependencies", check_academic_dependencies),
        ("Academic Modules", check_academic_modules), 
        ("Project Configuration", check_project_configuration)
    ]
    
    for step_name, check_function in validation_steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        if not check_function():
            print(f"\n❌ {step_name} validation failed!")
            print("🔧 Please fix the issues above before running the dashboard")
            sys.exit(1)
    
    print(f"\n{'='*25} VALIDATION COMPLETE {'='*25}")
    print("✅ All systems ready for academic analysis!")
    
    # Ask for confirmation
    try:
        response = input("\n🚀 Start academic dashboard? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            run_academic_dashboard()
        else:
            print("👋 Dashboard startup cancelled")
    except KeyboardInterrupt:
        print("\n👋 Startup cancelled by user")

if __name__ == "__main__":
    main()