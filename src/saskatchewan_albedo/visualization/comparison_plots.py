"""
Visualisations comparatives entre datasets MODIS
===============================================

Ce module génère des graphiques pour comparer les données
entre MCD43A3 et MOD10A1, incluant corrélations, différences,
et évolutions temporelles.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import warnings

# Import from parent package
from ..config import (
    FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS,
    COMPARISON_CONFIG, PLOT_STYLES
)
from ..utils.helpers import ensure_directory_exists, print_section_header

class ComparisonVisualizer:
    """
    Générateur de visualisations comparatives
    """
    
    def __init__(self, comparison_data, output_dir="results"):
        """
        Initialise le visualiseur de comparaison
        
        Args:
            comparison_data (dict): Données de comparaison du DatasetManager
            output_dir (str): Répertoire de sortie
        """
        self.comparison_data = comparison_data
        self.merged_data = comparison_data['merged']
        self.output_dir = output_dir
        ensure_directory_exists(output_dir)
        
        # Configuration matplotlib
        plt.style.use('seaborn-v0_8')
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['figure.dpi'] = 300
        
    def plot_correlation_matrix(self, save=True):
        """
        Crée une matrice de corrélation entre MCD43A3 et MOD10A1
        
        Args:
            save (bool): Sauvegarder le graphique
            
        Returns:
            matplotlib.figure.Figure: Figure du graphique
        """
        print_section_header("Matrice de corrélation MCD43A3 vs MOD10A1", level=3)
        
        # Préparer les données de corrélation
        correlations = []
        fraction_pairs = []
        
        for fraction in FRACTION_CLASSES:
            mcd_col = f'mcd43a3_{fraction}_mean'
            mod_col = f'mod10a1_{fraction}_mean'
            
            if mcd_col in self.merged_data.columns and mod_col in self.merged_data.columns:
                valid_data = self.merged_data[[mcd_col, mod_col]].dropna()
                
                if len(valid_data) >= 10:
                    corr = valid_data[mcd_col].corr(valid_data[mod_col])
                    correlations.append(corr)
                    fraction_pairs.append(CLASS_LABELS[fraction])
                else:
                    correlations.append(np.nan)
                    fraction_pairs.append(CLASS_LABELS[fraction])
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Matrice de corrélation sous forme de heatmap
        corr_matrix = np.diag(correlations)
        
        # Utiliser un barplot pour une meilleure lisibilité
        bars = ax.barh(fraction_pairs, correlations, 
                      color=[FRACTION_COLORS[frac] for frac in FRACTION_CLASSES[:len(correlations)]])
        
        # Personnaliser le graphique
        ax.set_xlabel('Coefficient de corrélation (Pearson)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Classes de fraction de couverture', fontsize=12, fontweight='bold')
        ax.set_title('Corrélations entre MCD43A3 et MOD10A1 par classe de fraction', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Ajouter les valeurs sur les barres
        for i, (bar, corr) in enumerate(zip(bars, correlations)):
            if not np.isnan(corr):
                ax.text(corr + 0.01 if corr > 0 else corr - 0.01, bar.get_y() + bar.get_height()/2, 
                       f'{corr:.3f}', ha='left' if corr > 0 else 'right', va='center', 
                       fontweight='bold', fontsize=10)
        
        # Lignes de référence
        ax.axvline(x=0.7, color='green', linestyle='--', alpha=0.7, label='Forte corrélation (0.7)')
        ax.axvline(x=0.5, color='orange', linestyle='--', alpha=0.7, label='Corrélation modérée (0.5)')
        
        ax.set_xlim(-0.1, 1.0)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.tight_layout()
        
        if save:
            filepath = f"{self.output_dir}/correlation_matrix_comparison.png"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"✓ Matrice de corrélation sauvegardée: {filepath}")
        
        return fig
    
    def plot_scatter_comparison(self, fraction='pure_ice', save=True):
        """
        Crée un graphique de dispersion pour comparer les valeurs
        
        Args:
            fraction (str): Fraction à analyser
            save (bool): Sauvegarder le graphique
            
        Returns:
            matplotlib.figure.Figure: Figure du graphique
        """
        print_section_header(f"Graphique de dispersion - {CLASS_LABELS[fraction]}", level=3)
        
        mcd_col = f'mcd43a3_{fraction}_mean'
        mod_col = f'mod10a1_{fraction}_mean'
        
        if mcd_col not in self.merged_data.columns or mod_col not in self.merged_data.columns:
            print(f"❌ Données non disponibles pour {fraction}")
            return None
        
        valid_data = self.merged_data[[mcd_col, mod_col]].dropna()
        
        if len(valid_data) < 10:
            print(f"❌ Données insuffisantes pour {fraction} (n={len(valid_data)})")
            return None
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Scatter plot
        scatter = ax.scatter(valid_data[mcd_col], valid_data[mod_col], 
                           alpha=0.6, c=FRACTION_COLORS[fraction], s=30)
        
        # Ligne 1:1
        min_val = min(valid_data[mcd_col].min(), valid_data[mod_col].min())
        max_val = max(valid_data[mcd_col].max(), valid_data[mod_col].max())
        ax.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.8, linewidth=2, label='Ligne 1:1')
        
        # Régression linéaire
        z = np.polyfit(valid_data[mcd_col], valid_data[mod_col], 1)
        p = np.poly1d(z)
        ax.plot(valid_data[mcd_col].sort_values(), p(valid_data[mcd_col].sort_values()), 
               'r-', alpha=0.8, linewidth=2, label=f'Régression (y={z[0]:.3f}x+{z[1]:.3f})')
        
        # Calculs statistiques
        correlation = valid_data[mcd_col].corr(valid_data[mod_col])
        rmse = np.sqrt(((valid_data[mod_col] - valid_data[mcd_col]) ** 2).mean())
        bias = (valid_data[mod_col] - valid_data[mcd_col]).mean()
        
        # Personnaliser le graphique
        ax.set_xlabel('MCD43A3 Albédo', fontsize=12, fontweight='bold')
        ax.set_ylabel('MOD10A1 Albédo', fontsize=12, fontweight='bold')
        ax.set_title(f'Comparaison MCD43A3 vs MOD10A1 - {CLASS_LABELS[fraction]}', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Ajouter les statistiques
        stats_text = f'r = {correlation:.3f}\\nRMSE = {rmse:.4f}\\nBiais = {bias:+.4f}\\nn = {len(valid_data)}'
        ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=11, 
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_aspect('equal', adjustable='box')
        
        plt.tight_layout()
        
        if save:
            filepath = f"{self.output_dir}/scatter_comparison_{fraction}.png"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"✓ Graphique de dispersion sauvegardé: {filepath}")
        
        return fig
    
    def plot_time_series_comparison(self, fraction='pure_ice', save=True):
        """
        Crée un graphique de séries temporelles pour comparer l'évolution - POINTS SEULEMENT
        
        Args:
            fraction (str): Fraction à analyser
            save (bool): Sauvegarder le graphique
            
        Returns:
            matplotlib.figure.Figure: Figure du graphique
        """
        print_section_header(f"Séries temporelles - {CLASS_LABELS[fraction]} - TOUS LES POINTS", level=3)
        
        mcd_col = f'mcd43a3_{fraction}_mean'
        mod_col = f'mod10a1_{fraction}_mean'
        
        if mcd_col not in self.merged_data.columns or mod_col not in self.merged_data.columns:
            print(f"❌ Données non disponibles pour {fraction}")
            return None
        
        # Préparer les données
        plot_data = self.merged_data[['date', mcd_col, mod_col]].dropna()
        plot_data = plot_data.sort_values('date')
        
        if len(plot_data) < 10:
            print(f"❌ Données insuffisantes pour {fraction}")
            return None
        
        print(f"✅ Affichage de {len(plot_data)} points de données pour {fraction}")
        
        # Créer le graphique avec style moderne
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), sharex=True)
        
        # GRAPHIQUE 1: SÉRIES TEMPORELLES - POINTS SEULEMENT
        # MCD43A3 - Points bleus
        ax1.scatter(plot_data['date'], plot_data[mcd_col], 
                   c='#3498db', s=25, alpha=0.8, edgecolors='white', linewidth=0.8,
                   label=f'MCD43A3 ({len(plot_data)} points)', zorder=5)
        
        # MOD10A1 - Points rouges
        ax1.scatter(plot_data['date'], plot_data[mod_col], 
                   c='#e74c3c', s=25, alpha=0.8, edgecolors='white', linewidth=0.8,
                   label=f'MOD10A1 ({len(plot_data)} points)', zorder=5)
        
        ax1.set_ylabel('Albedo', fontsize=14, fontweight='bold')
        ax1.set_title(f'Time Series Comparison - {CLASS_LABELS[fraction]}\nAll Individual Data Points (No Lines)', 
                     fontsize=16, fontweight='bold', pad=20)
        ax1.grid(True, alpha=0.4, linestyle=':', linewidth=0.8)
        ax1.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=12)
        ax1.set_facecolor('#fafafa')
        
        # GRAPHIQUE 2: DIFFÉRENCES - POINTS SEULEMENT
        differences = plot_data[mod_col] - plot_data[mcd_col]
        
        # Points de différence colorés selon le signe
        positive_mask = differences >= 0
        negative_mask = differences < 0
        
        # Points positifs (MOD10A1 > MCD43A3) en vert
        if positive_mask.any():
            ax2.scatter(plot_data.loc[positive_mask, 'date'], differences[positive_mask], 
                       c='#27ae60', s=30, alpha=0.8, edgecolors='white', linewidth=0.8,
                       label=f'MOD10A1 > MCD43A3 ({positive_mask.sum()} points)', zorder=5)
        
        # Points négatifs (MOD10A1 < MCD43A3) en orange
        if negative_mask.any():
            ax2.scatter(plot_data.loc[negative_mask, 'date'], differences[negative_mask], 
                       c='#f39c12', s=30, alpha=0.8, edgecolors='white', linewidth=0.8,
                       label=f'MOD10A1 < MCD43A3 ({negative_mask.sum()} points)', zorder=5)
        
        # Ligne de référence zéro
        ax2.axhline(y=0, color='#2c3e50', linestyle='--', alpha=0.8, linewidth=2)
        
        ax2.set_xlabel('Date', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Difference\n(MOD10A1 - MCD43A3)', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.4, linestyle=':', linewidth=0.8)
        ax2.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=12)
        ax2.set_facecolor('#fafafa')
        
        # Formater l'axe des dates de façon moderne
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax2.xaxis.set_major_locator(mdates.YearLocator(2))  # Tous les 2 ans
        ax2.xaxis.set_minor_locator(mdates.YearLocator())   # Marques mineures chaque année
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, fontsize=12)
        
        # Statistiques des différences améliorées
        diff_mean = differences.mean()
        diff_std = differences.std()
        diff_median = differences.median()
        stats_text = f'Statistics:\nMean: {diff_mean:+.4f}\nStd: {diff_std:.4f}\nMedian: {diff_median:+.4f}\nPoints: {len(differences)}'
        
        ax2.text(0.02, 0.98, stats_text, 
                transform=ax2.transAxes, fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='lightgray', alpha=0.95))
        
        plt.tight_layout()
        
        if save:
            filepath = f"{self.output_dir}/timeseries_comparison_{fraction}.png"
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
            print(f"✓ Enhanced timeseries with ALL POINTS saved: {filepath}")
        
        return fig
    
    def plot_difference_heatmap(self, save=True):
        """
        Crée une heatmap des différences par fraction et par mois
        
        Args:
            save (bool): Sauvegarder le graphique
            
        Returns:
            matplotlib.figure.Figure: Figure du graphique
        """
        print_section_header("Heatmap des différences par mois", level=3)
        
        # Préparer les données
        diff_matrix = []
        fraction_labels = []
        
        for fraction in FRACTION_CLASSES:
            mcd_col = f'mcd43a3_{fraction}_mean'
            mod_col = f'mod10a1_{fraction}_mean'
            
            if mcd_col in self.merged_data.columns and mod_col in self.merged_data.columns:
                monthly_diffs = []
                
                for month in [6, 7, 8, 9]:  # Juin à Septembre
                    month_data = self.merged_data[self.merged_data['month'] == month]
                    valid_data = month_data[[mcd_col, mod_col]].dropna()
                    
                    if len(valid_data) >= 5:
                        diff = (valid_data[mod_col] - valid_data[mcd_col]).mean()
                        monthly_diffs.append(diff)
                    else:
                        monthly_diffs.append(np.nan)
                
                diff_matrix.append(monthly_diffs)
                fraction_labels.append(CLASS_LABELS[fraction])
        
        if not diff_matrix:
            print("❌ Aucune donnée disponible pour la heatmap")
            return None
        
        # Créer la heatmap
        fig, ax = plt.subplots(figsize=(8, 10))
        
        diff_array = np.array(diff_matrix)
        
        # Déterminer les limites pour une palette centrée sur 0
        vmax = max(abs(np.nanmin(diff_array)), abs(np.nanmax(diff_array)))
        vmin = -vmax
        
        im = ax.imshow(diff_array, cmap='RdBu_r', aspect='auto', vmin=vmin, vmax=vmax)
        
        # Personnaliser les axes
        ax.set_xticks(range(4))
        ax.set_xticklabels(['Juin', 'Juillet', 'Août', 'Septembre'])
        ax.set_yticks(range(len(fraction_labels)))
        ax.set_yticklabels(fraction_labels)
        
        # Ajouter les valeurs dans les cellules
        for i in range(len(fraction_labels)):
            for j in range(4):
                value = diff_array[i, j]
                if not np.isnan(value):
                    text = ax.text(j, i, f'{value:.3f}', ha="center", va="center", 
                                 color="white" if abs(value) > vmax * 0.5 else "black",
                                 fontweight='bold', fontsize=9)
        
        # Titre et labels
        ax.set_title('Différences moyennes par mois (MOD10A1 - MCD43A3)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Mois', fontsize=12, fontweight='bold')
        ax.set_ylabel('Classes de fraction', fontsize=12, fontweight='bold')
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Différence d\'albédo', fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        
        if save:
            filepath = f"{self.output_dir}/difference_heatmap_monthly.png"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"✓ Heatmap des différences sauvegardée: {filepath}")
        
        return fig
    
    def plot_all_fractions_comparison(self, save=True):
        """
        Crée un graphique comparant toutes les fractions
        
        Args:
            save (bool): Sauvegarder le graphique
            
        Returns:
            matplotlib.figure.Figure: Figure du graphique
        """
        print_section_header("Comparaison toutes fractions", level=3)
        
        # Créer une grille de sous-graphiques
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.ravel()
        
        for i, fraction in enumerate(FRACTION_CLASSES):
            if i >= len(axes):
                break
                
            ax = axes[i]
            mcd_col = f'mcd43a3_{fraction}_mean'
            mod_col = f'mod10a1_{fraction}_mean'
            
            if mcd_col in self.merged_data.columns and mod_col in self.merged_data.columns:
                valid_data = self.merged_data[[mcd_col, mod_col]].dropna()
                
                if len(valid_data) >= 10:
                    # Scatter plot
                    ax.scatter(valid_data[mcd_col], valid_data[mod_col], 
                             alpha=0.6, c=FRACTION_COLORS[fraction], s=20)
                    
                    # Ligne 1:1
                    min_val = min(valid_data[mcd_col].min(), valid_data[mod_col].min())
                    max_val = max(valid_data[mcd_col].max(), valid_data[mod_col].max())
                    ax.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.8, linewidth=1)
                    
                    # Statistiques
                    correlation = valid_data[mcd_col].corr(valid_data[mod_col])
                    ax.text(0.05, 0.95, f'r = {correlation:.3f}', transform=ax.transAxes, 
                           fontsize=10, verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                    
                    ax.set_xlabel('MCD43A3', fontsize=10)
                    ax.set_ylabel('MOD10A1', fontsize=10)
                    ax.set_title(CLASS_LABELS[fraction], fontsize=11, fontweight='bold')
                    ax.grid(True, alpha=0.3)
                    ax.set_aspect('equal', adjustable='box')
                else:
                    ax.text(0.5, 0.5, 'Données\\ninsuffisantes', ha='center', va='center',
                           transform=ax.transAxes, fontsize=12)
                    ax.set_title(CLASS_LABELS[fraction], fontsize=11, fontweight='bold')
            else:
                ax.text(0.5, 0.5, 'Données\\nnon disponibles', ha='center', va='center',
                       transform=ax.transAxes, fontsize=12)
                ax.set_title(CLASS_LABELS[fraction], fontsize=11, fontweight='bold')
        
        # Masquer le dernier subplot s'il n'est pas utilisé
        if len(FRACTION_CLASSES) < len(axes):
            axes[-1].set_visible(False)
        
        plt.suptitle('Comparaison MCD43A3 vs MOD10A1 - Toutes les fractions', 
                    fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout()
        
        if save:
            filepath = f"{self.output_dir}/all_fractions_comparison.png"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"✓ Comparaison toutes fractions sauvegardée: {filepath}")
        
        return fig
    
    def generate_all_plots(self):
        """
        Génère tous les graphiques de comparaison
        """
        print_section_header("Génération de tous les graphiques de comparaison", level=2)
        
        plots_generated = []
        
        try:
            # Matrice de corrélation
            fig1 = self.plot_correlation_matrix()
            if fig1:
                plots_generated.append("Matrice de corrélation")
                plt.close(fig1)
        except Exception as e:
            print(f"❌ Erreur matrice de corrélation: {e}")
        
        try:
            # Heatmap des différences
            fig2 = self.plot_difference_heatmap()
            if fig2:
                plots_generated.append("Heatmap des différences")
                plt.close(fig2)
        except Exception as e:
            print(f"❌ Erreur heatmap: {e}")
        
        try:
            # Comparaison toutes fractions
            fig3 = self.plot_all_fractions_comparison()
            if fig3:
                plots_generated.append("Comparaison toutes fractions")
                plt.close(fig3)
        except Exception as e:
            print(f"❌ Erreur comparaison toutes fractions: {e}")
        
        # Graphiques individuels pour les fractions principales
        main_fractions = ['mostly_ice', 'pure_ice']
        for fraction in main_fractions:
            try:
                # Scatter plot
                fig4 = self.plot_scatter_comparison(fraction)
                if fig4:
                    plots_generated.append(f"Scatter {fraction}")
                    plt.close(fig4)
                
                # Séries temporelles
                fig5 = self.plot_time_series_comparison(fraction)
                if fig5:
                    plots_generated.append(f"Séries temporelles {fraction}")
                    plt.close(fig5)
            except Exception as e:
                print(f"❌ Erreur graphiques {fraction}: {e}")
        
        print(f"\n✅ Graphiques générés ({len(plots_generated)}):")
        for plot in plots_generated:
            print(f"  ✓ {plot}")
        
        return plots_generated