"""
Saskatchewan Glacier Albedo Analysis Package
===========================================

A comprehensive Python package for analyzing albedo trends in the Saskatchewan Glacier
using MODIS satellite data and statistical trend analysis.

Main Components:
- data: Data loading and handling
- analysis: Trend analysis and statistical tests
- visualization: Charts and plotting functionality
- utils: Helper functions and utilities
"""

__version__ = "1.0.0"
__author__ = "Saskatchewan Glacier Research Team"

# Import main classes for easy access
from .data.handler import AlbedoDataHandler
from .analysis.trends import TrendCalculator
from .visualization.charts import ChartGenerator
from .visualization.monthly import MonthlyVisualizer

__all__ = [
    'AlbedoDataHandler',
    'TrendCalculator', 
    'ChartGenerator',
    'MonthlyVisualizer'
]