# MODIS Data Processing for Saskatchewan Glacier

This folder contains Python scripts to download and process MODIS satellite data for Saskatchewan Glacier analysis, focusing on:

- **MOD10A1**: Daily snow cover data (500m resolution) - Terra satellite
- **MCD43A3**: 8-day albedo data (500m resolution) - Combined Terra+Aqua

## Setup

### 1. Install Dependencies

```bash
cd modis_data
pip install -r requirements.txt
```

### 2. Set up NASA Earthdata Credentials

You need a NASA Earthdata account: https://earthdata.nasa.gov/

**Option A: Use the setup script (recommended)**
```bash
python setup_credentials.py
```

**Option B: Manual setup**
```python
from modis_tools.auth import add_earthdata_netrc
add_earthdata_netrc("your_username", "your_password")
```

## Usage

### 1. Download MODIS Data

**Option A: With Glacier Mask (Recommended)**
```python
from modis_downloader import SaskatchewanGlacierModisDownloader

# Use precise glacier geometry for spatial filtering
downloader = SaskatchewanGlacierModisDownloader(
    username="your_username",
    password="your_password", 
    glacier_mask_path="saskatchewan_glacier_mask.geojson"
)
```

**Option B: With Bounding Box**
```bash
python modis_downloader.py
```

Or customize the download:

```python
from modis_downloader import SaskatchewanGlacierModisDownloader

# Use bounding box for spatial filtering (default)
downloader = SaskatchewanGlacierModisDownloader()
downloader.authenticate()

# Download summer 2023 data
results = downloader.download_glacier_data(
    start_date="2023-06-01",
    end_date="2023-09-30"
)
```

### 2. Process Downloaded Data

```bash
python data_processor.py
```

This will:
- Create an inventory of downloaded files
- Generate data availability plots
- Analyze file structure and metadata

## Data Products

### MOD10A1 - Snow Cover Daily Global 500m (Terra)

- **Purpose**: Daily snow cover extent and fractional snow cover
- **Resolution**: 500m
- **Satellite**: Terra
- **Key Datasets**:
  - Snow Cover Daily Tile: Binary snow/no-snow
  - Snow Cover Fractional: Percentage snow cover
  - Snow Cover Quality Assessment

### MCD43A3 - BRDF/Albedo Daily L3 Global 500m

- **Purpose**: Surface albedo and BRDF parameters
- **Resolution**: 500m
- **Key Datasets**:
  - White Sky Albedo (WSA)
  - Black Sky Albedo (BSA)
  - BRDF parameters
  - Quality flags

## File Structure

```
modis_data/
├── MOD10A1_snow_cover/     # Downloaded snow cover files
├── MCD43A3_albedo/         # Downloaded albedo files
├── processed/              # Processed outputs
│   ├── file_inventory.csv
│   └── data_availability.png
├── modis_downloader.py     # Download script
├── data_processor.py       # Processing script
├── setup_credentials.py    # Credential setup
├── modis_analysis.ipynb    # Interactive Jupyter notebook
├── export_glacier_mask.js  # GEE script to export glacier mask
├── quick_setup.py          # Non-interactive credential setup
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Spatial Filtering Options

### Option 1: Glacier Mask (Recommended)

Export your glacier mask from Google Earth Engine:

1. **Run the export script in GEE:**
   ```javascript
   // Copy contents of export_glacier_mask.js to GEE Code Editor
   ```

2. **Download the exported GeoJSON file** to your modis_data folder

3. **Use with the downloader:**
   ```python
   downloader = SaskatchewanGlacierModisDownloader(
       username="your_username",
       password="your_password",
       glacier_mask_path="saskatchewan_glacier_mask.geojson"
   )
   ```

**Benefits:**
- ✅ Precise spatial filtering using exact glacier boundaries
- ✅ Fewer unnecessary downloads
- ✅ Better data efficiency
- ✅ Supports GeoJSON, Shapefile, and other formats

### Option 2: Bounding Box (Default)

## Advanced Usage

### Custom Bounding Box

Edit the bounding box in `modis_downloader.py`:

```python
# Current Saskatchewan Glacier area (approximate)
self.saskatchewan_bbox = [-117.3, 52.1, -117.1, 52.3]  # [west, south, east, north]
```

### Multithreaded Downloads

Downloads use all available CPU cores by default (`threads=-1`). To limit:

```python
GranuleHandler.download_from_granules(
    granules, 
    session=session, 
    threads=4  # Use 4 threads
)
```

### File Format Filtering

Download specific file types:

```python
file_paths = GranuleHandler.download_from_granules(
    granules, 
    session=session,
    ext=("hdf", "h5")  # Only HDF files
)
```

## Integration with Google Earth Engine

The existing JavaScript files in the parent directory work with Google Earth Engine. This Python approach provides:

- **Local data storage**: Files stored locally for offline analysis
- **Custom processing**: Full control over data processing pipelines
- **Integration capabilities**: Can be combined with GEE workflows

## Troubleshooting

### Authentication Issues
- Ensure NASA Earthdata credentials are correct
- Check `.netrc` file permissions: `chmod 600 ~/.netrc`
- Try removing and re-adding credentials

### Download Issues
- Check internet connection
- Verify bounding box coordinates
- Ensure sufficient disk space
- Check NASA Earthdata server status

### File Processing Issues
- Verify HDF/NetCDF libraries are installed
- Check GDAL installation for spatial operations
- Ensure files downloaded completely

## Next Steps

1. **Data Analysis**: Process HDF files to extract specific bands
2. **Time Series**: Create temporal analysis scripts
3. **Spatial Analysis**: Clip data to glacier boundaries
4. **Visualization**: Create maps and plots of results
5. **Integration**: Combine with existing GEE analysis