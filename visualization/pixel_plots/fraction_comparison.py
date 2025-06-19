"""
MOD10A1 Fraction Comparison Plots
=================================

This module handles the new Phase 2 functionality for comparing
MOD10A1 fractions against each other (inter-fraction analysis).
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import os

from utils.helpers import print_section_header, ensure_directory_exists
from config import OUTPUT_DIR
from .core import BasePixelVisualizer


class FractionComparisonVisualizer(BasePixelVisualizer):
    """
    Specialized visualizer for MOD10A1 inter-fraction comparisons
    """
    
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
        stats_df = pd.DataFrame(stats_data)
        
        if not stats_df.empty:
            stats_path = os.path.join(save_dir, 'mod10a1_fraction_statistics.csv')
            stats_df.to_csv(stats_path, index=False)
            print(f"✓ Statistiques détaillées exportées: {stats_path}")
            
            return stats_path
        
        return None