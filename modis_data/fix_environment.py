#!/usr/bin/env python3
"""
Diagnose and fix environment encoding issues
"""

import os
import sys
import locale

def diagnose_environment():
    """Diagnose encoding issues in environment"""
    print("🔍 Environment Encoding Diagnostic")
    print("=" * 40)
    
    print(f"🐍 Python Information:")
    print(f"   Version: {sys.version}")
    print(f"   Executable: {sys.executable}")
    print(f"   Platform: {sys.platform}")
    print(f"   Default encoding: {sys.getdefaultencoding()}")
    print(f"   File system encoding: {sys.getfilesystemencoding()}")
    
    print(f"\n🌍 Locale Information:")
    try:
        loc = locale.getlocale()
        print(f"   Current locale: {loc}")
        print(f"   Preferred encoding: {locale.getpreferredencoding()}")
    except Exception as e:
        print(f"   ❌ Error getting locale: {e}")
    
    print(f"\n📁 Environment Variables:")
    problematic_vars = []
    
    important_vars = [
        'PATH', 'PYTHONPATH', 'CONDA_PREFIX', 'CONDA_DEFAULT_ENV',
        'GDAL_DATA', 'PROJ_LIB', 'GDAL_DRIVER_PATH',
        'USERNAME', 'USERPROFILE', 'HOME', 'TEMP', 'TMP'
    ]
    
    for var in important_vars:
        value = os.environ.get(var, 'Not set')
        try:
            # Try to encode/decode to check for issues
            if value != 'Not set':
                value.encode('utf-8').decode('utf-8')
                print(f"   ✅ {var}: {value[:80]}{'...' if len(value) > 80 else ''}")
        except UnicodeError:
            print(f"   ❌ {var}: Contains non-UTF-8 characters")
            problematic_vars.append(var)
        except Exception as e:
            print(f"   ⚠️  {var}: Error checking - {e}")
    
    if problematic_vars:
        print(f"\n🚨 Found problematic environment variables:")
        for var in problematic_vars:
            print(f"   • {var}")
    
    return len(problematic_vars) == 0

def fix_conda_environment():
    """Try to fix conda environment encoding"""
    print(f"\n🔧 Fixing Conda Environment...")
    
    # Set UTF-8 encoding explicitly
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['LC_ALL'] = 'C.UTF-8'
    
    # Clear potentially problematic GDAL variables
    gdal_vars = ['GDAL_DATA', 'PROJ_LIB', 'GDAL_DRIVER_PATH']
    for var in gdal_vars:
        if var in os.environ:
            print(f"   🧹 Clearing {var}")
            del os.environ[var]
    
    print("   ✅ Environment variables updated")

def test_rasterio_after_fix():
    """Test if rasterio works after environment fix"""
    print(f"\n🧪 Testing rasterio after environment fix...")
    
    try:
        import rasterio
        print("   ✅ rasterio import successful")
        
        # Try to open a simple dataset
        test_file = r"D:\Downloads\MCD43A3_downloads\*.hdf"
        import glob
        hdf_files = glob.glob(test_file)
        
        if hdf_files:
            test_hdf = hdf_files[0]
            print(f"   🔍 Testing with: {os.path.basename(test_hdf)}")
            
            try:
                with rasterio.open(test_hdf) as src:
                    subdatasets = src.subdatasets
                    print(f"   ✅ Successfully opened HDF file")
                    print(f"   📊 Found {len(subdatasets)} subdatasets")
                    return True
            except UnicodeDecodeError as e:
                print(f"   ❌ Still getting UTF-8 error: {e}")
                return False
            except Exception as e:
                print(f"   ⚠️  Other error: {e}")
                return False
        else:
            print("   ⚠️  No HDF files found to test")
            return False
            
    except Exception as e:
        print(f"   ❌ rasterio import failed: {e}")
        return False

def create_environment_fix_script():
    """Create a script to fix environment before running rasterio"""
    script_content = '''#!/usr/bin/env python3
"""
Set environment variables before importing rasterio
"""

import os
import sys

# Fix encoding environment variables
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LC_ALL'] = 'C.UTF-8'

# Clear problematic GDAL variables
gdal_vars = ['GDAL_DATA', 'PROJ_LIB', 'GDAL_DRIVER_PATH']
for var in gdal_vars:
    if var in os.environ:
        del os.environ[var]

print("🔧 Environment fixed for rasterio")

# Now import and use rasterio
try:
    import rasterio
    print("✅ rasterio imported successfully")
    
    # Your clipping code here...
    from simple_modis_clipper import clip_modis_hdf_files
    clip_modis_hdf_files()
    
except Exception as e:
    print(f"❌ Error: {e}")
'''
    
    script_path = r"D:\Downloads\run_with_fixed_env.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"\n📝 Created environment fix script: {script_path}")
    return script_path

if __name__ == "__main__":
    # Diagnose current environment
    env_ok = diagnose_environment()
    
    if not env_ok:
        print(f"\n🔧 Environment issues detected. Applying fixes...")
        fix_conda_environment()
        
        # Test if fix worked
        if test_rasterio_after_fix():
            print(f"\n🎉 Environment fix successful!")
            print("You can now run your clipping scripts")
        else:
            print(f"\n⚠️  Environment fix didn't resolve rasterio issues")
            print("Recommend using the GDAL-based alternative:")
            print("   python alternative_gdal_clipper.py")
    else:
        print(f"\n✅ Environment appears clean")
        if not test_rasterio_after_fix():
            print("But rasterio still has issues. Try GDAL alternative.")
    
    # Create fix script regardless
    script_path = create_environment_fix_script()
    
    print(f"\n📋 Next Steps:")
    print("1. Try: python alternative_gdal_clipper.py")
    print("2. Or run: python run_with_fixed_env.py")
    print("3. If still issues, the problem may be in rasterio/GDAL installation")