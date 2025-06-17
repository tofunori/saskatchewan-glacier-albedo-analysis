"""
Quality Assessment Plots
=======================

This module handles QA-specific visualizations including heatmaps,
time series plots, and quality statistics analysis.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from utils.helpers import print_section_header, ensure_directory_exists
from config import OUTPUT_DIR
from .core import BasePixelVisualizer


class QualityPlotsVisualizer(BasePixelVisualizer):
    """
    Specialized visualizer for quality assessment plots
    """
    
    def create_qa_statistics_plots(self, true_qa_results, save_path=None):
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
    
    def create_pixel_availability_heatmap(self, monthly_pixel_results, qa_results, save_path=None):
        """
        Create a heatmap showing pixel availability over time
        
        Args:
            monthly_pixel_results (dict): Results from monthly pixel analysis
            qa_results (dict): QA analysis results
            save_path (str, optional): Path to save the plot
            
        Returns:
            str: Path to saved plot
        """
        print_section_header("Création de la carte de chaleur de disponibilité des pixels", level=2)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('Disponibilité des Données - Heatmaps Temporelles', 
                     fontsize=16, fontweight='bold', y=0.98)
        
        # Heatmap 1: Pixel availability by year and month
        self._create_pixel_availability_matrix(ax1, monthly_pixel_results)
        
        # Heatmap 2: QA quality distribution
        self._create_qa_availability_matrix(ax2, qa_results)
        
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
        Create time series plot for total pixel counts and trends
        
        Args:
            total_pixel_results (dict): Results from analyze_total_pixel_trends()
            save_path (str, optional): Path to save the plot
            
        Returns:
            str: Path to saved plot
        """
        print_section_header("Création des séries temporelles des pixels totaux", level=2)
        
        if 'total_dataframe' not in total_pixel_results or total_pixel_results['total_dataframe'].empty:
            print("❌ Pas de données de pixels totaux pour créer les graphiques")
            return None
        
        total_data = total_pixel_results['total_dataframe']
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle('Analyse Temporelle des Pixels Totaux', 
                     fontsize=16, fontweight='bold', y=0.98)
        
        # Plot 1: Time series with trend
        self._plot_total_pixels_timeseries(ax1, total_data, total_pixel_results)
        
        # Plot 2: Seasonal patterns
        self._plot_seasonal_pixel_patterns(ax2, total_data)
        
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
    
    def _plot_qa_scores_distribution(self, ax, qa_stats):
        """Plot QA scores distribution"""
        qa_columns = ['quality_0_best', 'quality_1_good', 'quality_2_moderate', 'quality_3_poor']
        qa_labels = ['QA 0 (Best)', 'QA 1 (Good)', 'QA 2 (Moderate)', 'QA 3 (Poor)']
        qa_colors = ['#27ae60', '#3498db', '#f39c12', '#e74c3c']
        
        # Calculate mean QA scores
        qa_means = []
        for col in qa_columns:
            if col in qa_stats.columns:
                qa_means.append(qa_stats[col].mean())
            else:
                qa_means.append(0)
        
        bars = ax.bar(qa_labels, qa_means, color=qa_colors, alpha=0.8, edgecolor='white', linewidth=1)
        
        # Add value labels on bars
        for bar, value in zip(bars, qa_means):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_title('Distribution Moyenne des Scores QA')
        ax.set_ylabel('Nombre Moyen de Pixels')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
    
    def _plot_qa_stacked_bars(self, ax, qa_stats):
        """Plot QA scores as stacked bars by month"""
        qa_columns = ['quality_0_best', 'quality_1_good', 'quality_2_moderate', 'quality_3_poor']
        qa_colors = ['#27ae60', '#3498db', '#f39c12', '#e74c3c']
        
        if 'month' in qa_stats.columns:
            months = sorted(qa_stats['month'].unique())
            bottom = np.zeros(len(months))
            
            for col, color in zip(qa_columns, qa_colors):
                if col in qa_stats.columns:
                    values = [qa_stats[qa_stats['month'] == m][col].mean() for m in months]
                    ax.bar(months, values, bottom=bottom, color=color, 
                          label=col.replace('quality_', 'QA ').replace('_', ' ').title(),
                          alpha=0.8, edgecolor='white', linewidth=0.5)
                    bottom += values
            
            ax.set_title('Distribution QA par Mois (Barres Empilées)')
            ax.set_xlabel('Mois')
            ax.set_ylabel('Nombre de Pixels')
            ax.legend()
    
    def _plot_qa_trends_by_month(self, ax, qa_stats):
        """Plot QA trends over months"""
        if 'month' in qa_stats.columns:
            months = sorted(qa_stats['month'].unique())
            
            # Calculate quality ratio (best quality / total)
            quality_ratios = []
            for month in months:
                month_data = qa_stats[qa_stats['month'] == month]
                if not month_data.empty:
                    total_pixels = month_data[['quality_0_best', 'quality_1_good', 
                                             'quality_2_moderate', 'quality_3_poor']].sum(axis=1).mean()
                    best_pixels = month_data['quality_0_best'].mean()
                    ratio = (best_pixels / total_pixels * 100) if total_pixels > 0 else 0
                    quality_ratios.append(ratio)
                else:
                    quality_ratios.append(0)
            
            ax.plot(months, quality_ratios, marker='o', linewidth=2, markersize=8, 
                   color='#2ecc71', markerfacecolor='white', markeredgewidth=2)
            ax.fill_between(months, quality_ratios, alpha=0.3, color='#2ecc71')
            
            ax.set_title('Évolution de la Qualité par Mois')
            ax.set_xlabel('Mois')
            ax.set_ylabel('% Pixels Excellente Qualité (QA 0)')
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3)
    
    def _plot_qa_quality_heatmap(self, ax, true_qa_results):
        """Plot QA quality ratios heatmap"""
        if 'seasonal_summary' in true_qa_results:
            seasonal_data = true_qa_results['seasonal_summary']
            
            # Create a simple heatmap representation
            quality_data = np.array([[seasonal_data.get('total_pixels', 0),
                                    seasonal_data.get('best_quality_pct', 0),
                                    seasonal_data.get('good_quality_pct', 0),
                                    seasonal_data.get('poor_quality_pct', 0)]])
            
            im = ax.imshow(quality_data, cmap='RdYlGn', aspect='auto')
            ax.set_title('Résumé de la Qualité Saisonnière')
            ax.set_xticks([0, 1, 2, 3])
            ax.set_xticklabels(['Total', 'Best %', 'Good %', 'Poor %'])
            ax.set_yticks([0])
            ax.set_yticklabels(['Season'])
            
            # Add text annotations
            for i in range(quality_data.shape[1]):
                ax.text(i, 0, f'{quality_data[0, i]:.1f}', 
                       ha="center", va="center", fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'Données QA saisonnières\nnon disponibles', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Résumé de la Qualité Saisonnière')
    
    def _create_pixel_availability_matrix(self, ax, monthly_pixel_results):
        """Create pixel availability matrix"""
        if 'monthly_dataframe' in monthly_pixel_results:
            monthly_data = monthly_pixel_results['monthly_dataframe']
            
            # Create availability matrix
            years = sorted(monthly_data['year'].unique())
            months = [6, 7, 8, 9]  # Melt season
            
            availability_matrix = np.zeros((len(years), len(months)))
            
            for i, year in enumerate(years):
                for j, month in enumerate(months):
                    year_month_data = monthly_data[
                        (monthly_data['year'] == year) & 
                        (monthly_data['month'] == month)
                    ]
                    if not year_month_data.empty:
                        # Calculate total pixels for availability
                        pixel_cols = [f"{f}_pixel_count" for f in self.fraction_classes]
                        available_cols = [col for col in pixel_cols if col in monthly_data.columns]
                        if available_cols:
                            total_pixels = year_month_data[available_cols].sum(axis=1).mean()
                            availability_matrix[i, j] = total_pixels
            
            im = ax.imshow(availability_matrix, cmap='viridis', aspect='auto')
            ax.set_title('Disponibilité des Pixels par Année/Mois')
            ax.set_xlabel('Mois')
            ax.set_ylabel('Année')
            ax.set_xticks(range(len(months)))
            ax.set_xticklabels([f'{m:02d}' for m in months])
            ax.set_yticks(range(len(years)))
            ax.set_yticklabels(years)
            
            # Add colorbar
            plt.colorbar(im, ax=ax, shrink=0.8, label='Nombre de Pixels')
        else:
            ax.text(0.5, 0.5, 'Données mensuelles\nnon disponibles', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Disponibilité des Pixels')
    
    def _create_qa_availability_matrix(self, ax, qa_results):
        """Create QA availability matrix"""
        ax.text(0.5, 0.5, 'Heatmap QA\n(à implémenter)', 
               ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Distribution de la Qualité QA')
    
    def _plot_total_pixels_timeseries(self, ax, total_data, total_pixel_results):
        """Plot total pixels time series"""
        if 'date' in total_data.columns and 'total_pixels' in total_data.columns:
            ax.plot(total_data['date'], total_data['total_pixels'], 
                   linewidth=1.5, alpha=0.7, color='#3498db')
            ax.scatter(total_data['date'], total_data['total_pixels'], 
                      s=20, alpha=0.6, color='#2980b9')
            
            ax.set_title('Évolution Temporelle des Pixels Totaux')
            ax.set_ylabel('Nombre Total de Pixels')
            ax.grid(True, alpha=0.3)
    
    def _plot_seasonal_pixel_patterns(self, ax, total_data):
        """Plot seasonal patterns in pixel counts"""
        if 'month' in total_data.columns and 'total_pixels' in total_data.columns:
            monthly_means = total_data.groupby('month')['total_pixels'].agg(['mean', 'std'])
            
            months = monthly_means.index
            means = monthly_means['mean']
            stds = monthly_means['std']
            
            ax.errorbar(months, means, yerr=stds, marker='o', capsize=5,
                       linewidth=2, markersize=8, color='#e74c3c')
            
            for month in months:
                month_name = {6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep'}.get(month, str(month))
                ax.scatter(month, means[month], s=100, alpha=0.6, 
                          label=month_name)
        
        ax.set_title('Patterns Saisonniers par Année')
        ax.set_xlabel('Année')
        ax.set_ylabel('Nombre de Pixels Valides')
        ax.legend()
        ax.grid(True, alpha=0.3)