#!/usr/bin/env python3
"""
Test Dashboard Structure
=======================

Validate dashboard components and structure without requiring Streamlit.
"""

import os
import sys
from pathlib import Path

def test_dashboard_files():
    """Test that all dashboard files exist and are readable"""
    
    dashboard_files = [
        'dashboard.py',
        'dashboard_components.py', 
        'requirements_dashboard.txt',
        'run_dashboard.py'
    ]
    
    print("🔍 Testing Dashboard Files")
    print("=" * 40)
    
    for file_name in dashboard_files:
        file_path = Path(file_name)
        
        if file_path.exists():
            file_size = file_path.stat().st_size
            print(f"✅ {file_name} ({file_size:,} bytes)")
        else:
            print(f"❌ {file_name} missing")
    
    print()

def test_dashboard_structure():
    """Test dashboard.py structure"""
    
    print("🏗️  Testing Dashboard Structure")
    print("=" * 40)
    
    try:
        with open('dashboard.py', 'r') as f:
            content = f.read()
        
        # Check for main functions
        functions_to_check = [
            'main()',
            'show_home_page()',
            'show_data_management()',
            'show_trend_analysis()',
            'show_visualizations()',
            'show_gee_integration()',
            'show_custom_analysis()',
            'show_configuration()'
        ]
        
        for func in functions_to_check:
            if func.replace('()', '') in content:
                print(f"✅ Function {func} found")
            else:
                print(f"❌ Function {func} missing")
        
        # Check for key components
        components_to_check = [
            'st.header',
            'st.subheader', 
            'st.selectbox',
            'st.button',
            'st.plotly_chart',
            'st.dataframe'
        ]
        
        print("\n📦 Testing Streamlit Components")
        for component in components_to_check:
            count = content.count(component)
            print(f"✅ {component}: {count} uses")
        
    except Exception as e:
        print(f"❌ Error reading dashboard.py: {e}")
    
    print()

def test_dashboard_components():
    """Test dashboard_components.py structure"""
    
    print("🧩 Testing Dashboard Components")
    print("=" * 40)
    
    try:
        with open('dashboard_components.py', 'r') as f:
            content = f.read()
        
        # Check for main classes
        classes_to_check = [
            'class DataManager',
            'class TrendAnalyzer',
            'class Visualizer',
            'class GEEIntegration',
            'class AnalysisRunner'
        ]
        
        for cls in classes_to_check:
            if cls in content:
                print(f"✅ {cls} found")
            else:
                print(f"❌ {cls} missing")
        
        # Count methods
        method_count = content.count('def ')
        print(f"📊 Total methods: {method_count}")
        
    except Exception as e:
        print(f"❌ Error reading dashboard_components.py: {e}")
    
    print()

def test_requirements():
    """Test requirements file"""
    
    print("📋 Testing Requirements")
    print("=" * 40)
    
    try:
        with open('requirements_dashboard.txt', 'r') as f:
            requirements = f.readlines()
        
        print(f"📦 Total requirements: {len(requirements)}")
        
        # Check for key packages
        key_packages = [
            'streamlit',
            'pandas',
            'numpy', 
            'plotly',
            'matplotlib',
            'scipy'
        ]
        
        req_text = ''.join(requirements).lower()
        
        for package in key_packages:
            if package in req_text:
                print(f"✅ {package} specified")
            else:
                print(f"❌ {package} missing")
        
    except Exception as e:
        print(f"❌ Error reading requirements: {e}")
    
    print()

def test_launch_script():
    """Test run_dashboard.py"""
    
    print("🚀 Testing Launch Script")
    print("=" * 40)
    
    try:
        with open('run_dashboard.py', 'r') as f:
            content = f.read()
        
        # Check for key functions
        functions = [
            'check_dependencies',
            'install_dependencies', 
            'launch_dashboard',
            'main'
        ]
        
        for func in functions:
            if f"def {func}" in content:
                print(f"✅ Function {func}() found")
            else:
                print(f"❌ Function {func}() missing")
        
    except Exception as e:
        print(f"❌ Error reading launch script: {e}")
    
    print()

def calculate_dashboard_stats():
    """Calculate dashboard statistics"""
    
    print("📊 Dashboard Statistics")
    print("=" * 40)
    
    try:
        total_lines = 0
        total_files = 0
        
        dashboard_files = ['dashboard.py', 'dashboard_components.py', 'run_dashboard.py']
        
        for file_name in dashboard_files:
            if Path(file_name).exists():
                with open(file_name, 'r') as f:
                    lines = len(f.readlines())
                    total_lines += lines
                    total_files += 1
                    print(f"📄 {file_name}: {lines:,} lines")
        
        print(f"\n📈 Total: {total_files} files, {total_lines:,} lines")
        
        # Check file sizes
        total_size = 0
        for file_name in dashboard_files:
            if Path(file_name).exists():
                size = Path(file_name).stat().st_size
                total_size += size
        
        print(f"💾 Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        
    except Exception as e:
        print(f"❌ Error calculating stats: {e}")

def main():
    """Run all dashboard tests"""
    
    print("🏔️  Saskatchewan Glacier Albedo Analysis - Dashboard Test")
    print("=" * 60)
    print()
    
    test_dashboard_files()
    test_dashboard_structure()
    test_dashboard_components()
    test_requirements()
    test_launch_script()
    calculate_dashboard_stats()
    
    print("🎉 Dashboard structure validation complete!")

if __name__ == "__main__":
    main()