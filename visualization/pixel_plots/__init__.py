"""
Pixel Plots Module
==================

This module provides specialized visualizations for pixel count and QA statistics.
It has been restructured into smaller, focused submodules:

- core.py: Base PixelVisualizer class with common functionality
- daily_plots.py: Daily melt season plot generation
- fraction_comparison.py: MOD10A1 inter-fraction comparison (Phase 2)
- quality_plots.py: QA-specific visualizations

Usage:
    from saskatchewan_albedo.visualization.pixel_plots import PixelVisualizer
"""

from .core import BasePixelVisualizer
from .daily_plots import DailyPlotsVisualizer
from .fraction_comparison import FractionComparisonVisualizer
from .quality_plots import QualityPlotsVisualizer


class PixelVisualizer(BasePixelVisualizer):
    """
    Unified PixelVisualizer class that combines all specialized visualizers
    
    This class maintains backward compatibility while providing access to
    all pixel visualization functionality through composition.
    """
    
    def __init__(self, data_handler):
        """
        Initialize the unified pixel visualizer
        
        Args:
            data_handler: AlbedoDataHandler instance with loaded data
        """
        # Initialize the base class
        super().__init__(data_handler)
        
        # Initialize specialized visualizers as components
        self.daily_plots = DailyPlotsVisualizer(data_handler)
        self.fraction_comparison = FractionComparisonVisualizer(data_handler)
        self.quality_plots = QualityPlotsVisualizer(data_handler)
    
    # Delegate methods to specialized visualizers
    def create_daily_melt_season_plots(self, *args, **kwargs):
        return self.daily_plots.create_daily_melt_season_plots(*args, **kwargs)
    
    def plot_mod10a1_fraction_comparison(self, *args, **kwargs):
        return self.fraction_comparison.plot_mod10a1_fraction_comparison(*args, **kwargs)
    
    def create_qa_statistics_plots(self, *args, **kwargs):
        return self.quality_plots.create_qa_statistics_plots(*args, **kwargs)
    
    def create_pixel_availability_heatmap(self, *args, **kwargs):
        return self.quality_plots.create_pixel_availability_heatmap(*args, **kwargs)
    
    def create_total_pixels_timeseries(self, *args, **kwargs):
        return self.quality_plots.create_total_pixels_timeseries(*args, **kwargs)
    
    def get_available_methods(self):
        """
        Get a list of all available visualization methods
        
        Returns:
            dict: Dictionary of method categories and their available methods
        """
        return {
            'core_methods': [
                'create_monthly_pixel_count_plots',
                '_generate_year_summary_stats',
                '_create_smooth_line'
            ],
            'daily_plots': [
                'create_daily_melt_season_plots',
                '_create_yearly_daily_plot',
                '_create_hybrid_albedo_analysis',
                '_create_pixel_count_stacked_bars',
                '_create_qa_stacked_bars'
            ],
            'fraction_comparison': [
                'plot_mod10a1_fraction_comparison',
                '_create_fraction_timeseries_comparison',
                '_create_fraction_correlation_matrix',
                '_create_fraction_monthly_distribution',
                '_create_fraction_trend_comparison',
                '_export_fraction_statistics'
            ],
            'quality_plots': [
                'create_qa_statistics_plots',
                'create_pixel_availability_heatmap',
                'create_total_pixels_timeseries'
            ]
        }


# For backward compatibility, also export the old name
__all__ = ['PixelVisualizer', 'BasePixelVisualizer', 'DailyPlotsVisualizer', 
           'FractionComparisonVisualizer', 'QualityPlotsVisualizer']