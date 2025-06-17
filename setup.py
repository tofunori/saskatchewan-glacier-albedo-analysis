"""
Setup script for Saskatchewan Glacier Albedo Analysis package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="saskatchewan-albedo",
    version="1.0.0",
    author="Saskatchewan Glacier Research Team",
    author_email="research@example.com",
    description="A comprehensive package for analyzing albedo trends in the Saskatchewan Glacier using MODIS satellite data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tofunori/saskatchewan-glacier-albedo-analysis",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "scipy>=1.7.0",
        "scikit-learn>=0.24.0",
        "pymannkendall>=1.4.0",
        "openpyxl>=3.0.0",
        "pathlib",
        "datetime",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.900",
        ],
        "data": [
            "gdal>=3.0",
            "rasterio>=1.2",
            "geopandas>=0.9",
            "earthengine-api>=0.1.300",
        ],
    },
    entry_points={
        "console_scripts": [
            "saskatchewan-albedo=scripts.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["data/*.json", "config/*.yaml"],
    },
)