"""
Analyses saisonnières et mensuelles des tendances d'albédo
=========================================================

Ce module effectue les analyses de tendances par saison et par mois,
incluant les nouveaux graphiques de statistiques mensuelles demandés.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Import from package
from config import (FRACTION_CLASSES, CLASS_LABELS, MONTH_NAMES, FRACTION_COLORS,
                      PLOT_STYLES, get_significance_marker)
from utils.helpers import print_section_header, format_pvalue, validate_data

class SeasonalAnalyzer:
    """
    Analyseur pour les tendances saisonnières et mensuelles
    """
    
    def __init__(self, data_loader):
        """
        Initialise l'analyseur saisonnier
        
        Args:
            data_loader: Instance de SaskatchewanDataLoader avec données chargées
        """
        self.data_loader = data_loader
        self.data = data_loader.data
        self.fraction_classes = FRACTION_CLASSES
        self.class_labels = CLASS_LABELS
        self.results = {}
        
    def analyze_monthly_trends(self, variable='mean'):
        """
        Analyse les tendances par mois
        
        Args:
            variable (str): Variable à analyser ('mean' ou 'median')
            
        Returns:
            dict: Résultats des analyses mensuelles
        """
        print_section_header(f"Analyses mensuelles - Variable: {variable}", level=2)
        
        results = {}
        
        # Analyser chaque mois de la saison de fonte
        for month in [6, 7, 8, 9]:
            month_name = MONTH_NAMES[month]
            print(f"\n📅 Analyse pour {month_name} (mois {month})")
            
            # Filtrer les données pour ce mois
            month_data = self.data[self.data['month'] == month].copy()
            
            if len(month_data) < 5:
                print(f"  ⚠️  Données insuffisantes pour {month_name} ({len(month_data)} observations)")
                continue
            
            # Analyser chaque fraction pour ce mois
            month_results = {}
            
            for fraction in self.fraction_classes:
                col_name = f"{fraction}_{variable}"
                
                if col_name not in month_data.columns:
                    continue
                
                # Extraire les données valides
                valid_data = month_data[['decimal_year', col_name]].dropna()
                
                if len(valid_data) < 5:
                    continue
                
                times = valid_data['decimal_year'].values
                values = valid_data[col_name].values
                
                # Créer un analyseur temporaire pour cette sous-série
                temp_analyzer = BasicTrendAnalyzer(self.data_loader)
                
                # Test Mann-Kendall
                mk_result = temp_analyzer._perform_mann_kendall(values)
                
                # Pente de Sen
                sen_result = temp_analyzer._calculate_sen_slope(times, values)
                
                month_results[fraction] = {
                    'fraction': fraction,
                    'label': self.class_labels[fraction],
                    'n_obs': len(valid_data),
                    'mann_kendall': mk_result,
                    'sen_slope': sen_result,
                    'data': {
                        'times': times,
                        'values': values
                    }
                }
                
                # Afficher résultat bref
                trend = mk_result['trend']
                p_val = mk_result['p_value']
                slope_decade = sen_result['slope_per_decade']
                significance = get_significance_marker(p_val)
                
                print(f"    {self.class_labels[fraction]}: {trend} {significance} "
                      f"({slope_decade:.6f}/décennie)")
            
            results[month] = {
                'month': month,
                'month_name': month_name,
                'fractions': month_results
            }
        
        self.results[f'monthly_trends_{variable}'] = results
        return results
    
    def create_monthly_statistics_graphs(self, variable='mean', save_path=None):
        """
        Crée les graphiques de statistiques mensuelles demandés par l'utilisateur
        
        Args:
            variable (str): Variable à analyser ('mean' ou 'median')
            save_path (str, optional): Chemin pour sauvegarder le graphique
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        print_section_header("Création des graphiques de statistiques mensuelles", level=2)
        
        # Préparer les données mensuelles
        monthly_stats = []
        
        for month in [6, 7, 8, 9]:
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
                            'count': len(values)
                        })
        
        stats_df = pd.DataFrame(monthly_stats)
        
        if stats_df.empty:
            print("❌ Pas de données pour créer les graphiques mensuels")
            return None
        
        # Créer la figure avec sous-graphiques
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Statistiques Mensuelles d\'Albédo par Fraction ({variable.title()})', 
                     fontsize=16, fontweight='bold')
        
        # Graphique 1: Moyennes mensuelles
        ax1 = axes[0, 0]
        for fraction in self.fraction_classes:
            fraction_data = stats_df[stats_df['fraction'] == fraction]
            if not fraction_data.empty:
                ax1.plot(fraction_data['month'], fraction_data['mean'], 
                        marker='o', linewidth=2, label=self.class_labels[fraction],
                        color=FRACTION_COLORS.get(fraction, 'gray'))
        
        ax1.set_title('Moyennes Mensuelles par Fraction', fontweight='bold')
        ax1.set_xlabel('Mois')
        ax1.set_ylabel('Albédo Moyen')
        ax1.set_xticks([6, 7, 8, 9])
        ax1.set_xticklabels(['Juin', 'Juillet', 'Août', 'Sept'])
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # Graphique 2: Variabilité (écart-type)
        ax2 = axes[0, 1]
        for fraction in self.fraction_classes:
            fraction_data = stats_df[stats_df['fraction'] == fraction]
            if not fraction_data.empty:
                ax2.plot(fraction_data['month'], fraction_data['std'], 
                        marker='s', linewidth=2, label=self.class_labels[fraction],
                        color=FRACTION_COLORS.get(fraction, 'gray'))
        
        ax2.set_title('Variabilité Mensuelle (Écart-type)', fontweight='bold')
        ax2.set_xlabel('Mois')
        ax2.set_ylabel('Écart-type de l\'Albédo')
        ax2.set_xticks([6, 7, 8, 9])
        ax2.set_xticklabels(['Juin', 'Juillet', 'Août', 'Sept'])
        ax2.grid(True, alpha=0.3)
        
        # Graphique 3: Boxplot par mois
        ax3 = axes[1, 0]
        
        # Préparer les données pour le boxplot
        boxplot_data = []
        boxplot_labels = []
        
        for month in [6, 7, 8, 9]:
            month_data = self.data[self.data['month'] == month]
            # Utiliser la fraction avec le plus de données (généralement pure_ice)
            main_fraction = 'pure_ice'
            col_name = f"{main_fraction}_{variable}"
            
            if col_name in month_data.columns:
                values = month_data[col_name].dropna()
                if len(values) > 0:
                    boxplot_data.append(values)
                    boxplot_labels.append(MONTH_NAMES[month])
        
        if boxplot_data:
            bp = ax3.boxplot(boxplot_data, labels=boxplot_labels, patch_artist=True)
            for patch in bp['boxes']:
                patch.set_facecolor('lightblue')
                patch.set_alpha(0.7)
        
        ax3.set_title(f'Distribution Mensuelle - {self.class_labels["pure_ice"]}', fontweight='bold')
        ax3.set_ylabel('Albédo')
        ax3.grid(True, alpha=0.3)
        
        # Graphique 4: Nombre d'observations par mois
        ax4 = axes[1, 1]
        
        # Compter les observations par mois et fraction
        count_data = stats_df.pivot(index='month', columns='fraction_label', values='count')
        count_data.plot(kind='bar', ax=ax4, width=0.8)
        
        ax4.set_title('Nombre d\'Observations par Mois', fontweight='bold')
        ax4.set_xlabel('Mois')
        ax4.set_ylabel('Nombre d\'Observations')
        ax4.set_xticklabels(['Juin', 'Juillet', 'Août', 'Sept'], rotation=0)
        ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Sauvegarder le graphique
        if save_path is None:
            save_path = f'monthly_statistics_{variable}_graphs.png'
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Graphique sauvegardé: {save_path}")
        
        plt.show()
        
        return save_path
    
    def create_seasonal_comparison_graph(self, variable='mean', save_path=None):
        """
        Crée un graphique comparant les tendances saisonnières
        
        Args:
            variable (str): Variable à analyser
            save_path (str, optional): Chemin pour sauvegarder
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        print_section_header("Comparaison des tendances saisonnières", level=3)
        
        if f'monthly_trends_{variable}' not in self.results:
            print("❌ Analyses mensuelles non effectuées")
            return None
        
        monthly_results = self.results[f'monthly_trends_{variable}']
        
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
                    'significance': get_significance_marker(mk['p_value'])
                })
        
        trend_df = pd.DataFrame(trend_data)
        
        if trend_df.empty:
            print("❌ Pas de données pour la comparaison saisonnière")
            return None
        
        # Créer le graphique
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle(f'Comparaison des Tendances Saisonnières ({variable.title()})', 
                     fontsize=14, fontweight='bold')
        
        # Graphique 1: Heatmap des pentes
        pivot_slopes = trend_df.pivot(index='fraction_label', columns='month_name', values='slope_decade')
        sns.heatmap(pivot_slopes, annot=True, fmt='.6f', cmap='RdBu_r', center=0,
                   ax=ax1, cbar_kws={'label': 'Pente Sen (par décennie)'})
        ax1.set_title('Pentes de Sen par Mois et Fraction')
        ax1.set_ylabel('Fraction de Couverture')
        
        # Graphique 2: Significativité
        # Convertir les p-values en couleurs
        significance_colors = []
        for _, row in trend_df.iterrows():
            if row['p_value'] < 0.001:
                significance_colors.append(3)
            elif row['p_value'] < 0.01:
                significance_colors.append(2)
            elif row['p_value'] < 0.05:
                significance_colors.append(1)
            else:
                significance_colors.append(0)
        
        trend_df['sig_level'] = significance_colors
        pivot_sig = trend_df.pivot(index='fraction_label', columns='month_name', values='sig_level')
        
        sns.heatmap(pivot_sig, annot=True, fmt='d', cmap='Reds', 
                   ax=ax2, cbar_kws={'label': 'Niveau de significativité'})
        ax2.set_title('Significativité Statistique')
        ax2.set_ylabel('Fraction de Couverture')
        
        plt.tight_layout()
        
        # Sauvegarder
        if save_path is None:
            save_path = f'seasonal_trends_comparison_{variable}.png'
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Graphique sauvegardé: {save_path}")
        
        plt.show()
        
        return save_path
    
    def get_monthly_summary_table(self, variable='mean'):
        """
        Génère un tableau de résumé des analyses mensuelles
        
        Args:
            variable (str): Variable analysée
            
        Returns:
            pd.DataFrame: Tableau de résumé mensuel
        """
        if f'monthly_trends_{variable}' not in self.results:
            raise ValueError(f"Analyses mensuelles non effectuées pour {variable}")
        
        monthly_results = self.results[f'monthly_trends_{variable}']
        summary_data = []
        
        for month, month_result in monthly_results.items():
            for fraction, fraction_result in month_result['fractions'].items():
                mk = fraction_result['mann_kendall']
                sen = fraction_result['sen_slope']
                
                summary_data.append({
                    'Mois': MONTH_NAMES[month],
                    'Fraction': self.class_labels[fraction],
                    'N_obs': fraction_result['n_obs'],
                    'Tendance': mk['trend'],
                    'P_value': mk['p_value'],
                    'Significativité': get_significance_marker(mk['p_value']),
                    'Pente_Sen_decade': sen['slope_per_decade'],
                    'Tau': mk['tau']
                })
        
        return pd.DataFrame(summary_data)
    
    def print_seasonal_summary(self, variable='mean'):
        """
        Affiche un résumé des analyses saisonnières
        """
        print_section_header("Résumé des analyses saisonnières", level=2)
        
        if f'monthly_trends_{variable}' not in self.results:
            print("❌ Analyses mensuelles non effectuées")
            return
        
        monthly_results = self.results[f'monthly_trends_{variable}']
        
        print("📊 Tendances significatives par mois:")
        
        for month, month_result in monthly_results.items():
            month_name = MONTH_NAMES[month]
            significant_count = 0
            
            print(f"\n📅 {month_name}:")
            
            for fraction, fraction_result in month_result['fractions'].items():
                mk = fraction_result['mann_kendall']
                sen = fraction_result['sen_slope']
                
                if mk['p_value'] < 0.05:
                    significant_count += 1
                    trend_symbol = '📈' if mk['trend'] == 'increasing' else '📉'
                    significance = get_significance_marker(mk['p_value'])
                    
                    print(f"  {trend_symbol} {self.class_labels[fraction]}: "
                          f"{mk['trend']} {significance} "
                          f"({sen['slope_per_decade']:.6f}/décennie)")
            
            if significant_count == 0:
                print(f"  ➡️  Aucune tendance significative détectée")
    
    def calculate_monthly_statistics(self, fraction, variable='mean'):
        """
        Calculate monthly statistics for a specific fraction
        
        Args:
            fraction (str): Fraction class name
            variable (str): Variable to analyze ('mean' or 'median')
            
        Returns:
            dict: Monthly statistics (mean, std, count for each month)
        """
        if self.data is None:
            return None
        
        col_name = f"{fraction}_{variable}"
        if col_name not in self.data.columns:
            return None
        
        # Filter data and group by month
        data = self.data[['month', col_name]].dropna()
        monthly_stats = data.groupby('month')[col_name].agg(['mean', 'std', 'count']).reset_index()
        
        # Convert to dictionary format
        result = {
            'mean': monthly_stats['mean'].tolist(),
            'std': monthly_stats['std'].tolist(),
            'count': monthly_stats['count'].tolist(),
            'months': monthly_stats['month'].tolist()
        }
        
        return result
    
    def calculate_seasonal_statistics(self, fraction, variable='mean'):
        """
        Calculate comprehensive seasonal statistics for a fraction
        
        Args:
            fraction (str): Fraction class name
            variable (str): Variable to analyze
            
        Returns:
            dict: Comprehensive seasonal statistics
        """
        monthly_stats = self.calculate_monthly_statistics(fraction, variable)
        
        if monthly_stats is None:
            return None
        
        # Calculate seasonal patterns
        monthly_means = monthly_stats['mean']
        
        result = {
            'monthly_means': {i+1: val for i, val in enumerate(monthly_means) if i < 12},
            'seasonal_amplitude': max(monthly_means) - min(monthly_means) if monthly_means else 0,
            'peak_month': monthly_stats['months'][monthly_means.index(max(monthly_means))] if monthly_means else None,
            'low_month': monthly_stats['months'][monthly_means.index(min(monthly_means))] if monthly_means else None
        }
        
        return result