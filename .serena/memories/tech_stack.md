# Technology Stack

## Core Technologies
- **Python 3.8+**: Primary programming language
- **Google Earth Engine**: Satellite data processing and analysis
- **MODIS**: Satellite data source (MCD43A3, MOD10A1)

## Python Dependencies
### Core Libraries:
- **pandas (≥1.3.0)**: Data manipulation and analysis
- **numpy (≥1.21.0)**: Numerical computations
- **matplotlib (≥3.4.0)**: Plotting and visualization
- **seaborn (≥0.11.0)**: Statistical visualization
- **scipy (≥1.7.0)**: Scientific computing and statistics

### Analysis Libraries:
- **scikit-learn (≥0.24.0)**: Machine learning and statistical analysis
- **pymannkendall (≥1.4.0)**: Mann-Kendall trend tests
- **openpyxl (≥3.0.0)**: Excel file handling

### Optional/Development Libraries:
- **pytest (≥6.0)**: Testing framework (dev extra)
- **black (≥21.0)**: Code formatting (dev extra)
- **flake8 (≥3.9)**: Linting (dev extra)
- **mypy (≥0.900)**: Type checking (dev extra)

### Geospatial Libraries (data extra):
- **gdal (≥3.0)**: Geospatial data processing
- **rasterio (≥1.2)**: Raster data I/O
- **geopandas (≥0.9)**: Geospatial data manipulation
- **earthengine-api (≥0.1.300)**: Google Earth Engine Python API

## Package Management
- **setuptools**: Package building and distribution
- **pip**: Package installation
- **Development mode**: `pip install -e .` for editable installation

## Data Formats
- **CSV**: Primary data exchange format
- **GeoTIFF**: Satellite imagery
- **JSON**: Configuration and metadata
- **Excel**: Export and reporting formats