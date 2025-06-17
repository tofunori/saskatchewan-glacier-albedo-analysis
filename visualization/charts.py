"""
Générateur de graphiques pour l'analyse des tendances d'albédo
=============================================================

Ce module crée les visualisations principales : aperçu des tendances,
patterns saisonniers, corrélations et autres graphiques analytiques.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from config import (FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS, PLOT_STYLES,
                     TREND_SYMBOLS, get_significance_marker, OUTPUT_DIR)
from utils.helpers import print_section_header, format_pvalue, ensure_directory_exists
import os

class ChartGenerator:
    """
    Générateur pour toutes les visualisations principales
    """
    
    def __init__(self, data_handler):
        """
        Initialise le générateur de graphiques
        
        Args:
            data_handler: Instance d'AlbedoDataHandler avec données chargées
        """
        self.data_handler = data_handler
        self.data = data_handler.data
        self.fraction_classes = FRACTION_CLASSES
        self.class_labels = CLASS_LABELS
        
    def create_trend_overview_graph(self, trend_results, variable='mean', save_path=None):
        """
        Crée un graphique d'aperçu des tendances pour toutes les fractions
        
        Args:
            trend_results (dict): Résultats des analyses de tendances
            variable (str): Variable analysée
            save_path (str, optional): Chemin pour sauvegarder
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        print_section_header("Création du graphique d'aperçu des tendances", level=3)
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'Aperçu des Tendances d\'Albédo par Fraction - {variable.title()}', 
                     fontsize=16, fontweight='bold')
        
        axes = axes.flatten()
        
        for idx, fraction in enumerate(self.fraction_classes):
            ax = axes[idx]
            
            if fraction not in trend_results or trend_results[fraction].get('error', False):
                ax.text(0.5, 0.5, f'Pas de données\n{self.class_labels[fraction]}', 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, bbox=dict(boxstyle='round', facecolor='lightgray'))
                ax.set_title(self.class_labels[fraction])
                continue
            
            result = trend_results[fraction]
            times = result['data']['times']
            values = result['data']['values']
            
            # Données et ligne de tendance
            ax.scatter(times, values, alpha=0.6, s=20, 
                      color=FRACTION_COLORS.get(fraction, 'blue'))
            
            # Ligne de tendance Sen
            sen_slope = result['sen_slope']['slope']
            sen_intercept = result['sen_slope']['intercept']
            
            if not np.isnan(sen_slope):
                trend_line = sen_slope * times + sen_intercept
                ax.plot(times, trend_line, color='red', linewidth=2, alpha=0.8,
                       label=f'Pente: {sen_slope*10:.6f}/décennie')
            
            # Informations sur la tendance
            mk = result['mann_kendall']
            trend_symbol = TREND_SYMBOLS.get(mk['trend'], '❓')
            significance = get_significance_marker(mk['p_value'])
            
            title = f"{self.class_labels[fraction]}\n{trend_symbol} {mk['trend']} {significance}"
            ax.set_title(title, fontsize=10)
            ax.set_xlabel('Année')
            ax.set_ylabel('Albédo')
            ax.grid(True, alpha=0.3)
            
            if not np.isnan(sen_slope):
                ax.legend(fontsize=8)
        
        # Supprimer le subplot vide
        if len(self.fraction_classes) < len(axes):
            axes[-1].remove()
        
        plt.tight_layout()
        
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, f'trend_overview_{variable}.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Aperçu des tendances sauvegardé: {save_path}")
        
        plt.close()
        
        return save_path
    
    def create_seasonal_patterns_graph(self, variable='mean', save_path=None):
        """
        Crée un graphique des patterns saisonniers
        
        Args:
            variable (str): Variable à analyser
            save_path (str, optional): Chemin pour sauvegarder
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        print_section_header("Patterns saisonniers", level=3)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Patterns Saisonniers - Albédo {variable.title()}', 
                     fontsize=16, fontweight='bold')
        
        # Graphique 1: Évolution mensuelle moyenne
        ax1 = axes[0, 0]
        
        for fraction in self.fraction_classes:
            col_name = f"{fraction}_{variable}"
            if col_name in self.data.columns:
                monthly_means = self.data.groupby('month')[col_name].mean()
                ax1.plot(monthly_means.index, monthly_means.values, 
                        marker='o', linewidth=2, label=self.class_labels[fraction],
                        color=FRACTION_COLORS.get(fraction, 'gray'))
        
        ax1.set_title('Moyennes Mensuelles par Fraction')
        ax1.set_xlabel('Mois')
        ax1.set_ylabel('Albédo Moyen')
        ax1.set_xticks([6, 7, 8, 9])
        ax1.set_xticklabels(['Juin', 'Juillet', 'Août', 'Sept'])
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Graphique 2: Boxplot par mois pour la fraction pure
        ax2 = axes[0, 1]
        
        main_fraction = 'pure_ice'
        col_name = f"{main_fraction}_{variable}"
        
        if col_name in self.data.columns:
            monthly_data = []
            month_labels = []
            
            for month in [6, 7, 8, 9]:
                month_values = self.data[self.data['month'] == month][col_name].dropna()
                if len(month_values) > 0:
                    monthly_data.append(month_values)
                    month_labels.append(f"{month}")
            
            if monthly_data:
                bp = ax2.boxplot(monthly_data, labels=month_labels, patch_artist=True)
                colors = ['lightcoral', 'lightblue', 'lightgreen', 'lightyellow']
                for patch, color in zip(bp['boxes'], colors):
                    patch.set_facecolor(color)
                    patch.set_alpha(0.7)
        
        ax2.set_title(f'Distribution Mensuelle - {self.class_labels[main_fraction]}')
        ax2.set_xlabel('Mois')
        ax2.set_ylabel('Albédo')
        ax2.grid(True, alpha=0.3)
        
        # Graphique 3: Heatmap saisonnière
        ax3 = axes[1, 0]
        
        # Créer un pivot table pour la heatmap
        pivot_data = self.data.pivot_table(
            values=f"{main_fraction}_{variable}", 
            index=self.data['date'].dt.year, 
            columns=self.data['date'].dt.month, 
            aggfunc='mean'
        )
        
        if not pivot_data.empty:
            sns.heatmap(pivot_data, cmap='Blues', annot=False, 
                       cbar_kws={'label': 'Albédo'}, ax=ax3)
        
        ax3.set_title('Heatmap Année-Mois')
        ax3.set_xlabel('Mois')
        ax3.set_ylabel('Année')
        
        # Graphique 4: Variabilité saisonnière
        ax4 = axes[1, 1]
        
        for fraction in self.fraction_classes:
            col_name = f"{fraction}_{variable}"
            if col_name in self.data.columns:
                monthly_std = self.data.groupby('month')[col_name].std()
                ax4.plot(monthly_std.index, monthly_std.values, 
                        marker='s', linewidth=2, label=self.class_labels[fraction],
                        color=FRACTION_COLORS.get(fraction, 'gray'))
        
        ax4.set_title('Variabilité Mensuelle (Écart-type)')
        ax4.set_xlabel('Mois')
        ax4.set_ylabel('Écart-type')
        ax4.set_xticks([6, 7, 8, 9])
        ax4.set_xticklabels(['Juin', 'Juillet', 'Août', 'Sept'])
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, f'seasonal_patterns_{variable}.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Patterns saisonniers sauvegardés: {save_path}")
        
        plt.close()
        
        return save_path
    
    def create_correlation_matrix_graph(self, variable='mean', save_path=None):
        """
        Crée une matrice de corrélation entre les fractions
        
        Args:
            variable (str): Variable à analyser
            save_path (str, optional): Chemin pour sauvegarder
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        print_section_header("Matrice de corrélation entre fractions", level=3)
        
        # Préparer les données pour la matrice de corrélation
        correlation_data = {}
        
        for fraction in self.fraction_classes:
            col_name = f"{fraction}_{variable}"
            if col_name in self.data.columns:
                correlation_data[self.class_labels[fraction]] = self.data[col_name]
        
        if len(correlation_data) < 2:
            print("❌ Pas assez de fractions pour créer une matrice de corrélation")
            return None
        
        corr_df = pd.DataFrame(correlation_data)
        correlation_matrix = corr_df.corr()
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(10, 8))
        
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        
        sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm', 
                   center=0, square=True, linewidths=0.5, cbar_kws={"shrink": .8},
                   ax=ax)
        
        ax.set_title(f'Matrice de Corrélation - Albédo {variable.title()} entre Fractions', 
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, f'correlation_matrix_{variable}.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Matrice de corrélation sauvegardée: {save_path}")
        
        plt.close()
        
        return save_path
    
    def create_time_series_graph(self, fraction, variable='mean', save_path=None):
        """
        Crée un graphique détaillé de série temporelle pour une fraction
        
        Args:
            fraction (str): Fraction à analyser
            variable (str): Variable à analyser
            save_path (str, optional): Chemin pour sauvegarder
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        print_section_header(f"Série temporelle - {self.class_labels[fraction]}", level=3)
        
        try:
            fraction_data = self.data_handler.get_fraction_data(fraction, variable, dropna=True)
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction des données: {e}")
            return None
        
        if len(fraction_data) == 0:
            print("❌ Pas de données disponibles")
            return None
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle(f'Série Temporelle - {self.class_labels[fraction]} ({variable.title()})', 
                     fontsize=14, fontweight='bold')
        
        # Graphique 1: Série complète
        dates = fraction_data['date']
        values = fraction_data['value']
        
        ax1.plot(dates, values, alpha=0.7, linewidth=1, color='blue')
        ax1.scatter(dates, values, alpha=0.5, s=15, color='darkblue')
        
        # Moyennes mobiles
        if len(values) > 30:
            # Moyenne mobile 30 jours
            rolling_30 = pd.Series(values.values, index=dates).rolling(window=30).mean()
            ax1.plot(dates, rolling_30, color='red', linewidth=2, alpha=0.8, 
                    label='Moyenne mobile 30 jours')
        
        ax1.set_title('Série Temporelle Complète')
        ax1.set_ylabel('Albédo')
        ax1.grid(True, alpha=0.3)
        if len(values) > 30:
            ax1.legend()
        
        # Graphique 2: Évolution annuelle
        fraction_data['year'] = fraction_data['date'].dt.year
        yearly_stats = fraction_data.groupby('year')['value'].agg(['mean', 'std', 'count'])
        
        ax2.errorbar(yearly_stats.index, yearly_stats['mean'], 
                    yerr=yearly_stats['std'], fmt='o-', capsize=5,
                    color='green', alpha=0.8, linewidth=2)
        
        # Ajouter les comptes d'observations
        for year, stats in yearly_stats.iterrows():
            ax2.text(year, stats['mean'] + stats['std'] + 0.01, 
                    f"n={stats['count']}", ha='center', va='bottom', fontsize=8)
        
        ax2.set_title('Moyennes Annuelles avec Écart-types')
        ax2.set_xlabel('Année')
        ax2.set_ylabel('Albédo Moyen')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, f'timeseries_{fraction}_{variable}.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Série temporelle sauvegardée: {save_path}")
        
        plt.close()
        
        return save_path
    
    def create_summary_dashboard(self, basic_results, variable='mean', save_path=None):
        """
        Crée un dashboard de résumé avec les graphiques principaux
        
        Args:
            basic_results (dict): Résultats des analyses de base
            variable (str): Variable analysée
            save_path (str, optional): Chemin pour sauvegarder
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        print_section_header("Création du dashboard de résumé", level=2)
        
        fig = plt.figure(figsize=(20, 16))
        fig.suptitle(f'Dashboard Résumé - Analyse Tendances Albédo {variable.title()}', 
                     fontsize=18, fontweight='bold')
        
        # Layout en grille
        gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
        
        # 1. Graphique des tendances principales (2x2)
        ax1 = fig.add_subplot(gs[0:2, 0:2])
        self._plot_main_trends(ax1, basic_results, variable)
        
        # 2. Statistiques de significativité (1x2)
        ax2 = fig.add_subplot(gs[0, 2:4])
        self._plot_significance_summary(ax2, basic_results)
        
        # 3. Pentes de Sen (1x2)
        ax3 = fig.add_subplot(gs[1, 2:4])
        self._plot_sen_slopes(ax3, basic_results)
        
        # 4. Série temporelle principale (2x2)
        ax4 = fig.add_subplot(gs[2:4, 0:2])
        self._plot_main_timeseries(ax4, variable)
        
        # 5. Patterns saisonniers (1x2)
        ax5 = fig.add_subplot(gs[2, 2:4])
        self._plot_seasonal_summary(ax5, variable)
        
        # 6. Métadonnées (1x2)
        ax6 = fig.add_subplot(gs[3, 2:4])
        self._plot_metadata_summary(ax6)
        
        if save_path is None:
            ensure_directory_exists(OUTPUT_DIR)
            save_path = os.path.join(OUTPUT_DIR, f'dashboard_summary_{variable}.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Dashboard sauvegardé: {save_path}")
        
        plt.close()
        
        return save_path
    
    def _plot_main_trends(self, ax, basic_results, variable):
        """Graphique principal des tendances"""
        ax.set_title('Tendances Principales par Fraction', fontweight='bold')
        
        for i, fraction in enumerate(self.fraction_classes):
            if fraction in basic_results and not basic_results[fraction].get('error', False):
                result = basic_results[fraction]
                times = result['data']['times']
                values = result['data']['values']
                
                # Scatter plot
                ax.scatter(times, values, alpha=0.4, s=10, 
                          color=FRACTION_COLORS.get(fraction, 'gray'))
                
                # Ligne de tendance
                sen_slope = result['sen_slope']['slope']
                sen_intercept = result['sen_slope']['intercept']
                
                if not np.isnan(sen_slope):
                    trend_line = sen_slope * times + sen_intercept
                    ax.plot(times, trend_line, color=FRACTION_COLORS.get(fraction, 'gray'), 
                           linewidth=2, alpha=0.8, label=self.class_labels[fraction])
        
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Année')
        ax.set_ylabel('Albédo')
    
    def _plot_significance_summary(self, ax, basic_results):
        """Graphique de résumé de significativité"""
        trends = {'increasing': 0, 'decreasing': 0, 'no trend': 0}
        significant = 0
        
        for fraction, result in basic_results.items():
            if not result.get('error', False):
                trend = result['mann_kendall']['trend']
                p_value = result['mann_kendall']['p_value']
                
                trends[trend] += 1
                if p_value < 0.05:
                    significant += 1
        
        # Graphique en barres
        categories = ['Croissante', 'Décroissante', 'Pas de tendance', 'Significatives']
        values = [trends['increasing'], trends['decreasing'], trends['no trend'], significant]
        colors = ['green', 'red', 'gray', 'blue']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.7)
        ax.set_title('Résumé Statistique', fontweight='bold')
        ax.set_ylabel('Nombre de Fractions')
        
        # Ajouter les valeurs sur les barres
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                   str(value), ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylim(0, max(values) + 1)
    
    def _plot_sen_slopes(self, ax, basic_results):
        """Graphique des pentes de Sen"""
        fractions = []
        slopes = []
        colors = []
        
        for fraction, result in basic_results.items():
            if not result.get('error', False):
                slope = result['sen_slope']['slope_per_decade']
                if not np.isnan(slope):
                    fractions.append(self.class_labels[fraction][:10])
                    slopes.append(slope)
                    colors.append(FRACTION_COLORS.get(fraction, 'gray'))
        
        if fractions:
            bars = ax.barh(range(len(fractions)), slopes, color=colors, alpha=0.7)
            ax.axvline(x=0, color='black', linestyle='--', alpha=0.5)
            ax.set_title('Pentes de Sen (par décennie)', fontweight='bold')
            ax.set_xlabel('Pente')
            ax.set_yticks(range(len(fractions)))
            ax.set_yticklabels(fractions)
            ax.grid(True, alpha=0.3, axis='x')
    
    def _plot_main_timeseries(self, ax, variable):
        """Série temporelle principale"""
        main_fraction = 'pure_ice'
        col_name = f"{main_fraction}_{variable}"
        
        if col_name in self.data.columns:
            data_subset = self.data[['date', col_name]].dropna()
            ax.plot(data_subset['date'], data_subset[col_name], 
                   alpha=0.6, linewidth=1, color='blue')
            
            # Moyenne mobile
            if len(data_subset) > 30:
                rolling = data_subset.set_index('date')[col_name].rolling(window=30).mean()
                ax.plot(rolling.index, rolling.values, color='red', linewidth=2)
        
        ax.set_title(f'Série Temporelle - {self.class_labels[main_fraction]}', fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Albédo')
        ax.grid(True, alpha=0.3)
    
    def _plot_seasonal_summary(self, ax, variable):
        """Résumé saisonnier"""
        main_fraction = 'pure_ice'
        col_name = f"{main_fraction}_{variable}"
        
        if col_name in self.data.columns:
            monthly_means = self.data.groupby('month')[col_name].mean()
            ax.plot(monthly_means.index, monthly_means.values, 
                   marker='o', linewidth=3, color='blue')
            
            ax.set_title('Pattern Saisonnier', fontweight='bold')
            ax.set_xlabel('Mois')
            ax.set_ylabel('Albédo Moyen')
            ax.set_xticks([6, 7, 8, 9])
            ax.set_xticklabels(['Jun', 'Jul', 'Aug', 'Sep'])
            ax.grid(True, alpha=0.3)
    
    def _plot_metadata_summary(self, ax):
        """Résumé des métadonnées"""
        summary = self.data_handler.get_data_summary()
        
        ax.axis('off')
        
        # Informations textuelles
        info_text = f"""
MÉTADONNÉES DE L'ANALYSE

• Observations totales: {summary['total_observations']:,}
• Période: {summary['date_range']['start'].strftime('%Y-%m-%d')} 
  à {summary['date_range']['end'].strftime('%Y-%m-%d')}
• Années couvertes: {len(summary['years_covered'])} ans
• Mois analysés: {', '.join(map(str, summary['months_covered']))}

• Fractions disponibles: {len(summary['fractions_available'])}
• Génération: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """
        
        ax.text(0.05, 0.95, info_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))