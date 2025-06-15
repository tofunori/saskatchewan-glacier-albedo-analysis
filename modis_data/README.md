# MODIS Data Processing for Saskatchewan Glacier

This folder contains Python scripts to download and process MODIS satellite data for Saskatchewan Glacier analysis, focusing on:

- **MCD10A1**: Daily snow cover data (500m resolution)
- **MCD43A3**: 8-day albedo data (500m resolution)

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

```bash
python modis_downloader.py
```

Or customize the download:

```python
from modis_downloader import SaskatchewanGlacierModisDownloader

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

### MCD10A1 - Snow Cover Daily Global 500m

- **Purpose**: Daily snow cover extent and fractional snow cover
- **Resolution**: 500m
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
├── MCD10A1_snow_cover/     # Downloaded snow cover files
├── MCD43A3_albedo/         # Downloaded albedo files
├── processed/              # Processed outputs
│   ├── file_inventory.csv
│   └── data_availability.png
├── modis_downloader.py     # Download script
├── data_processor.py       # Processing script
├── setup_credentials.py    # Credential setup
├── modis_analysis.ipynb    # Interactive Jupyter notebook
├── requirements.txt        # Dependencies
└── README.md              # This file
```

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