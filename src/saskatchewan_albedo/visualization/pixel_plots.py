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
    
    def create_daily_melt_season_plots(self, pixel_analyzer, save_dir=None):
        """
        Create daily QA and pixel count plots for each year's melt season
        
        Args:
            pixel_analyzer: PixelCountAnalyzer instance with loaded data
            save_dir (str, optional): Directory to save the plots
            
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
            plot_path = self._create_yearly_daily_plot(year, year_data, pixel_analyzer, save_dir)
            if plot_path:
                saved_plots.append(plot_path)
        
        print(f"\n✅ {len(saved_plots)} graphiques annuels créés")
        return saved_plots
    
    def _create_yearly_daily_plot(self, year, year_data, pixel_analyzer, save_dir):
        """
        Create daily plot for a specific year's melt season
        
        Args:
            year (int): Year to plot
            year_data (pd.DataFrame): Data for this year
            pixel_analyzer: PixelCountAnalyzer instance
            save_dir (str): Directory to save the plot
            
        Returns:
            str: Path to saved plot
        """
        # Create figure with 2x2 subplots: albedo, pixel counts, QA scores, and total pixels
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        fig.suptitle(f'Daily Analysis for Melt Season {year}', 
                     fontsize=18, fontweight='bold', y=0.95)
        
        # Sort data by date
        year_data = year_data.sort_values('date')
        dates = year_data['date']
        
        # Plot A: Daily albedo values by fraction (top-left)
        ax1 = axes[0, 0]
        for fraction in self.fraction_classes:
            albedo_col = f"{fraction}_mean"
            if albedo_col in year_data.columns:
                albedo_data = year_data[albedo_col].dropna()
                if len(albedo_data) > 0:
                    ax1.plot(year_data['date'], year_data[albedo_col], 
                            marker='o', markersize=4, linewidth=2, alpha=0.8,
                            label=self.class_labels[fraction],
                            color=self.academic_colors.get(fraction, 'gray'))
        
        ax1.set_title('A) Daily Albedo Values by Ice Coverage Fraction', fontweight='bold', pad=20)
        ax1.set_xlabel('Date', fontsize=12)
        ax1.set_ylabel('Albedo', fontsize=12)
        ax1.set_ylim(0, 1)  # Albedo ranges from 0 to 1
        ax1.legend(loc='upper right', frameon=True, fancybox=True, shadow=True, fontsize=10)
        ax1.grid(True, alpha=0.3, linestyle='--')
        
        # Plot B: Daily pixel counts by fraction (top-right)
        ax2 = axes[0, 1]
        for fraction in self.fraction_classes:
            pixel_col = f"{fraction}_pixel_count"
            if pixel_col in year_data.columns:
                pixel_data = year_data[pixel_col].dropna()
                if len(pixel_data) > 0:
                    ax2.scatter(year_data['date'], year_data[pixel_col], 
                               s=35, alpha=0.7, 
                               label=self.class_labels[fraction],
                               color=self.academic_colors.get(fraction, 'gray'))
        
        ax2.set_title('B) Daily Pixel Counts by Ice Coverage Fraction', fontweight='bold', pad=20)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Number of Pixels', fontsize=12)
        ax2.legend(loc='upper right', frameon=True, fancybox=True, shadow=True, fontsize=10)
        ax2.grid(True, alpha=0.3, linestyle='--')
        
        # Plot C: Daily QA scores (absolute counts) (bottom-left)
        ax3 = axes[1, 0]
        qa_plotted = False
        
        # Try to plot QA data if available
        if pixel_analyzer.qa_data is not None:
            year_qa_data = pixel_analyzer.qa_data[
                pixel_analyzer.qa_data['year'] == year
            ].copy()
            
            if len(year_qa_data) > 0:
                year_qa_data = year_qa_data.sort_values('date')
                
                # Plot QA scores 0-3 with absolute counts (academic colors)
                qa_colors = ['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728']  # Green, Blue, Orange, Red
                qa_labels = ['QA 0 (Best)', 'QA 1 (Good)', 'QA 2 (Moderate)', 'QA 3 (Poor)']
                
                for i, qa_col in enumerate(['quality_0_best', 'quality_1_good', 'quality_2_moderate', 'quality_3_poor']):
                    if qa_col in year_qa_data.columns:
                        qa_data = year_qa_data[qa_col].dropna()
                        # Only plot if there are non-zero values (these are absolute counts now)
                        if len(qa_data) > 0 and qa_data.max() > 0:
                            ax3.scatter(year_qa_data['date'], year_qa_data[qa_col], 
                                       s=35, alpha=0.7, marker='s',
                                       label=qa_labels[i], color=qa_colors[i])
                            qa_plotted = True
        
        # If no QA data, plot data quality from main dataset
        if not qa_plotted:
            for fraction in self.fraction_classes:
                qa_col = f"{fraction}_data_quality"
                if qa_col in year_data.columns:
                    qa_data = year_data[qa_col].dropna()
                    if len(qa_data) > 0:
                        ax3.plot(year_data['date'], year_data[qa_col], 
                                marker='s', markersize=3, linewidth=1, alpha=0.7,
                                label=f"{self.class_labels[fraction]} QA",
                                color=FRACTION_COLORS.get(fraction, 'gray'))
                        qa_plotted = True
        
        if qa_plotted:
            ax3.set_title('C) Daily QA Score Distribution (Absolute Counts)', fontweight='bold', pad=20)
            ax3.set_xlabel('Date', fontsize=12)
            ax3.set_ylabel('Number of Pixels', fontsize=12)
            ax3.legend(loc='upper right', frameon=True, fancybox=True, shadow=True, fontsize=10)
            ax3.grid(True, alpha=0.3, linestyle='--')
        else:
            ax3.text(0.5, 0.5, 'Aucune donnée QA disponible pour cette année', 
                    ha='center', va='center', transform=ax3.transAxes, fontsize=12)
            ax3.set_title('C) Daily QA Score Distribution (Not Available)', fontweight='bold', pad=20)
        
        # Plot D: Total valid pixels over time (bottom-right)
        ax4 = axes[1, 1]
        if 'total_valid_pixels' in year_data.columns:
            ax4.scatter(year_data['date'], year_data['total_valid_pixels'], 
                       s=40, alpha=0.7, 
                       color='#1f77b4', label='Total Valid Pixels')
            
            # Add monthly averages
            monthly_avg = year_data.groupby(year_data['date'].dt.month)['total_valid_pixels'].mean()
            for month, avg_pixels in monthly_avg.items():
                month_data = year_data[year_data['date'].dt.month == month]
                if len(month_data) > 0:
                    ax4.axhline(y=avg_pixels, alpha=0.5, linestyle='--', 
                              label=f'Avg. {MONTH_NAMES[month]}: {avg_pixels:.0f}')
            
            ax4.set_title('D) Total Valid Pixels Over Time', fontweight='bold', pad=20)
            ax4.set_xlabel('Date', fontsize=12)
            ax4.set_ylabel('Total Number of Pixels', fontsize=12)
            ax4.legend(loc='upper right', frameon=True, fancybox=True, shadow=True, fontsize=10)
            ax4.grid(True, alpha=0.3, linestyle='--')
        else:
            ax4.text(0.5, 0.5, 'Données de pixels totaux non disponibles', 
                    ha='center', va='center', transform=ax4.transAxes, fontsize=12)
            ax4.set_title('D) Total Valid Pixels Over Time (Not Available)', fontweight='bold', pad=20)
        
        # Add summary statistics text box (repositioned for 2x2 layout)
        stats_text = self._generate_year_summary_stats(year, year_data, pixel_analyzer)
        fig.text(0.02, 0.01, stats_text, fontsize=9, 
                bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.9))
        
        # Adjust layout with proper spacing for 2x2 grid
        plt.tight_layout(rect=[0.0, 0.1, 1.0, 0.93])
        
        # Create directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
        
        # Save the plot
        save_path = os.path.join(save_dir, f'daily_melt_season_{year}.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Graphique {year} sauvegardé: {save_path}")
        
        plt.close()
        return save_path
    
    def _generate_year_summary_stats(self, year, year_data, pixel_analyzer):
        """
        Generate summary statistics text for a year
        
        Args:
            year (int): Year
            year_data (pd.DataFrame): Data for this year
            pixel_analyzer: PixelCountAnalyzer instance
            
        Returns:
            str: Summary statistics text
        """
        stats_lines = [f"📊 RÉSUMÉ {year}:"]
        
        # Basic statistics
        total_days = len(year_data)
        date_range = f"{year_data['date'].min().strftime('%Y-%m-%d')} à {year_data['date'].max().strftime('%Y-%m-%d')}"
        stats_lines.append(f"• {total_days} jours de données ({date_range})")
        
        # Pixel count statistics
        if 'total_valid_pixels' in year_data.columns:
            total_pixels = year_data['total_valid_pixels']
            avg_pixels = total_pixels.mean()
            stats_lines.append(f"• Moyenne pixels/jour: {avg_pixels:.0f}")
            stats_lines.append(f"• Range pixels: {total_pixels.min():.0f} - {total_pixels.max():.0f}")
        
        # Monthly breakdown
        monthly_counts = year_data['month'].value_counts().sort_index()
        month_summary = ", ".join([f"{MONTH_NAMES[m]}({count}j)" for m, count in monthly_counts.items()])
        stats_lines.append(f"• Répartition: {month_summary}")
        
        return "\n".join(stats_lines)
    
    def _plot_qa_scores_distribution(self, ax, qa_stats):
        """Plot QA scores distribution by month"""
        qa_colors = ['#2E8B57', '#4682B4', '#FF8C00', '#DC143C']  # Colors for QA 0,1,2,3
        qa_labels = ['QA 0 (Meilleur)', 'QA 1 (Bon)', 'QA 2 (Modéré)', 'QA 3 (Mauvais)']
        
        for i, qa_score in enumerate(['0', '1', '2', '3']):
            score_data = qa_stats[qa_stats['qa_score'] == qa_score]
            if not score_data.empty:
                ax.plot(score_data['year'], score_data['mean_count'], 
                       marker='o', linewidth=2, markersize=6,
                       label=qa_labels[i], color=qa_colors[i])
        
        ax.set_title('📊 Distribution des Comptages QA par Année', fontweight='bold')
        ax.set_xlabel('Année')
        ax.set_ylabel('Comptage Moyen (pixels)')
        ax.set_xticks(range(2010, 2025, 2))  # Show every 2 years to avoid crowding
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_qa_stacked_bars(self, ax, qa_stats):
        """Plot QA scores as stacked bars by year"""
        years = sorted(qa_stats['year'].unique())
        qa_colors = ['#2E8B57', '#4682B4', '#FF8C00', '#DC143C']
        qa_labels = ['QA 0 (Meilleur)', 'QA 1 (Bon)', 'QA 2 (Modéré)', 'QA 3 (Mauvais)']
        
        # Prepare data for stacking
        qa_data_by_year = {}
        for year in years:
            year_data = qa_stats[qa_stats['year'] == year]
            qa_data_by_year[year] = {}
            for qa_score in ['0', '1', '2', '3']:
                score_data = year_data[year_data['qa_score'] == qa_score]
                if not score_data.empty:
                    qa_data_by_year[year][qa_score] = score_data['mean_count'].iloc[0]
                else:
                    qa_data_by_year[year][qa_score] = 0
        
        # Create stacked bar chart
        bottom = np.zeros(len(years))
        for i, qa_score in enumerate(['0', '1', '2', '3']):
            values = [qa_data_by_year[year][qa_score] for year in years]
            ax.bar(years, values, bottom=bottom, 
                  label=qa_labels[i], color=qa_colors[i])
            bottom += values
        
        ax.set_title('📊 Répartition des Scores QA par Année (Empilés)', fontweight='bold')
        ax.set_xlabel('Année')
        ax.set_ylabel('Comptages de Pixels')
        ax.set_xticks(range(2010, 2025, 2))  # Show every 2 years
        ax.legend()
    
    def _plot_qa_trends_by_month(self, ax, qa_stats):
        """Plot QA trends by year with focus on best vs poor quality"""
        best_data = qa_stats[qa_stats['qa_score'] == '0']
        poor_data = qa_stats[qa_stats['qa_score'] == '3']
        
        if not best_data.empty:
            ax.plot(best_data['year'], best_data['mean_count'], 
                   marker='o', linewidth=3, markersize=8,
                   label='QA 0 (Meilleur)', color='#2E8B57')
        
        if not poor_data.empty:
            ax.plot(poor_data['year'], poor_data['mean_count'], 
                   marker='s', linewidth=3, markersize=8,
                   label='QA 3 (Mauvais)', color='#DC143C')
        
        ax.set_title('📈 Tendances QA: Meilleur vs Mauvais par Année', fontweight='bold')
        ax.set_xlabel('Année')
        ax.set_ylabel('Comptages (pixels)')
        ax.set_xticks(range(2010, 2025, 2))  # Show every 2 years
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_qa_quality_heatmap(self, ax, true_qa_results):
        """Plot QA quality counts as heatmap by year (absolute values)"""
        if 'by_month' not in true_qa_results:
            ax.text(0.5, 0.5, 'Pas de données QA\ndisponibles', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        # Prepare heatmap data with absolute counts by year
        heatmap_data = []
        years = []
        
        for year, year_data in true_qa_results['by_month'].items():
            if 'quality_counts' in year_data:
                counts = year_data['quality_counts']
                years.append(str(year))
                heatmap_data.append([
                    counts.get('quality_0_best', 0),
                    counts.get('quality_1_good', 0), 
                    counts.get('quality_2_moderate', 0),
                    counts.get('quality_3_poor', 0)
                ])
        
        if heatmap_data:
            heatmap_array = np.array(heatmap_data)
            
            # Use a color map suitable for count data
            im = ax.imshow(heatmap_array.T, cmap='Blues', aspect='auto')
            
            # Set labels
            ax.set_xticks(range(len(years)))
            ax.set_xticklabels(years, rotation=45)  # Rotate years for better readability
            ax.set_yticks(range(4))
            ax.set_yticklabels(['QA 0\n(Meilleur)', 'QA 1\n(Bon)', 'QA 2\n(Modéré)', 'QA 3\n(Mauvais)'])
            
            # Add text annotations with absolute counts
            for i in range(len(years)):
                for j in range(4):
                    count_val = heatmap_array[i, j]
                    if count_val > 0:
                        text = ax.text(i, j, f'{count_val:.0f}',
                                     ha="center", va="center", color="white" if count_val > heatmap_array.max()/2 else "black", 
                                     fontweight='bold')
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax, shrink=0.8)
            cbar.set_label('Comptages de Pixels')
            
            ax.set_title('🌡️ Heatmap des Comptages QA par Année', fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'Pas de données\nde comptages QA', 
                   ha='center', va='center', transform=ax.transAxes)
    
    def _plot_average_pixel_counts(self, ax, monthly_stats):
        """Plot average pixel counts by month and fraction"""
        for fraction in self.fraction_classes:
            fraction_data = monthly_stats[monthly_stats['fraction'] == fraction]
            if not fraction_data.empty:
                ax.plot(fraction_data['month'], fraction_data['mean'], 
                       marker='o', linewidth=2, markersize=6,
                       label=self.class_labels[fraction],
                       color=FRACTION_COLORS.get(fraction, 'gray'))
        
        ax.set_title('📊 Comptages Moyens de Pixels par Mois', fontweight='bold')
        ax.set_xlabel('Mois')
        ax.set_ylabel('Nombre Moyen de Pixels')
        ax.set_xticks([6, 7, 8, 9])
        ax.set_xticklabels(['Juin', 'Juillet', 'Août', 'Sept'])
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
    
    def _plot_total_pixel_counts(self, ax, monthly_stats):
        """Plot total pixel counts as stacked bars"""
        months = [6, 7, 8, 9]
        month_names = ['Juin', 'Juillet', 'Août', 'Sept']
        
        # Prepare data for stacking
        totals_by_month = {}
        for month in months:
            month_data = monthly_stats[monthly_stats['month'] == month]
            totals_by_month[month] = {}
            for fraction in self.fraction_classes:
                frac_data = month_data[month_data['fraction'] == fraction]
                if not frac_data.empty:
                    totals_by_month[month][fraction] = frac_data['total'].iloc[0]
                else:
                    totals_by_month[month][fraction] = 0
        
        # Create stacked bar chart
        bottom = np.zeros(len(months))
        for fraction in self.fraction_classes:
            values = [totals_by_month[month][fraction] for month in months]
            ax.bar(month_names, values, bottom=bottom, 
                  label=self.class_labels[fraction],
                  color=FRACTION_COLORS.get(fraction, 'gray'))
            bottom += values
        
        ax.set_title('📊 Comptages Totaux de Pixels (Empilés)', fontweight='bold')
        ax.set_xlabel('Mois')
        ax.set_ylabel('Nombre Total de Pixels')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    def _plot_pixel_variability(self, ax, monthly_stats):
        """Plot pixel count variability (standard deviation)"""
        for fraction in self.fraction_classes:
            fraction_data = monthly_stats[monthly_stats['fraction'] == fraction]
            if not fraction_data.empty:
                ax.plot(fraction_data['month'], fraction_data['std'], 
                       marker='s', linewidth=2, markersize=6,
                       label=self.class_labels[fraction],
                       color=FRACTION_COLORS.get(fraction, 'gray'),
                       linestyle='--')
        
        ax.set_title('📈 Variabilité des Comptages (Écart-type)', fontweight='bold')
        ax.set_xlabel('Mois')
        ax.set_ylabel('Écart-type des Pixels')
        ax.set_xticks([6, 7, 8, 9])
        ax.set_xticklabels(['Juin', 'Juillet', 'Août', 'Sept'])
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def _plot_observation_counts(self, ax, monthly_stats):
        """Plot number of observations per month"""
        obs_data = monthly_stats.groupby(['month', 'month_name'])['observations'].first().reset_index()
        
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(obs_data)))
        bars = ax.bar(obs_data['month_name'], obs_data['observations'], color=colors)
        
        ax.set_title('📊 Nombre d\'Observations par Mois', fontweight='bold')
        ax.set_xlabel('Mois')
        ax.set_ylabel('Nombre d\'Observations')
        
        # Add values on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
    
    def _plot_qa_scores(self, ax, qa_stats):
        """Plot QA scores by month and fraction"""
        for fraction in self.fraction_classes:
            fraction_data = qa_stats[qa_stats['fraction'] == fraction]
            if not fraction_data.empty:
                ax.plot(fraction_data['month'], fraction_data['qa_mean'], 
                       marker='o', linewidth=2, markersize=6,
                       label=self.class_labels[fraction],
                       color=FRACTION_COLORS.get(fraction, 'gray'))
        
        ax.set_title('📊 Scores de Qualité Moyens (%)', fontweight='bold')
        ax.set_xlabel('Mois')
        ax.set_ylabel('Score QA Moyen (%)')
        ax.set_xticks([6, 7, 8, 9])
        ax.set_xticklabels(['Juin', 'Juillet', 'Août', 'Sept'])
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 100])
    
    def _plot_quality_ratios(self, ax, qa_stats):
        """Plot high quality data ratios"""
        for fraction in self.fraction_classes:
            fraction_data = qa_stats[qa_stats['fraction'] == fraction]
            if not fraction_data.empty:
                ax.plot(fraction_data['month'], fraction_data['high_quality_ratio'] * 100, 
                       marker='o', linewidth=2, markersize=6,
                       label=self.class_labels[fraction],
                       color=FRACTION_COLORS.get(fraction, 'gray'))
        
        ax.set_title('📈 Proportion de Données Haute Qualité (%)', fontweight='bold')
        ax.set_xlabel('Mois')
        ax.set_ylabel('Haute Qualité (%)')
        ax.set_xticks([6, 7, 8, 9])
        ax.set_xticklabels(['Juin', 'Juillet', 'Août', 'Sept'])
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 100])
    
    def _plot_pixel_availability(self, ax, qa_stats):
        """Plot pixel availability patterns"""
        for fraction in self.fraction_classes:
            fraction_data = qa_stats[qa_stats['fraction'] == fraction]
            if not fraction_data.empty:
                ax.plot(fraction_data['month'], fraction_data['pixel_availability'] * 100, 
                       marker='s', linewidth=2, markersize=6,
                       label=self.class_labels[fraction],
                       color=FRACTION_COLORS.get(fraction, 'gray'),
                       linestyle='-.')
        
        ax.set_title('📊 Disponibilité des Pixels (%)', fontweight='bold')
        ax.set_xlabel('Mois')
        ax.set_ylabel('Disponibilité (%)')
        ax.set_xticks([6, 7, 8, 9])
        ax.set_xticklabels(['Juin', 'Juillet', 'Août', 'Sept'])
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 100])
    
    def _plot_qa_heatmap(self, ax, qa_stats):
        """Plot QA scores as heatmap"""
        qa_matrix = qa_stats.pivot_table(
            index='fraction_label',
            columns='month_name',
            values='qa_mean',
            aggfunc='first'
        )
        
        # Ensure correct month order
        month_order = ['Juin', 'Juillet', 'Août', 'Septembre']
        available_months = [m for m in month_order if m in qa_matrix.columns]
        qa_matrix = qa_matrix.reindex(columns=available_months)
        
        im = sns.heatmap(qa_matrix, 
                        annot=True, 
                        fmt='.1f',
                        cmap='RdYlGn',
                        vmin=0, vmax=100,
                        cbar_kws={'label': 'Score QA (%)'},
                        ax=ax)
        
        ax.set_title('🌡️ Heatmap des Scores QA', fontweight='bold')
        ax.set_xlabel('Mois')
        ax.set_ylabel('')