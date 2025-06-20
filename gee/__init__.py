"""
Google Earth Engine integration module for Saskatchewan Glacier Albedo Analysis

This module provides direct integration with Google Earth Engine to fetch
MODIS satellite data for albedo analysis, complementing the existing CSV workflow.
"""

__version__ = "1.0.0"
__author__ = "Saskatchewan Glacier Albedo Analysis Team"

from .client import GEEClient
from .saskatchewan import SaskatchewanMODISFetcher
from .exporter import DataExporter

__all__ = ["GEEClient", "SaskatchewanMODISFetcher", "DataExporter"]