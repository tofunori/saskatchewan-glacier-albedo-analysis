# Suggested Commands

## Installation and Setup
```bash
# Clone repository
git clone https://github.com/tofunori/saskatchewan-glacier-albedo-analysis.git
cd saskatchewan-glacier-albedo-analysis

# Install package in development mode
pip install -e .

# Install with all dependencies (if requirements.txt existed)
# pip install -r requirements.txt  # (Not available - use setup.py)

# Install with optional dependencies
pip install -e .[dev]  # Development tools
pip install -e .[data]  # Geospatial data tools
```

## Running the Analysis
```bash
# Main interactive interface (recommended)
python scripts/main.py

# Alternative: as installed console script
saskatchewan-albedo

# Alternative: as module
python -m scripts.main
```

## Development Commands
```bash
# No formal test suite exists
# No linting/formatting commands configured in project
# No automated CI/CD pipeline

# Manual testing through interactive menu system
```

## Project Navigation
```bash
# List project structure
ls -la

# Check data availability
ls -la data/
ls -la results/

# View configuration
cat config.py

# Check Git status
git status
git log --oneline -10
```

## Data Management
```bash
# Results are saved to results/ directory
ls -la results/

# Data inputs expected in data/ directory
ls -la data/

# CSV data files (when available)
ls -la data/csv/ 2>/dev/null || echo "CSV directory not found"
```

## Google Earth Engine Integration
```bash
# Earth Engine authentication (if needed)
earthengine authenticate

# Check Earth Engine status
earthengine --help
```

## System Commands (Linux)
```bash
# File operations
ls, cat, grep, find, cd, pwd

# Package management
pip, python

# Version control
git status, git add, git commit, git push

# Process management
ps, top, htop

# File permissions
chmod, chown

# Text processing
sed, awk, cut, sort, uniq
```