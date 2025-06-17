"""
Simple test script for the Shiny dashboard
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_data_loading():
    """Test if data can be loaded successfully"""
    try:
        from data.handler import AlbedoDataHandler
        from config import MCD43A3_CONFIG
        
        print("Testing data loading...")
        data_handler = AlbedoDataHandler(MCD43A3_CONFIG['csv_path'])
        data_handler.load_data()
        
        print(f"✓ Data loaded successfully")
        print(f"  - Rows: {len(data_handler.data)}")
        print(f"  - Columns: {len(data_handler.data.columns)}")
        print(f"  - Sample columns: {list(data_handler.data.columns[:5])}")
        
        return True
    except Exception as e:
        print(f"✗ Data loading failed: {e}")
        return False

def test_dependencies():
    """Test if all required dependencies are available"""
    try:
        import shiny
        import pandas
        import plotly
        
        print("Testing dependencies...")
        print(f"✓ Shiny version: {shiny.__version__}")
        print(f"✓ Pandas version: {pandas.__version__}")
        print(f"✓ Plotly version: {plotly.__version__}")
        
        return True
    except ImportError as e:
        print(f"✗ Dependency test failed: {e}")
        return False

def test_config():
    """Test if configuration is accessible"""
    try:
        from config import FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS
        
        print("Testing configuration...")
        print(f"✓ Fraction classes: {FRACTION_CLASSES}")
        print(f"✓ Sample labels: {dict(list(CLASS_LABELS.items())[:2])}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Dashboard Test Suite ===\n")
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Configuration", test_config), 
        ("Data Loading", test_data_loading)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        print("-" * 40)
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Dashboard is ready to run.")
        print("\nTo start the dashboard:")
        print("  cd dashboard")
        print("  ../venv/bin/python3 -m shiny run app.py")
        print("  Then open http://localhost:8000")
    else:
        print("✗ Some tests failed. Check the errors above.")