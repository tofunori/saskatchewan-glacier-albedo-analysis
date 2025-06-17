"""
Daily Melt Season Plots
======================

This module handles the creation of daily melt season plots with stacked bars
and enhanced visualizations for each year's melt season data.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

from utils.helpers import print_section_header, ensure_directory_exists
from config import OUTPUT_DIR
from .core import BasePixelVisualizer


class DailyPlotsVisualizer(BasePixelVisualizer):
    """
    Specialized visualizer for daily melt season plots
    """
    
    def create_daily_melt_season_plots(self, pixel_analyzer, save_dir=None, dataset_suffix=""):
        """
        Create daily QA and pixel count plots for each year's melt season
        
        Args:
            pixel_analyzer: PixelCountAnalyzer instance with loaded data
            save_dir (str, optional): Directory to save the plots
            dataset_suffix (str, optional): Suffix to add to filenames for dataset identification
            
        Returns:
            list: Paths to saved plots for each year
        """
        print_section_header("Création des graphiques quotidiens par saison de fonte", level=2)
        
        if save_dir is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_dir = OUTPUT_DIR
        
        # Get available years from the data
        years = sorted(self.data['year'].unique())
        print(f"📅 Années disponibles: {years}")
        
        saved_plots = []
        
        for year in years:
            print(f"\n🎯 Création des graphiques pour l'année {year}")
            
            # Filter data for this year's melt season (June-September)
            year_data = self.data[
                (self.data['year'] == year) & 
                (self.data['month'].isin([6, 7, 8, 9]))
            ].copy()
            
            if len(year_data) == 0:
                print(f"⚠️ Pas de données pour {year}")
                continue
            
            # Create plot for this year
            plot_path = self._create_yearly_daily_plot(year, year_data, pixel_analyzer, save_dir, dataset_suffix)
            if plot_path:
                saved_plots.append(plot_path)
        
        print(f"\n✅ {len(saved_plots)} graphiques annuels créés")
        return saved_plots
    
    def _create_yearly_daily_plot(self, year, year_data, pixel_analyzer, save_dir, dataset_suffix=""):
        """
        Create daily plot for a specific year's melt season with improved design
        
        Args:
            year (int): Year to plot
            year_data (pd.DataFrame): Data for this year
            pixel_analyzer: PixelCountAnalyzer instance
            save_dir (str): Directory to save the plot
            dataset_suffix (str): Suffix to add to filename
            
        Returns:
            str: Path to saved plot
        """
        # Create figure with 3 vertically stacked subplots for better readability
        fig, axes = plt.subplots(3, 1, figsize=(16, 18), gridspec_kw={'hspace': 0.4})
        
        # Enhanced title with dataset info
        dataset_name = "MOD10A1" if "mod10a1" in dataset_suffix else "MCD43A3"
        fig.suptitle(f'Daily Melt Season Analysis {year} - {dataset_name}\nSaskatchewan Glacier Albedo Monitoring', 
                     fontsize=20, fontweight='bold', y=0.98)
        
        # Modern color palette - more distinct and professional
        modern_colors = {
            'border': '#e74c3c',      # Bright red
            'mixed_low': '#f39c12',   # Orange
            'mixed_high': '#2ecc71',  # Green  
            'mostly_ice': '#3498db',  # Blue
            'pure_ice': '#9b59b6'     # Purple
        }
        
        # Sort data by date
        year_data = year_data.sort_values('date')
        dates = year_data['date']
        
        # =================================================================
        # SUBPLOT A: Monthly Albedo Analysis - HYBRID (Box plots + Stacked bars)
        # =================================================================
        ax1 = axes[0]
        self._create_hybrid_albedo_analysis(ax1, year, year_data, modern_colors)
        
        # =================================================================
        # SUBPLOT B: Daily Pixel Count Composition - STACKED BARS
        # =================================================================
        ax2 = axes[1]
        self._create_pixel_count_stacked_bars(ax2, year_data, modern_colors)
        
        # =================================================================
        # SUBPLOT C: Daily Quality Assessment Distribution - STACKED BARS
        # =================================================================
        ax3 = axes[2]
        self._create_qa_stacked_bars(ax3, year, pixel_analyzer, modern_colors)
        
        # =================================================================
        # FINAL FORMATTING AND LAYOUT
        # =================================================================
        
        # Add summary statistics text box
        stats_text = self._generate_year_summary_stats(year, year_data, pixel_analyzer)
        fig.text(0.02, 0.01, stats_text, fontsize=10, 
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                         edgecolor='lightgray', alpha=0.95))
        
        # Adjust layout with proper spacing for vertical stack
        plt.tight_layout(rect=[0.0, 0.08, 1.0, 0.96])
        
        # Apply consistent date formatting to all x-axes with weekly intervals
        for ax in axes:
            # Dates par semaine (tous les 7 jours)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            locator = mdates.WeekdayLocator(interval=1)  # Toutes les semaines
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_minor_locator(mdates.DayLocator(interval=3))      # Marques mineures tous les 3 jours
            ax.tick_params(axis='x', rotation=45, labelsize=11)
            ax.tick_params(axis='y', labelsize=12)
            # Améliorer l'espacement des étiquettes
            plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
            
            # Ajouter des lignes verticales légères aux positions des dates principales
            ax.grid(True, which='major', axis='x', alpha=0.3, linestyle='-', linewidth=0.8, color='gray')
            ax.grid(True, which='minor', axis='x', alpha=0.15, linestyle=':', linewidth=0.5, color='lightgray')
            # Garder la grille horizontale existante
            ax.grid(True, which='major', axis='y', alpha=0.4, linestyle=':', linewidth=0.8)
        
        # Create directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
        
        # Save the plot with high quality
        save_path = os.path.join(save_dir, f'daily_melt_season_{year}{dataset_suffix}.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        print(f"✅ Enhanced daily plot for {year} saved: {save_path}")
        
        plt.close()
        return save_path
    
    def _create_hybrid_albedo_analysis(self, ax, year, year_data, modern_colors):
        """
        Crée des barres empilées quotidiennes d'albédo avec couleurs plus douces
        
        Args:
            ax: Matplotlib axes object
            year: Année analysée
            year_data: Données pour cette année
            modern_colors: Palette de couleurs (sera remplacée par des couleurs plus douces)
        """
        print(f"🎨 Création des barres empilées quotidiennes d'albédo pour {year}...")
        
        # Utiliser la palette de couleurs moderne originale
        colors_to_use = modern_colors
        
        # Préparer les données pour barres empilées - contribution pondérée d'albédo
        albedo_data = {}
        valid_dates = []
        
        for _, row in year_data.iterrows():
            date = row['date']
            day_albedo = {}
            
            # Get albedo and pixel count for each fraction
            total_pixels = 0
            for fraction in self.fraction_classes:
                mean_col = f"{fraction}_mean"
                pixel_col = f"{fraction}_pixel_count"
                
                if (mean_col in row.index and pixel_col in row.index and 
                    pd.notna(row[mean_col]) and pd.notna(row[pixel_col]) and 
                    row[pixel_col] > 0):
                    
                    albedo_value = row[mean_col]
                    pixel_count = row[pixel_col]
                    
                    # Weighted albedo contribution
                    day_albedo[fraction] = albedo_value * (pixel_count / 100.0)  # Normalized
                    total_pixels += pixel_count
            
            # Only include days with valid albedo data
            if day_albedo and total_pixels > 0:
                valid_dates.append(date)
                
                for fraction in self.fraction_classes:
                    if fraction not in albedo_data:
                        albedo_data[fraction] = []
                    
                    if fraction in day_albedo:
                        albedo_data[fraction].append(day_albedo[fraction])
                    else:
                        albedo_data[fraction].append(0)
        
        if valid_dates and albedo_data:
            # Create stacked bars for albedo contributions
            bottom_values = np.zeros(len(valid_dates))
            width = 1.0  # Full width bars for daily data
            
            for fraction in self.fraction_classes:
                if fraction in albedo_data and len(albedo_data[fraction]) == len(valid_dates):
                    values = np.array(albedo_data[fraction])
                    
                    ax.bar(valid_dates, values, width, bottom=bottom_values,
                           label=f'{self.class_labels[fraction]}',
                           color=colors_to_use.get(fraction, '#7f8c8d'),
                           alpha=0.8, edgecolor='white', linewidth=0.5)
                    
                    bottom_values += values
            
            ax.set_title('A) Daily Albedo Composition (Stacked by Ice Coverage Fraction)', 
                         fontsize=16, fontweight='bold', pad=15)
            ax.set_ylabel('Weighted Albedo', fontsize=14, fontweight='bold')
            ax.set_ylim(0, max(bottom_values) * 1.1 if len(bottom_values) > 0 else 1)
            ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, 
                      fontsize=11, ncol=2)
            ax.set_facecolor('#fafafa')
            
            print(f"✅ Panel A: Barres empilées d'albédo quotidiennes pour {len(valid_dates)} jours")
        else:
            ax.text(0.5, 0.5, 'No albedo data available for this year', 
                    ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('A) Daily Albedo Composition (No Data)', 
                         fontsize=16, fontweight='bold', pad=15)
    
    def _create_pixel_count_stacked_bars(self, ax, year_data, modern_colors):
        """Create stacked bars for pixel count composition"""
        # Prepare data for stacked pixel count bars
        pixel_data = {}
        pixel_valid_dates = []
        
        for _, row in year_data.iterrows():
            date = row['date']
            day_pixels = {}
            
            # Get pixel count for each fraction
            for fraction in self.fraction_classes:
                pixel_col = f"{fraction}_pixel_count"
                
                if pixel_col in row.index and pd.notna(row[pixel_col]) and row[pixel_col] > 0:
                    day_pixels[fraction] = row[pixel_col]
            
            # Only include days with pixel data
            if day_pixels:
                pixel_valid_dates.append(date)
                
                for fraction in self.fraction_classes:
                    if fraction not in pixel_data:
                        pixel_data[fraction] = []
                    
                    if fraction in day_pixels:
                        pixel_data[fraction].append(day_pixels[fraction])
                    else:
                        pixel_data[fraction].append(0)
        
        if pixel_valid_dates and pixel_data:
            # Create stacked bars for pixel counts
            bottom_values = np.zeros(len(pixel_valid_dates))
            width = 1.0  # Full width bars for daily data
            
            for fraction in self.fraction_classes:
                if fraction in pixel_data and len(pixel_data[fraction]) == len(pixel_valid_dates):
                    values = np.array(pixel_data[fraction])
                    
                    ax.bar(pixel_valid_dates, values, width, bottom=bottom_values,
                           label=f'{self.class_labels[fraction]}',
                           color=modern_colors.get(fraction, '#7f8c8d'),
                           alpha=0.8, edgecolor='white', linewidth=0.5)
                    
                    bottom_values += values
            
            ax.set_title('B) Daily Pixel Count Composition (Stacked by Ice Coverage Fraction)', 
                         fontsize=16, fontweight='bold', pad=15)
            ax.set_ylabel('Number of Pixels', fontsize=14, fontweight='bold')
            ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, 
                      fontsize=11, ncol=2)
            ax.grid(True, alpha=0.4, linestyle=':', linewidth=0.8, axis='y')
            ax.set_facecolor('#fafafa')
            
            print(f"✅ Panel B: Stacked pixel count bars for {len(pixel_valid_dates)} days")
        else:
            ax.text(0.5, 0.5, 'No pixel count data available for this year', 
                    ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('B) Daily Pixel Count Composition (No Data)', 
                         fontsize=16, fontweight='bold', pad=15)
    
    def _create_qa_stacked_bars(self, ax, year, pixel_analyzer, modern_colors):
        """Create stacked bars for QA distribution"""
        qa_plotted = False
        
        # Enhanced QA color scheme with better contrast
        qa_colors = ['#27ae60', '#3498db', '#f39c12', '#e74c3c']  # Green, Blue, Orange, Red
        qa_labels = ['QA 0 (Excellent)', 'QA 1 (Good)', 'QA 2 (Fair)', 'QA 3 (Poor)']
        qa_columns = ['quality_0_best', 'quality_1_good', 'quality_2_moderate', 'quality_3_poor']
        
        # Try to plot QA data if available
        if pixel_analyzer.qa_data is not None:
            year_qa_data = pixel_analyzer.qa_data[
                pixel_analyzer.qa_data['year'] == year
            ].copy()
            
            if len(year_qa_data) > 0:
                year_qa_data = year_qa_data.sort_values('date')
                
                # Prepare data for stacked bars
                qa_valid_dates = []
                qa_stacked_data = {qa_col: [] for qa_col in qa_columns}
                
                for _, row in year_qa_data.iterrows():
                    has_data = False
                    for qa_col in qa_columns:
                        if qa_col in year_qa_data.columns and pd.notna(row[qa_col]) and row[qa_col] > 0:
                            has_data = True
                            break
                    
                    if has_data:
                        qa_valid_dates.append(row['date'])
                        for qa_col in qa_columns:
                            value = row[qa_col] if qa_col in year_qa_data.columns and pd.notna(row[qa_col]) else 0
                            qa_stacked_data[qa_col].append(max(0, value))
                
                if qa_valid_dates:
                    # Create stacked bars
                    width = pd.Timedelta(days=1)  # Bar width
                    bottom_values = np.zeros(len(qa_valid_dates))
                    
                    for i, (qa_col, qa_label, qa_color) in enumerate(zip(qa_columns, qa_labels, qa_colors)):
                        values = qa_stacked_data[qa_col]
                        if any(v > 0 for v in values):
                            ax.bar(qa_valid_dates, values, width, bottom=bottom_values,
                                   label=f'{qa_label}',
                                   color=qa_color, alpha=0.8, edgecolor='white', linewidth=0.5)
                            bottom_values += np.array(values)
                    
                    qa_plotted = True
                    print(f"✅ Panel C: Stacked QA distribution bars for {len(qa_valid_dates)} days")
        
        if qa_plotted:
            ax.set_title('C) Daily Quality Assessment Distribution (Stacked Bars)', 
                         fontsize=16, fontweight='bold', pad=15)
            ax.set_ylabel('Number of Pixels', fontsize=14, fontweight='bold')
            ax.set_xlabel('Date', fontsize=14, fontweight='bold')
            ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, 
                      fontsize=11, ncol=2)
            ax.grid(True, alpha=0.4, linestyle=':', linewidth=0.8, axis='y')
            ax.set_facecolor('#fafafa')
        else:
            ax.text(0.5, 0.5, 'No quality assessment data available for this year', 
                    ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('C) Daily Quality Assessment Distribution (Not Available)', 
                         fontsize=16, fontweight='bold', pad=15)
            ax.set_xlabel('Date', fontsize=14, fontweight='bold')