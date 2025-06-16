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
            qa_results (dict): Results from PixelCountAnalyzer.analyze_seasonal_qa_statistics()
            save_path (str, optional): Path to save the plot
            
        Returns:
            str: Path to saved plot
        """
        print_section_header("Création des graphiques de qualité des données", level=2)
        
        qa_stats = qa_results['qa_dataframe']
        
        if qa_stats.empty:
            print("❌ Pas de données QA pour créer les graphiques")
            return None
        
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
        # Create figure with combined albedo and melt season data
        fig, ax1 = plt.subplots(1, 1, figsize=(16, 10))
        fig.suptitle(f'Saison de Fonte {year} - Albédo Quotidien et Données de Pixels Combinés', 
                     fontsize=16, fontweight='bold')
        
        # Sort data by date
        year_data = year_data.sort_values('date')
        dates = year_data['date']
        
        # Primary axis (left): Daily albedo values by fraction
        ax1.set_xlabel('Date', fontweight='bold')
        ax1.set_ylabel('Albédo', color='black', fontweight='bold')
        
        # Plot albedo data
        albedo_lines = []
        for fraction in self.fraction_classes:
            albedo_col = f"{fraction}_mean"
            if albedo_col in year_data.columns:
                albedo_data = year_data[albedo_col].dropna()
                if len(albedo_data) > 0:
                    line = ax1.plot(year_data['date'], year_data[albedo_col], 
                                   marker='o', markersize=4, linewidth=2, alpha=0.9,
                                   label=f'Albédo {self.class_labels[fraction]}',
                                   color=FRACTION_COLORS.get(fraction, 'gray'))
                    albedo_lines.extend(line)
        
        ax1.set_ylim(0, 1)  # Albedo ranges from 0 to 1
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='y', labelcolor='black')
        
        # Plot pixel counts on secondary axis with dashed lines
        pixel_lines = []
        for fraction in self.fraction_classes:
            pixel_col = f"{fraction}_pixel_count"
            if pixel_col in year_data.columns:
                pixel_data = year_data[pixel_col].dropna()
                if len(pixel_data) > 0:
                    line = ax2.plot(year_data['date'], year_data[pixel_col], 
                                   marker='s', markersize=3, linewidth=1, alpha=0.6, 
                                   linestyle='--', 
                                   label=f'Pixels {self.class_labels[fraction]}',
                                   color=FRACTION_COLORS.get(fraction, 'gray'))
                    pixel_lines.extend(line)
        
        ax2.tick_params(axis='y', labelcolor='navy')
        
        # Combine legends from both axes
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        
        # Create combined legend
        ax1.legend(lines1 + lines2, labels1 + labels2, 
                  bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        
        # Add summary statistics text box
        stats_text = self._generate_year_summary_stats(year, year_data, pixel_analyzer)
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, 
                verticalalignment='top', fontsize=8,
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        
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
                ax.plot(score_data['month'], score_data['mean_percentage'], 
                       marker='o', linewidth=2, markersize=6,
                       label=qa_labels[i], color=qa_colors[i])
        
        ax.set_title('📊 Distribution des Scores QA par Mois', fontweight='bold')
        ax.set_xlabel('Mois')
        ax.set_ylabel('Pourcentage Moyen (%)')
        ax.set_xticks([6, 7, 8, 9])
        ax.set_xticklabels(['Juin', 'Juillet', 'Août', 'Sept'])
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_qa_stacked_bars(self, ax, qa_stats):
        """Plot QA scores as stacked bars by month"""
        months = [6, 7, 8, 9]
        month_names = ['Juin', 'Juillet', 'Août', 'Sept']
        qa_colors = ['#2E8B57', '#4682B4', '#FF8C00', '#DC143C']
        qa_labels = ['QA 0 (Meilleur)', 'QA 1 (Bon)', 'QA 2 (Modéré)', 'QA 3 (Mauvais)']
        
        # Prepare data for stacking
        qa_data_by_month = {}
        for month in months:
            month_data = qa_stats[qa_stats['month'] == month]
            qa_data_by_month[month] = {}
            for qa_score in ['0', '1', '2', '3']:
                score_data = month_data[month_data['qa_score'] == qa_score]
                if not score_data.empty:
                    qa_data_by_month[month][qa_score] = score_data['mean_percentage'].iloc[0]
                else:
                    qa_data_by_month[month][qa_score] = 0
        
        # Create stacked bar chart
        bottom = np.zeros(len(months))
        for i, qa_score in enumerate(['0', '1', '2', '3']):
            values = [qa_data_by_month[month][qa_score] for month in months]
            ax.bar(month_names, values, bottom=bottom, 
                  label=qa_labels[i], color=qa_colors[i])
            bottom += values
        
        ax.set_title('📊 Répartition des Scores QA (Empilés)', fontweight='bold')
        ax.set_xlabel('Mois')
        ax.set_ylabel('Pourcentage (%)')
        ax.legend()
    
    def _plot_qa_trends_by_month(self, ax, qa_stats):
        """Plot QA trends by month with focus on best vs poor quality"""
        best_data = qa_stats[qa_stats['qa_score'] == '0']
        poor_data = qa_stats[qa_stats['qa_score'] == '3']
        
        if not best_data.empty:
            ax.plot(best_data['month'], best_data['mean_percentage'], 
                   marker='o', linewidth=3, markersize=8,
                   label='QA 0 (Meilleur)', color='#2E8B57')
        
        if not poor_data.empty:
            ax.plot(poor_data['month'], poor_data['mean_percentage'], 
                   marker='s', linewidth=3, markersize=8,
                   label='QA 3 (Mauvais)', color='#DC143C')
        
        ax.set_title('📈 Tendances QA: Meilleur vs Mauvais', fontweight='bold')
        ax.set_xlabel('Mois')
        ax.set_ylabel('Pourcentage (%)')
        ax.set_xticks([6, 7, 8, 9])
        ax.set_xticklabels(['Juin', 'Juillet', 'Août', 'Sept'])
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_qa_quality_heatmap(self, ax, true_qa_results):
        """Plot QA quality ratios as heatmap"""
        if 'by_month' not in true_qa_results:
            ax.text(0.5, 0.5, 'Pas de données QA\ndisponibles', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        # Prepare heatmap data
        heatmap_data = []
        months = []
        
        for month, month_data in true_qa_results['by_month'].items():
            if 'quality_ratios' in month_data:
                ratios = month_data['quality_ratios']
                months.append(MONTH_NAMES[month])
                heatmap_data.append([
                    ratios['best_ratio'],
                    ratios['good_ratio'], 
                    ratios['moderate_ratio'],
                    ratios['poor_ratio']
                ])
        
        if heatmap_data:
            heatmap_array = np.array(heatmap_data)
            
            im = ax.imshow(heatmap_array.T, cmap='RdYlGn_r', aspect='auto')
            
            # Set labels
            ax.set_xticks(range(len(months)))
            ax.set_xticklabels(months)
            ax.set_yticks(range(4))
            ax.set_yticklabels(['QA 0\n(Meilleur)', 'QA 1\n(Bon)', 'QA 2\n(Modéré)', 'QA 3\n(Mauvais)'])
            
            # Add text annotations
            for i in range(len(months)):
                for j in range(4):
                    text = ax.text(i, j, f'{heatmap_array[i, j]:.1f}%',
                                 ha="center", va="center", color="black", fontweight='bold')
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax, shrink=0.8)
            cbar.set_label('Pourcentage (%)')
            
            ax.set_title('🌡️ Heatmap des Ratios QA', fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'Pas de données\nde ratios QA', 
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