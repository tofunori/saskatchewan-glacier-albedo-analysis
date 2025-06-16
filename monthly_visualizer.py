"""
Visualiseur de statistiques mensuelles pour l'analyse d'albédo
=============================================================

Ce module crée spécifiquement les graphiques de statistiques mensuelles
demandés par l'utilisateur : moyennes, variabilité, distributions et comptages.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import (FRACTION_CLASSES, CLASS_LABELS, MONTH_NAMES, FRACTION_COLORS,
                   PLOT_STYLES, OUTPUT_DIR)
from helpers import print_section_header, ensure_directory_exists
import os

class MonthlyVisualizer:
    """
    Visualiseur spécialisé pour les graphiques mensuels
    """
    
    def __init__(self, data_handler):
        """
        Initialise le visualiseur mensuel
        
        Args:
            data_handler: Instance d'AlbedoDataHandler avec données chargées
        """
        self.data_handler = data_handler
        self.data = data_handler.data
        self.fraction_classes = FRACTION_CLASSES
        self.class_labels = CLASS_LABELS
        
    def create_monthly_statistics_graphs(self, variable='mean', save_path=None):
        """
        Crée les graphiques de statistiques mensuelles demandés par l'utilisateur
        
        Cette fonction génère 4 sous-graphiques :
        1. Moyennes mensuelles par fraction
        2. Variabilité mensuelle (écart-types)
        3. Distributions mensuelles (boxplots)
        4. Nombre d'observations par mois
        
        Args:
            variable (str): Variable à analyser ('mean' ou 'median')
            save_path (str, optional): Chemin pour sauvegarder le graphique
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        print_section_header("Création des graphiques de statistiques mensuelles", level=2)
        print("🎨 Génération des 4 graphiques mensuels demandés...")
        
        # Préparer les données mensuelles
        monthly_stats = self._prepare_monthly_statistics(variable)
        
        if monthly_stats.empty:
            print("❌ Pas de données pour créer les graphiques mensuels")
            return None
        
        # Créer la figure avec 4 sous-graphiques
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Statistiques Mensuelles d\'Albédo par Fraction ({variable.title()})', 
                     fontsize=16, fontweight='bold', y=0.98)
        
        # Graphique 1: Moyennes mensuelles par fraction
        self._plot_monthly_means(axes[0, 0], monthly_stats)
        
        # Graphique 2: Variabilité mensuelle (écart-types)
        self._plot_monthly_variability(axes[0, 1], monthly_stats)
        
        # Graphique 3: Distributions mensuelles (boxplots)
        self._plot_monthly_distributions(axes[1, 0], variable)
        
        # Graphique 4: Nombre d'observations par mois
        self._plot_monthly_counts(axes[1, 1], monthly_stats)
        
        plt.tight_layout()
        
        # Sauvegarder le graphique
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, f'monthly_statistics_{variable}_graphs.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Graphiques mensuels sauvegardés: {save_path}")
        
        plt.show()
        
        return save_path
    
    def _prepare_monthly_statistics(self, variable):
        """
        Prépare les statistiques mensuelles pour tous les graphiques
        
        Args:
            variable (str): Variable à analyser
            
        Returns:
            pd.DataFrame: Statistiques mensuelles par fraction et mois
        """
        monthly_stats = []
        
        for month in [6, 7, 8, 9]:  # Saison de fonte
            month_data = self.data[self.data['month'] == month].copy()
            
            for fraction in self.fraction_classes:
                col_name = f"{fraction}_{variable}"
                
                if col_name in month_data.columns:
                    values = month_data[col_name].dropna()
                    
                    if len(values) > 0:
                        monthly_stats.append({
                            'month': month,
                            'month_name': MONTH_NAMES[month],
                            'fraction': fraction,
                            'fraction_label': self.class_labels[fraction],
                            'mean': values.mean(),
                            'median': values.median(),
                            'std': values.std(),
                            'min': values.min(),
                            'max': values.max(),
                            'count': len(values),
                            'q25': values.quantile(0.25),
                            'q75': values.quantile(0.75)
                        })
        
        return pd.DataFrame(monthly_stats)
    
    def _plot_monthly_means(self, ax, monthly_stats):
        """
        Graphique 1: Moyennes mensuelles par fraction
        """
        for fraction in self.fraction_classes:
            fraction_data = monthly_stats[monthly_stats['fraction'] == fraction]
            if not fraction_data.empty:
                ax.plot(fraction_data['month'], fraction_data['mean'], 
                       marker='o', linewidth=3, markersize=8,
                       label=self.class_labels[fraction],
                       color=FRACTION_COLORS.get(fraction, 'gray'))
        
        ax.set_title('📊 Moyennes Mensuelles par Fraction', fontweight='bold', fontsize=12)
        ax.set_xlabel('Mois')
        ax.set_ylabel('Albédo Moyen')
        ax.set_xticks([6, 7, 8, 9])
        ax.set_xticklabels(['Juin', 'Juillet', 'Août', 'Sept'])
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Ajouter les valeurs sur les points
        for fraction in self.fraction_classes:
            fraction_data = monthly_stats[monthly_stats['fraction'] == fraction]
            for _, row in fraction_data.iterrows():
                ax.annotate(f'{row["mean"]:.3f}', 
                           (row['month'], row['mean']),
                           textcoords="offset points", xytext=(0,10), ha='center',
                           fontsize=8, alpha=0.7)
    
    def _plot_monthly_variability(self, ax, monthly_stats):
        """
        Graphique 2: Variabilité mensuelle (écart-types)
        """
        for fraction in self.fraction_classes:
            fraction_data = monthly_stats[monthly_stats['fraction'] == fraction]
            if not fraction_data.empty:
                ax.plot(fraction_data['month'], fraction_data['std'], 
                       marker='s', linewidth=2, markersize=6,
                       label=self.class_labels[fraction],
                       color=FRACTION_COLORS.get(fraction, 'gray'),
                       linestyle='--')
        
        ax.set_title('📈 Variabilité Mensuelle (Écart-type)', fontweight='bold', fontsize=12)
        ax.set_xlabel('Mois')
        ax.set_ylabel('Écart-type de l\'Albédo')
        ax.set_xticks([6, 7, 8, 9])
        ax.set_xticklabels(['Juin', 'Juillet', 'Août', 'Sept'])
        ax.grid(True, alpha=0.3)
        
        # Légende simplifiée pour éviter l'encombrement
        ax.legend(fontsize=8, loc='upper right')
    
    def _plot_monthly_distributions(self, ax, variable):
        """
        Graphique 3: Distributions mensuelles (boxplots)
        """
        # Utiliser la fraction avec le plus de données (généralement pure_ice)
        main_fraction = 'pure_ice'
        col_name = f"{main_fraction}_{variable}"
        
        # Préparer les données pour le boxplot
        boxplot_data = []
        boxplot_labels = []
        boxplot_colors = []
        
        for month in [6, 7, 8, 9]:
            month_data = self.data[self.data['month'] == month]
            
            if col_name in month_data.columns:
                values = month_data[col_name].dropna()
                if len(values) > 0:
                    boxplot_data.append(values)
                    boxplot_labels.append(MONTH_NAMES[month])
                    boxplot_colors.append(plt.cm.Blues(0.3 + month*0.15))  # Gradient de couleurs
        
        if boxplot_data:
            bp = ax.boxplot(boxplot_data, labels=boxplot_labels, patch_artist=True,
                           showmeans=True, meanline=True)
            
            # Colorier les boîtes
            for patch, color in zip(bp['boxes'], boxplot_colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            
            # Styliser les moyennes
            for mean in bp['means']:
                mean.set_color('red')
                mean.set_linewidth(2)
        
        ax.set_title(f'📦 Distribution Mensuelle - {self.class_labels[main_fraction]}', 
                    fontweight='bold', fontsize=12)
        ax.set_ylabel('Albédo')
        ax.grid(True, alpha=0.3)
        
        # Ajouter des statistiques textuelles
        if boxplot_data:
            stats_text = []
            for i, data in enumerate(boxplot_data):
                stats_text.append(f"{boxplot_labels[i]}: n={len(data)}")
            
            ax.text(0.02, 0.98, '\n'.join(stats_text), transform=ax.transAxes,
                   verticalalignment='top', fontsize=9,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    def _plot_monthly_counts(self, ax, monthly_stats):
        """
        Graphique 4: Nombre d'observations par mois et fraction
        """
        # Créer un pivot table pour les comptages
        count_data = monthly_stats.pivot(index='month', columns='fraction_label', values='count')
        
        # Assurer l'ordre correct des mois (saisonnier)
        month_order = [6, 7, 8, 9]
        count_data = count_data.reindex(month_order)
        
        # Graphique en barres groupées
        count_data.plot(kind='bar', ax=ax, width=0.8, 
                       color=[FRACTION_COLORS.get(f, 'gray') for f in self.fraction_classes])
        
        ax.set_title('📊 Nombre d\'Observations par Mois', fontweight='bold', fontsize=12)
        ax.set_xlabel('Mois')
        ax.set_ylabel('Nombre d\'Observations')
        ax.set_xticklabels(['Juin', 'Juillet', 'Août', 'Sept'], rotation=0)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Ajouter les valeurs sur les barres
        for container in ax.containers:
            ax.bar_label(container, fontsize=8, rotation=90)
    
    def create_seasonal_trends_comparison(self, monthly_results, variable='mean', save_path=None):
        """
        Crée un graphique comparant les tendances entre les mois
        
        Args:
            monthly_results (dict): Résultats des analyses mensuelles
            variable (str): Variable analysée
            save_path (str, optional): Chemin pour sauvegarder
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        print_section_header("Comparaison des tendances mensuelles", level=3)
        
        if not monthly_results:
            print("❌ Pas de résultats mensuels disponibles")
            return None
        
        # Préparer les données pour la visualisation
        trend_data = []
        
        for month, month_result in monthly_results.items():
            for fraction, fraction_result in month_result['fractions'].items():
                mk = fraction_result['mann_kendall']
                sen = fraction_result['sen_slope']
                
                trend_data.append({
                    'month': month,
                    'month_name': MONTH_NAMES[month],
                    'fraction': fraction,
                    'fraction_label': self.class_labels[fraction],
                    'trend': mk['trend'],
                    'p_value': mk['p_value'],
                    'slope_decade': sen['slope_per_decade'],
                    'n_obs': fraction_result['n_obs']
                })
        
        trend_df = pd.DataFrame(trend_data)
        
        if trend_df.empty:
            print("❌ Pas de données pour la comparaison mensuelle")
            return None
        
        # Créer le graphique
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle(f'Comparaison des Tendances Mensuelles ({variable.title()})', 
                     fontsize=14, fontweight='bold')
        
        # Graphique 1: Heatmap des pentes
        pivot_slopes = trend_df.pivot(index='fraction_label', columns='month_name', values='slope_decade')
        
        # Assurer l'ordre correct des mois (saisonnier)
        month_name_order = ['Juin', 'Juillet', 'Août', 'Septembre']
        available_months = [m for m in month_name_order if m in pivot_slopes.columns]
        pivot_slopes = pivot_slopes.reindex(columns=available_months)
        
        # Gérer les valeurs manquantes pour la heatmap
        pivot_slopes_filled = pivot_slopes.fillna(0)
        
        im1 = sns.heatmap(pivot_slopes_filled, annot=True, fmt='.6f', cmap='RdBu_r', center=0,
                         ax=ax1, cbar_kws={'label': 'Pente Sen (par décennie)'})
        ax1.set_title('Pentes de Sen par Mois et Fraction')
        ax1.set_ylabel('Fraction de Couverture')
        
        # Graphique 2: Nombre d'observations
        pivot_counts = trend_df.pivot(index='fraction_label', columns='month_name', values='n_obs')
        pivot_counts = pivot_counts.reindex(columns=available_months)
        pivot_counts_filled = pivot_counts.fillna(0)
        
        im2 = sns.heatmap(pivot_counts_filled, annot=True, fmt='.0f', cmap='Blues',
                         ax=ax2, cbar_kws={'label': 'Nombre d\'observations'})
        ax2.set_title('Nombre d\'Observations')
        ax2.set_ylabel('Fraction de Couverture')
        
        plt.tight_layout()
        
        # Sauvegarder
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, f'monthly_trends_comparison_{variable}.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Comparaison mensuelle sauvegardée: {save_path}")
        
        plt.show()
        
        return save_path
    
    def create_monthly_summary_table(self, variable='mean'):
        """
        Génère un tableau de résumé des statistiques mensuelles
        
        Args:
            variable (str): Variable analysée
            
        Returns:
            pd.DataFrame: Tableau de résumé mensuel
        """
        monthly_stats = self._prepare_monthly_statistics(variable)
        
        if monthly_stats.empty:
            return pd.DataFrame()
        
        # Reformater le tableau pour export
        summary_table = monthly_stats[[
            'month_name', 'fraction_label', 'count', 'mean', 'std', 'median', 'min', 'max'
        ]].copy()
        
        summary_table.columns = [
            'Mois', 'Fraction', 'N_observations', 'Moyenne', 'Ecart_type',
            'Mediane', 'Minimum', 'Maximum'
        ]
        
        return summary_table.round(6)
    
    def print_monthly_summary(self, variable='mean'):
        """
        Affiche un résumé des statistiques mensuelles
        """
        print_section_header("Résumé des statistiques mensuelles", level=2)
        
        monthly_stats = self._prepare_monthly_statistics(variable)
        
        if monthly_stats.empty:
            print("❌ Pas de données mensuelles disponibles")
            return
        
        print("📊 Statistiques par mois:")
        
        for month in [6, 7, 8, 9]:
            month_name = MONTH_NAMES[month]
            month_data = monthly_stats[monthly_stats['month'] == month]
            
            if not month_data.empty:
                print(f"\n📅 {month_name}:")
                total_obs = month_data['count'].sum()
                print(f"  📊 Observations totales: {total_obs}")
                
                # Fraction avec le plus d'observations
                max_obs_fraction = month_data.loc[month_data['count'].idxmax()]
                print(f"  🏆 Plus d'observations: {max_obs_fraction['fraction_label']} ({max_obs_fraction['count']} obs)")
                
                # Moyenne générale pondérée
                weighted_mean = (month_data['mean'] * month_data['count']).sum() / month_data['count'].sum()
                print(f"  📈 Albédo moyen pondéré: {weighted_mean:.4f}")
            else:
                print(f"\n📅 {month_name}: Pas de données")