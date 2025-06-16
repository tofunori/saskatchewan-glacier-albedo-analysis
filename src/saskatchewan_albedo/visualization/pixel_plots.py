"""
Pixel Count and QA Visualizations for Saskatchewan Glacier
=========================================================

This module creates comprehensive visualizations for pixel counts,
data quality statistics, and availability patterns.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from scipy.interpolate import make_interp_spline

# Import from parent package
from ..config import (FRACTION_CLASSES, CLASS_LABELS, MONTH_NAMES, FRACTION_COLORS,
                      PLOT_STYLES, OUTPUT_DIR)
from ..utils.helpers import print_section_header, ensure_directory_exists


class PixelVisualizer:
    """
    Visualizer for pixel count and QA statistics
    """
    
    def __init__(self, data_handler):
        """
        Initialize the pixel visualizer
        
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
            day_contributions = {}
            total_weighted_albedo = 0
            total_pixels = 0
            
            # Calculer la contribution pondérée de chaque fraction
            for fraction in self.fraction_classes:
                albedo_col = f"{fraction}_mean"
                pixel_col = f"{fraction}_pixel_count"
                
                if (albedo_col in row.index and pixel_col in row.index and 
                    pd.notna(row[albedo_col]) and pd.notna(row[pixel_col]) and row[pixel_col] > 0):
                    
                    # Pondérer l'albédo par le nombre de pixels
                    weighted_contribution = row[albedo_col] * row[pixel_col]
                    day_contributions[fraction] = weighted_contribution
                    total_weighted_albedo += weighted_contribution
                    total_pixels += row[pixel_col]
            
            # N'inclure que les jours avec des données
            if day_contributions and total_pixels > 0:
                valid_dates.append(date)
                # Normaliser les contributions pour obtenir l'albédo proportionnel
                for fraction in day_contributions:
                    if fraction not in albedo_data:
                        albedo_data[fraction] = []
                    albedo_data[fraction].append(day_contributions[fraction] / total_pixels)
                
                # Remplir les fractions manquantes avec 0
                for fraction in self.fraction_classes:
                    if fraction not in day_contributions:
                        if fraction not in albedo_data:
                            albedo_data[fraction] = []
                        albedo_data[fraction].append(0)
        
        if valid_dates and albedo_data:
            # Créer les barres empilées
            bottom_values = np.zeros(len(valid_dates))
            width = 1.0  # Largeur complète pour les données quotidiennes
            
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
        
    def create_monthly_pixel_count_plots(self, pixel_results, save_path=None):
        """
        Create comprehensive monthly pixel count visualizations
        
        Args:
            pixel_results (dict): Results from PixelCountAnalyzer.analyze_monthly_pixel_counts()
            save_path (str, optional): Path to save the plot
            
        Returns:
            str: Path to saved plot
        """
        print_section_header("Création des graphiques de comptages de pixels", level=2)
        
        monthly_stats = pixel_results['summary_dataframe']
        
        if monthly_stats.empty:
            print("❌ Pas de données pour créer les graphiques de pixels")
            return None
        
        # Create figure with 4 subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Statistiques de Comptages de Pixels par Mois et Fraction', 
                     fontsize=16, fontweight='bold', y=0.98)
        
        # Plot 1: Average pixel counts by month and fraction
        self._plot_average_pixel_counts(axes[0, 0], monthly_stats)
        
        # Plot 2: Total pixel counts (stacked bar)
        self._plot_total_pixel_counts(axes[0, 1], monthly_stats)
        
        # Plot 3: Pixel count variability (std dev)
        self._plot_pixel_variability(axes[1, 0], monthly_stats)
        
        # Plot 4: Observation counts per month
        self._plot_observation_counts(axes[1, 1], monthly_stats)
        
        plt.tight_layout()
        
        # Save the plot
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, 'pixel_counts_by_month_fraction.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Graphiques de pixels sauvegardés: {save_path}")
        
        plt.close()
        return save_path
    
    def create_qa_statistics_plots(self, qa_results, save_path=None):
        """
        Create QA statistics visualizations by melt season
        
        Args:
            qa_results (dict): Results from PixelCountAnalyzer.analyze_true_qa_statistics() or analyze_seasonal_qa_statistics()
            save_path (str, optional): Path to save the plot
            
        Returns:
            str: Path to saved plot
        """
        print_section_header("Création des graphiques de qualité des données", level=2)
        
        qa_stats = qa_results['qa_dataframe']
        
        if qa_stats.empty:
            print("❌ Pas de données QA pour créer les graphiques")
            return None
        
        # Check if this is true QA data (0-3 scores) or seasonal QA data (by fraction)
        has_qa_score_column = 'qa_score' in qa_stats.columns
        
        if has_qa_score_column:
            # This is true QA data (0-3 scores) - use the true_qa_plots logic
            print("🔍 Utilisation des données QA vraies (scores 0-3)")
            
            # Create figure with 4 subplots optimized for QA scores
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Statistiques QA par Scores (0-3) - Saison de Fonte', 
                         fontsize=16, fontweight='bold', y=0.98)
            
            # Plot 1: QA scores distribution by month
            self._plot_qa_scores_distribution(axes[0, 0], qa_stats)
            
            # Plot 2: QA stacked bars
            self._plot_qa_stacked_bars(axes[0, 1], qa_stats)
            
            # Plot 3: QA trends by month
            self._plot_qa_trends_by_month(axes[1, 0], qa_stats)
            
            # Plot 4: QA quality ratios heatmap
            self._plot_qa_quality_heatmap(axes[1, 1], qa_results)
            
        else:
            # This is seasonal QA data (by fraction) - use the original logic
            print("🔍 Utilisation des données QA saisonnières (par fraction)")
            
            # Create figure with 4 subplots
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Statistiques de Qualité des Données par Saison de Fonte', 
                         fontsize=16, fontweight='bold', y=0.98)
            
            # Plot 1: QA scores by month and fraction
            self._plot_qa_scores(axes[0, 0], qa_stats)
            
            # Plot 2: High quality data ratios
            self._plot_quality_ratios(axes[0, 1], qa_stats)
            
            # Plot 3: Pixel availability patterns
            self._plot_pixel_availability(axes[1, 0], qa_stats)
            
            # Plot 4: QA distribution heatmap
            self._plot_qa_heatmap(axes[1, 1], qa_stats)
        
        plt.tight_layout()
        
        # Save the plot
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, 'qa_statistics_by_season.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Graphiques QA sauvegardés: {save_path}")
        
        plt.close()
        return save_path
    
    def create_pixel_availability_heatmap(self, pixel_results, qa_results, save_path=None):
        """
        Create a heatmap showing pixel availability across months and fractions
        
        Args:
            pixel_results (dict): Pixel count analysis results
            qa_results (dict): QA analysis results
            save_path (str, optional): Path to save the plot
            
        Returns:
            str: Path to saved plot
        """
        print_section_header("Création de la heatmap de disponibilité des pixels", level=2)
        
        qa_stats = qa_results['qa_dataframe']
        
        # Create availability matrix
        availability_matrix = qa_stats.pivot_table(
            index='fraction_label',
            columns='month_name',
            values='pixel_availability',
            aggfunc='first'
        )
        
        # Ensure correct month order
        month_order = ['Juin', 'Juillet', 'Août', 'Septembre']
        available_months = [m for m in month_order if m in availability_matrix.columns]
        availability_matrix = availability_matrix.reindex(columns=available_months)
        
        # Create the heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        
        im = sns.heatmap(availability_matrix, 
                        annot=True, 
                        fmt='.1%',
                        cmap='RdYlGn',
                        vmin=0, vmax=1,
                        cbar_kws={'label': 'Disponibilité des Pixels'},
                        ax=ax)
        
        ax.set_title('Disponibilité des Pixels par Fraction et Mois', 
                    fontweight='bold', fontsize=14)
        ax.set_xlabel('Mois')
        ax.set_ylabel('Fraction de Couverture')
        
        plt.tight_layout()
        
        # Save the plot
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, 'pixel_availability_heatmap.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Heatmap de disponibilité sauvegardée: {save_path}")
        
        plt.close()
        return save_path
    
    def create_total_pixels_timeseries(self, total_pixel_results, save_path=None):
        """
        Create time series plot of total valid pixels
        
        Args:
            total_pixel_results (dict): Results from analyze_total_pixel_trends()
            save_path (str, optional): Path to save the plot
            
        Returns:
            str: Path to saved plot
        """
        print_section_header("Création du graphique temporel des pixels totaux", level=2)
        
        if 'time_series' not in total_pixel_results:
            print("❌ Pas de données temporelles pour les pixels totaux")
            return None
        
        time_data = total_pixel_results['time_series']
        
        # Create figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle('Évolution Temporelle des Pixels Valides Totaux', 
                     fontsize=16, fontweight='bold')
        
        # Plot 1: Time series
        ax1.plot(time_data['date'], time_data['total_valid_pixels'], 
                'b-', alpha=0.7, linewidth=1, label='Pixels quotidiens')
        
        # Add monthly averages
        monthly_avg = time_data.groupby([time_data['date'].dt.year, time_data['date'].dt.month])['total_valid_pixels'].mean()
        monthly_dates = pd.to_datetime([f"{year}-{month:02d}-15" for (year, month) in monthly_avg.index])
        ax1.plot(monthly_dates, monthly_avg.values, 'r-', linewidth=2, 
                marker='o', markersize=4, label='Moyennes mensuelles')
        
        ax1.set_title('Série Temporelle des Pixels Valides')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Nombre de Pixels Valides')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Seasonal patterns
        for month in [6, 7, 8, 9]:
            month_data = time_data[time_data['month'] == month]
            if not month_data.empty:
                ax2.scatter(month_data['year'], month_data['total_valid_pixels'], 
                           label=MONTH_NAMES[month], alpha=0.6, s=30)
        
        ax2.set_title('Patterns Saisonniers par Année')
        ax2.set_xlabel('Année')
        ax2.set_ylabel('Nombre de Pixels Valides')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Add trend info if available
        if 'overall_trend' in total_pixel_results:
            trend = total_pixel_results['overall_trend']
            ax1.text(0.02, 0.98, 
                    f"Tendance: {trend['slope_per_decade']:.0f} pixels/décennie\n"
                    f"Changement: {trend['relative_change']:.1f}%", 
                    transform=ax1.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        # Save the plot
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, 'total_pixels_timeseries.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Série temporelle sauvegardée: {save_path}")
        
        plt.close()
        return save_path
    
    def create_true_qa_plots(self, true_qa_results, save_path=None):
        """
        Create visualizations for true QA scores (0-3) by melt season
        
        Args:
            true_qa_results (dict): Results from analyze_true_qa_statistics()
            save_path (str, optional): Path to save the plot
            
        Returns:
            str: Path to saved plot
        """
        print_section_header("Création des graphiques des vrais scores QA (0-3)", level=2)
        
        if 'qa_dataframe' not in true_qa_results or true_qa_results['qa_dataframe'].empty:
            print("❌ Pas de données QA vraies pour créer les graphiques")
            return None
        
        qa_stats = true_qa_results['qa_dataframe']
        
        # Create figure with 4 subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Analyse des Scores de Qualité QA (0-3) par Saison de Fonte', 
                     fontsize=16, fontweight='bold', y=0.98)
        
        # Plot 1: QA scores distribution by month
        self._plot_qa_scores_distribution(axes[0, 0], qa_stats)
        
        # Plot 2: QA scores as stacked bars
        self._plot_qa_stacked_bars(axes[0, 1], qa_stats)
        
        # Plot 3: QA trends over months
        self._plot_qa_trends_by_month(axes[1, 0], qa_stats)
        
        # Plot 4: QA quality ratios heatmap
        self._plot_qa_quality_heatmap(axes[1, 1], true_qa_results)
        
        plt.tight_layout()
        
        # Save the plot
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, 'true_qa_scores_analysis.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Graphiques QA vrais sauvegardés: {save_path}")
        
        plt.close()
        return save_path
    
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
                    
                    ax2.bar(pixel_valid_dates, values, width, bottom=bottom_values,
                           label=f'{self.class_labels[fraction]}',
                           color=modern_colors.get(fraction, '#7f8c8d'),
                           alpha=0.8, edgecolor='white', linewidth=0.5)
                    
                    bottom_values += values
            
            ax2.set_title('B) Daily Pixel Count Composition (Stacked by Ice Coverage Fraction)', 
                         fontsize=16, fontweight='bold', pad=15)
            ax2.set_ylabel('Number of Pixels', fontsize=14, fontweight='bold')
            ax2.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, 
                      fontsize=11, ncol=2)
            ax2.grid(True, alpha=0.4, linestyle=':', linewidth=0.8, axis='y')
            ax2.set_facecolor('#fafafa')
            
            print(f"✅ Panel B: Stacked pixel count bars for {len(pixel_valid_dates)} days")
        else:
            ax2.text(0.5, 0.5, 'No pixel count data available for this year', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=14)
            ax2.set_title('B) Daily Pixel Count Composition (No Data)', 
                         fontsize=16, fontweight='bold', pad=15)
        
        # =================================================================
        # SUBPLOT C: Daily Quality Assessment Distribution - STACKED BARS
        # =================================================================
        ax3 = axes[2]
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
                            ax3.bar(qa_valid_dates, values, width, bottom=bottom_values,
                                   label=f'{qa_label}',
                                   color=qa_color, alpha=0.8, edgecolor='white', linewidth=0.5)
                            bottom_values += np.array(values)
                    
                    qa_plotted = True
                    print(f"✅ Panel C: Stacked QA distribution bars for {len(qa_valid_dates)} days")
        
        if qa_plotted:
            ax3.set_title('C) Daily Quality Assessment Distribution (Stacked Bars)', 
                         fontsize=16, fontweight='bold', pad=15)
            ax3.set_ylabel('Number of Pixels', fontsize=14, fontweight='bold')
            ax3.set_xlabel('Date', fontsize=14, fontweight='bold')
            ax3.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, 
                      fontsize=11, ncol=2)
            ax3.grid(True, alpha=0.4, linestyle=':', linewidth=0.8, axis='y')
            ax3.set_facecolor('#fafafa')
        else:
            ax3.text(0.5, 0.5, 'No quality assessment data available for this year', 
                    ha='center', va='center', transform=ax3.transAxes, fontsize=14)
            ax3.set_title('C) Daily Quality Assessment Distribution (Not Available)', 
                         fontsize=16, fontweight='bold', pad=15)
            ax3.set_xlabel('Date', fontsize=14, fontweight='bold')
        
        
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
        import matplotlib.dates as mdates
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
    
    def plot_mod10a1_fraction_comparison(self, save_dir=None, year_filter=None):
        """
        Crée une comparaison directe entre toutes les fractions MOD10A1
        
        Args:
            save_dir (str, optional): Répertoire de sauvegarde
            year_filter (list, optional): Années à inclure (par défaut: toutes)
            
        Returns:
            list: Chemins des graphiques sauvegardés
        """
        print_section_header("Comparaison des fractions MOD10A1", level=2)
        
        if save_dir is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_dir = OUTPUT_DIR
        
        # Filtrer les données si nécessaire
        plot_data = self.data.copy()
        if year_filter:
            plot_data = plot_data[plot_data['year'].isin(year_filter)]
        
        # Filtrer pour la saison de fonte (juin-septembre)
        melt_data = plot_data[plot_data['month'].isin([6, 7, 8, 9])].copy()
        
        if len(melt_data) == 0:
            print("❌ Aucune donnée de saison de fonte disponible")
            return []
        
        print(f"📊 Données disponibles: {len(melt_data)} observations")
        print(f"📅 Période: {melt_data['year'].min()}-{melt_data['year'].max()}")
        
        saved_plots = []
        
        # 1. Graphique temporel - Comparaison toutes fractions
        saved_plots.append(self._create_fraction_timeseries_comparison(melt_data, save_dir))
        
        # 2. Graphique de corrélation entre fractions
        saved_plots.append(self._create_fraction_correlation_matrix(melt_data, save_dir))
        
        # 3. Graphique de distribution par mois
        saved_plots.append(self._create_fraction_monthly_distribution(melt_data, save_dir))
        
        # 4. Graphique de tendances par fraction
        saved_plots.append(self._create_fraction_trend_comparison(melt_data, save_dir))
        
        # 5. Statistiques détaillées
        self._export_fraction_statistics(melt_data, save_dir)
        
        print(f"\n✅ {len([p for p in saved_plots if p])} graphiques de comparaison créés")
        return [p for p in saved_plots if p]
    
    def _create_fraction_timeseries_comparison(self, data, save_dir):
        """Série temporelle comparant toutes les fractions"""
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Couleurs modernes pour chaque fraction
        fraction_colors = {
            'border': '#e74c3c',      # Rouge
            'mixed_low': '#f39c12',   # Orange
            'mixed_high': '#2ecc71',  # Vert
            'mostly_ice': '#3498db',  # Bleu
            'pure_ice': '#9b59b6'     # Violet
        }
        
        # Plot chaque fraction
        for fraction in self.fraction_classes:
            mean_col = f"{fraction}_mean"
            pixel_col = f"{fraction}_pixel_count"
            
            if mean_col in data.columns:
                # Filtrer les données valides
                valid_data = data[
                    (data[mean_col].notna()) & 
                    (data[mean_col] > 0) &
                    (data[pixel_col].fillna(0) > 0)
                ].copy()
                
                if len(valid_data) > 0:
                    # Scatter plot avec transparence
                    ax.scatter(valid_data['date'], valid_data[mean_col],
                             label=f'{self.class_labels[fraction]} ({len(valid_data)} pts)',
                             color=fraction_colors[fraction], alpha=0.7, s=25,
                             edgecolors='white', linewidth=0.5)
        
        ax.set_title('MOD10A1 Daily Albedo Comparison - All Fractions\nMelt Season Observations (June-September)', 
                    fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=14, fontweight='bold')
        ax.set_ylabel('Albedo', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True, fontsize=11)
        ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
        ax.set_facecolor('#fafafa')
        
        # Formater les dates
        import matplotlib.dates as mdates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # Sauvegarder
        save_path = os.path.join(save_dir, 'mod10a1_fraction_timeseries_comparison.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✓ Série temporelle fractions sauvegardée: {save_path}")
        plt.close()
        
        return save_path
    
    def _create_fraction_correlation_matrix(self, data, save_dir):
        """Matrice de corrélation entre fractions"""
        import numpy as np
        import seaborn as sns
        
        # Préparer les données de corrélation
        fraction_data = {}
        for fraction in self.fraction_classes:
            mean_col = f"{fraction}_mean"
            if mean_col in data.columns:
                valid_values = data[data[mean_col].notna()][mean_col]
                if len(valid_values) > 10:
                    fraction_data[self.class_labels[fraction]] = valid_values
        
        if len(fraction_data) < 2:
            print("⚠️ Données insuffisantes pour la matrice de corrélation")
            return None
        
        # Créer DataFrame pour corrélation
        import pandas as pd
        
        # Aligner les données par date
        aligned_data = {}
        for fraction_name, values in fraction_data.items():
            fraction_key = [k for k, v in self.class_labels.items() if v == fraction_name][0]
            mean_col = f"{fraction_key}_mean"
            fraction_df = data[data[mean_col].notna()][['date', mean_col]].copy()
            fraction_df = fraction_df.rename(columns={mean_col: fraction_name})
            aligned_data[fraction_name] = fraction_df.set_index('date')
        
        # Merger toutes les fractions
        corr_df = aligned_data[list(aligned_data.keys())[0]]
        for frac_name in list(aligned_data.keys())[1:]:
            corr_df = corr_df.join(aligned_data[frac_name], how='outer')
        
        # Calculer la matrice de corrélation
        correlation_matrix = corr_df.corr()
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Heatmap avec annotations
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        sns.heatmap(correlation_matrix, mask=mask, annot=True, fmt='.3f', 
                   cmap='RdBu_r', center=0, square=True, cbar_kws={'shrink': 0.8},
                   annot_kws={'fontsize': 11, 'fontweight': 'bold'})
        
        ax.set_title('MOD10A1 Inter-Fraction Correlation Matrix\nPearson Correlation Coefficients', 
                    fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # Sauvegarder
        save_path = os.path.join(save_dir, 'mod10a1_fraction_correlation_matrix.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✓ Matrice de corrélation sauvegardée: {save_path}")
        plt.close()
        
        return save_path
    
    def _create_fraction_monthly_distribution(self, data, save_dir):
        """Distribution des valeurs d'albédo par mois et fraction"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('MOD10A1 Monthly Albedo Distribution by Fraction\nMelt Season Analysis', 
                    fontsize=18, fontweight='bold', y=0.98)
        
        months = [6, 7, 8, 9]
        month_names = ['June', 'July', 'August', 'September']
        colors = ['#3498db', '#e74c3c', '#f39c12', '#2ecc71']
        
        for i, (month, month_name, color) in enumerate(zip(months, month_names, colors)):
            ax = axes[i // 2, i % 2]
            month_data = data[data['month'] == month]
            
            # Box plots pour chaque fraction
            box_data = []
            labels = []
            
            for fraction in self.fraction_classes:
                mean_col = f"{fraction}_mean"
                if mean_col in month_data.columns:
                    values = month_data[month_data[mean_col].notna()][mean_col]
                    if len(values) > 5:
                        box_data.append(values)
                        labels.append(f'{self.class_labels[fraction]}\n(n={len(values)})')
            
            if box_data:
                bp = ax.boxplot(box_data, labels=labels, patch_artist=True)
                
                # Colorer les boîtes
                fraction_colors = ['#e74c3c', '#f39c12', '#2ecc71', '#3498db', '#9b59b6']
                for patch, fcolor in zip(bp['boxes'], fraction_colors[:len(box_data)]):
                    patch.set_facecolor(fcolor)
                    patch.set_alpha(0.7)
            
            ax.set_title(f'{month_name} ({month:02d})', fontsize=14, fontweight='bold')
            ax.set_ylabel('Albedo', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', rotation=45, labelsize=10)
        
        plt.tight_layout()
        
        # Sauvegarder
        save_path = os.path.join(save_dir, 'mod10a1_fraction_monthly_distribution.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✓ Distribution mensuelle sauvegardée: {save_path}")
        plt.close()
        
        return save_path
    
    def _create_fraction_trend_comparison(self, data, save_dir):
        """Comparaison des tendances par fraction"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Calculer les tendances annuelles pour chaque fraction
        trends = {}
        colors = ['#e74c3c', '#f39c12', '#2ecc71', '#3498db', '#9b59b6']
        
        for i, fraction in enumerate(self.fraction_classes):
            mean_col = f"{fraction}_mean"
            if mean_col in data.columns:
                # Grouper par année et calculer la moyenne
                annual_means = data.groupby('year')[mean_col].mean().dropna()
                
                if len(annual_means) >= 3:
                    years = annual_means.index.values
                    values = annual_means.values
                    
                    # Calculer la tendance linéaire
                    z = np.polyfit(years, values, 1)
                    trend_line = np.poly1d(z)
                    
                    # Plot les données et la tendance
                    ax.scatter(years, values, label=f'{self.class_labels[fraction]}',
                             color=colors[i], s=40, alpha=0.8, zorder=5)
                    ax.plot(years, trend_line(years), color=colors[i], 
                           linestyle='--', alpha=0.8, linewidth=2)
                    
                    # Stocker les infos de tendance
                    slope_per_decade = z[0] * 10
                    trends[fraction] = {
                        'slope': z[0],
                        'slope_per_decade': slope_per_decade,
                        'intercept': z[1],
                        'label': self.class_labels[fraction]
                    }
        
        ax.set_title('MOD10A1 Annual Albedo Trends by Fraction\nMelt Season Averages with Linear Trends', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Year', fontsize=14, fontweight='bold')
        ax.set_ylabel('Mean Albedo', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
        ax.set_facecolor('#fafafa')
        
        # Ajouter texte avec les tendances
        trend_text = "Trends (per decade):\\n"
        for fraction, trend_info in trends.items():
            direction = "↗" if trend_info['slope_per_decade'] > 0 else "↘"
            trend_text += f"{direction} {trend_info['label']}: {trend_info['slope_per_decade']:+.4f}\\n"
        
        ax.text(0.02, 0.98, trend_text, transform=ax.transAxes, 
               fontsize=11, verticalalignment='top',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                        edgecolor='lightgray', alpha=0.95))
        
        plt.tight_layout()
        
        # Sauvegarder
        save_path = os.path.join(save_dir, 'mod10a1_fraction_trend_comparison.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✓ Comparaison des tendances sauvegardée: {save_path}")
        plt.close()
        
        return save_path
    
    def _export_fraction_statistics(self, data, save_dir):
        """Exporter les statistiques détaillées"""
        stats_data = []
        
        for fraction in self.fraction_classes:
            mean_col = f"{fraction}_mean"
            pixel_col = f"{fraction}_pixel_count"
            
            if mean_col in data.columns:
                valid_data = data[data[mean_col].notna()]
                
                if len(valid_data) > 0:
                    values = valid_data[mean_col]
                    pixels = valid_data[pixel_col].fillna(0)
                    
                    stats = {
                        'fraction': self.class_labels[fraction],
                        'fraction_code': fraction,
                        'n_observations': len(values),
                        'mean_albedo': values.mean(),
                        'median_albedo': values.median(),
                        'std_albedo': values.std(),
                        'min_albedo': values.min(),
                        'max_albedo': values.max(),
                        'mean_pixels': pixels.mean(),
                        'total_pixels': pixels.sum(),
                        'years_covered': len(valid_data['year'].unique()),
                        'first_observation': valid_data['date'].min(),
                        'last_observation': valid_data['date'].max()
                    }
                    
                    stats_data.append(stats)
        
        # Sauvegarder les statistiques
        import pandas as pd
        stats_df = pd.DataFrame(stats_data)
        
        if not stats_df.empty:
            stats_path = os.path.join(save_dir, 'mod10a1_fraction_statistics.csv')
            stats_df.to_csv(stats_path, index=False)
            print(f"✓ Statistiques détaillées exportées: {stats_path}")
            
            return stats_path
        
        return None

