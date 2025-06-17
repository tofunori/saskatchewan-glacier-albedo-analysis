"""
Core PixelVisualizer Base Class
==============================

This module contains the base PixelVisualizer class with core functionality
and shared methods for pixel count and QA visualizations.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from scipy.interpolate import make_interp_spline

# Import from package
from config import (FRACTION_CLASSES, CLASS_LABELS, MONTH_NAMES, FRACTION_COLORS,
                      PLOT_STYLES, OUTPUT_DIR)
from utils.helpers import print_section_header, ensure_directory_exists


class BasePixelVisualizer:
    """
    Base visualizer for pixel count and QA statistics
    
    This is the core class that provides shared functionality for all
    pixel-related visualizations. Specialized classes inherit from this.
    """
    
    def __init__(self, data_handler):
        """
        Initialize the base pixel visualizer
        
        Args:
            data_handler: AlbedoDataHandler instance with loaded data
        """
        self.data_handler = data_handler
        self.data = data_handler.data
        self.fraction_classes = FRACTION_CLASSES
        self.class_labels = CLASS_LABELS
        
        # Academic color scheme for publication
        self.academic_colors = {
            'border': '#d62728',      # Red
            'mixed_low': '#ff7f0e',   # Orange  
            'mixed_high': '#2ca02c',  # Green
            'mostly_ice': '#1f77b4',  # Blue
            'pure_ice': '#17becf'     # Cyan
        }
    
    def _create_smooth_line(self, x_data, y_data, num_points=300):
        """
        Create smooth interpolated line for plotting
        
        Args:
            x_data: X coordinates (dates converted to numeric)
            y_data: Y coordinates (values)
            num_points: Number of points for smooth line
            
        Returns:
            tuple: (x_smooth, y_smooth) for plotting
        """
        if len(x_data) < 3:  # Need at least 3 points for spline
            return x_data, y_data
        
        try:
            # Convert dates to numeric for interpolation
            x_numeric = np.arange(len(x_data))
            
            # Create spline interpolation
            spline = make_interp_spline(x_numeric, y_data, k=min(3, len(x_data)-1))
            
            # Generate smooth line
            x_smooth_numeric = np.linspace(x_numeric.min(), x_numeric.max(), num_points)
            y_smooth = spline(x_smooth_numeric)
            
            # Map back to original x scale
            x_smooth = np.interp(x_smooth_numeric, x_numeric, np.arange(len(x_data)))
            x_smooth_dates = [x_data.iloc[int(i)] if int(i) < len(x_data) else x_data.iloc[-1] 
                             for i in x_smooth]
            
            return x_smooth_dates, y_smooth
        except:
            # Fallback to original data if interpolation fails
            return x_data, y_data
    
    def _generate_year_summary_stats(self, year, year_data, pixel_analyzer):
        """
        Generate enhanced summary statistics text for a year
        
        Args:
            year (int): Year
            year_data (pd.DataFrame): Data for this year
            pixel_analyzer: PixelCountAnalyzer instance
            
        Returns:
            str: Enhanced summary statistics text
        """
        stats_lines = [f"📊 ANALYSIS SUMMARY {year}"]
        
        # Basic statistics
        total_days = len(year_data)
        date_range = f"{year_data['date'].min().strftime('%m/%d')} to {year_data['date'].max().strftime('%m/%d')}"
        stats_lines.append(f"• {total_days} observation days ({date_range})")
        
        # Albedo statistics
        albedo_cols = [f"{fraction}_mean" for fraction in self.fraction_classes 
                      if f"{fraction}_mean" in year_data.columns]
        if albedo_cols:
            avg_albedo = year_data[albedo_cols].mean().mean()
            max_albedo = year_data[albedo_cols].max().max()
            min_albedo = year_data[albedo_cols].min().min()
            stats_lines.append(f"• Albedo range: {min_albedo:.3f} - {max_albedo:.3f} (avg: {avg_albedo:.3f})")
        
        # Pixel count statistics
        pixel_cols = [f"{fraction}_pixel_count" for fraction in self.fraction_classes 
                     if f"{fraction}_pixel_count" in year_data.columns]
        if pixel_cols:
            total_pixels = year_data[pixel_cols].sum(axis=1)
            avg_pixels = total_pixels.mean()
            max_pixels = total_pixels.max()
            stats_lines.append(f"• Total pixels/day: {avg_pixels:.0f} avg, {max_pixels:.0f} max")
        
        # Data availability by month
        monthly_counts = year_data['month'].value_counts().sort_index()
        month_names = {6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep'}
        month_summary = ", ".join([f"{month_names.get(m, str(m))}({count})" for m, count in monthly_counts.items()])
        stats_lines.append(f"• Monthly distribution: {month_summary}")
        
        # Quality assessment summary if available
        if pixel_analyzer.qa_data is not None:
            year_qa = pixel_analyzer.qa_data[pixel_analyzer.qa_data['year'] == year]
            if not year_qa.empty:
                qa_cols = ['quality_0_best', 'quality_1_good', 'quality_2_moderate', 'quality_3_poor']
                available_qa_cols = [col for col in qa_cols if col in year_qa.columns]
                if available_qa_cols:
                    qa_totals = year_qa[available_qa_cols].sum()
                    best_qa_pct = (qa_totals.iloc[0] / qa_totals.sum()) * 100 if qa_totals.sum() > 0 else 0
                    stats_lines.append(f"• Data quality: {best_qa_pct:.1f}% excellent quality")
        
        return "\n".join(stats_lines)
    
    def create_monthly_pixel_count_plots(self, monthly_pixel_results, save_path=None):
        """
        Create visualizations for monthly pixel count analysis
        
        Args:
            monthly_pixel_results (dict): Results from analyze_monthly_pixel_counts()
            save_path (str, optional): Path to save the plot
            
        Returns:
            str: Path to saved plot
        """
        print_section_header("Création des graphiques mensuels des comptages de pixels", level=2)
        
        if 'monthly_dataframe' not in monthly_pixel_results or monthly_pixel_results['monthly_dataframe'].empty:
            print("❌ Pas de données mensuelles pour créer les graphiques")
            return None
        
        monthly_stats = monthly_pixel_results['monthly_dataframe']
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Analyse Mensuelle des Comptages de Pixels par Fraction', 
                     fontsize=16, fontweight='bold', y=0.98)
        
        # Plot 1: Monthly trends for each fraction
        self._plot_monthly_trends(axes[0, 0], monthly_stats)
        
        # Plot 2: Fraction composition by month
        self._plot_fraction_composition(axes[0, 1], monthly_stats)
        
        # Plot 3: Seasonal variations
        self._plot_seasonal_variations(axes[1, 0], monthly_stats)
        
        # Plot 4: Data availability heatmap
        self._plot_availability_heatmap(axes[1, 1], monthly_stats)
        
        plt.tight_layout()
        
        # Save the plot
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, 'monthly_pixel_count_analysis.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Graphiques mensuels sauvegardés: {save_path}")
        
        plt.close()
        return save_path
    
    def _plot_monthly_trends(self, ax, monthly_stats):
        """Plot monthly trends for pixel counts"""
        # Implementation for monthly trends
        for fraction in self.fraction_classes:
            pixel_col = f"{fraction}_pixel_count"
            if pixel_col in monthly_stats.columns:
                monthly_data = monthly_stats.groupby('month')[pixel_col].mean()
                ax.plot(monthly_data.index, monthly_data.values, 
                       marker='o', label=self.class_labels[fraction], linewidth=2)
        
        ax.set_title('Tendances Mensuelles des Comptages de Pixels')
        ax.set_xlabel('Mois')
        ax.set_ylabel('Nombre Moyen de Pixels')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_fraction_composition(self, ax, monthly_stats):
        """Plot fraction composition by month"""
        # Stacked bar chart of fractions by month
        months = sorted(monthly_stats['month'].unique())
        bottom = np.zeros(len(months))
        
        for i, fraction in enumerate(self.fraction_classes):
            pixel_col = f"{fraction}_pixel_count"
            if pixel_col in monthly_stats.columns:
                values = [monthly_stats[monthly_stats['month'] == m][pixel_col].mean() 
                         for m in months]
                ax.bar(months, values, bottom=bottom, 
                      label=self.class_labels[fraction], 
                      color=self.academic_colors.get(fraction, f'C{i}'))
                bottom += values
        
        ax.set_title('Composition des Fractions par Mois')
        ax.set_xlabel('Mois')
        ax.set_ylabel('Nombre de Pixels')
        ax.legend()
    
    def _plot_seasonal_variations(self, ax, monthly_stats):
        """Plot seasonal variations"""
        # Box plots for seasonal analysis
        seasonal_data = []
        seasonal_labels = []
        
        for fraction in self.fraction_classes:
            pixel_col = f"{fraction}_pixel_count"
            if pixel_col in monthly_stats.columns:
                values = monthly_stats[monthly_stats[pixel_col].notna()][pixel_col]
                if len(values) > 0:
                    seasonal_data.append(values)
                    seasonal_labels.append(self.class_labels[fraction])
        
        if seasonal_data:
            bp = ax.boxplot(seasonal_data, labels=seasonal_labels, patch_artist=True)
            for patch, color in zip(bp['boxes'], [self.academic_colors.get(f, 'lightblue') 
                                                 for f in self.fraction_classes[:len(seasonal_data)]]):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
        
        ax.set_title('Variations Saisonnières')
        ax.set_ylabel('Nombre de Pixels')
        ax.tick_params(axis='x', rotation=45)
    
    def _plot_availability_heatmap(self, ax, monthly_stats):
        """Plot data availability heatmap"""
        # Create availability matrix
        years = sorted(monthly_stats['year'].unique())
        months = [6, 7, 8, 9]  # Melt season months
        
        availability_matrix = np.zeros((len(years), len(months)))
        
        for i, year in enumerate(years):
            for j, month in enumerate(months):
                year_month_data = monthly_stats[
                    (monthly_stats['year'] == year) & 
                    (monthly_stats['month'] == month)
                ]
                if not year_month_data.empty:
                    # Calculate data availability (non-zero pixel counts)
                    pixel_cols = [f"{f}_pixel_count" for f in self.fraction_classes 
                                 if f"{f}_pixel_count" in monthly_stats.columns]
                    total_pixels = year_month_data[pixel_cols].sum(axis=1)
                    availability_matrix[i, j] = (total_pixels > 0).mean() * 100
        
        im = ax.imshow(availability_matrix, cmap='YlOrRd', aspect='auto')
        ax.set_title('Disponibilité des Données (%)')
        ax.set_xlabel('Mois')
        ax.set_ylabel('Année')
        ax.set_xticks(range(len(months)))
        ax.set_xticklabels([f'{m:02d}' for m in months])
        ax.set_yticks(range(len(years)))
        ax.set_yticklabels(years)
        
        # Add colorbar
        plt.colorbar(im, ax=ax, shrink=0.8)