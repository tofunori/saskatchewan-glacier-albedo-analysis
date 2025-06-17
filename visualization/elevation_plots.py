#!/usr/bin/env python3
"""
VISUALISATIONS FRACTION × ÉLÉVATION - Méthodologie Williamson & Menounos (2021)
===============================================================================

Module de visualisation pour les analyses d'albédo par fraction × élévation
suivant la méthodologie de Williamson & Menounos (2021).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration des graphiques
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ElevationPlotter:
    """
    Générateur de visualisations pour l'analyse fraction × élévation
    """
    
    def __init__(self, analyzer, output_dir=None):
        """
        Initialise le générateur de plots
        
        Args:
            analyzer: Instance d'ElevationAnalyzer avec données chargées
            output_dir: Répertoire de sortie (None = utilise celui de l'analyzer)
        """
        self.analyzer = analyzer
        self.output_dir = Path(output_dir) if output_dir else analyzer.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration des couleurs par zone d'élévation
        self.zone_colors = {
            'above_median': '#d62728',  # Rouge - zone haute
            'at_median': '#ff7f0e',     # Orange - zone médiane  
            'below_median': '#2ca02c'   # Vert - zone basse
        }
        
        # Configuration des styles par fraction
        self.fraction_styles = {
            'mostly_ice': {'linestyle': '--', 'marker': 'o', 'alpha': 0.7},
            'pure_ice': {'linestyle': '-', 'marker': 's', 'alpha': 0.9}
        }
        
        print(f"📊 ElevationPlotter initialisé")
        print(f"📁 Sortie: {self.output_dir}")
    
    def plot_elevation_trends_comparison(self, figsize=(14, 10)):
        """
        Graphique comparaison des tendances par zone d'élévation
        Style Williamson & Menounos
        """
        print("📈 Création graphique tendances par élévation...")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle('Tendances d\'albédo par zone d\'élévation\n(Méthodologie Williamson & Menounos 2021)', 
                     fontsize=16, fontweight='bold')
        
        # 1. Pentes par zone d'élévation
        zone_data = []
        for combo, trend in self.analyzer.trends.items():
            zone_data.append({
                'Zone': trend['elevation_zone'],
                'Fraction': trend['fraction_class'],
                'Slope': trend['sens_slope'],
                'Slope_per_decade': trend['sens_slope_per_decade'],
                'P_value': trend['mk_p_value'],
                'Significant': trend['mk_significant']
            })
        
        zone_df = pd.DataFrame(zone_data)
        
        # Graphique en barres des pentes par zone
        zone_means = zone_df.groupby('Zone')['Slope'].mean()
        
        # Améliorer les labels des zones
        zone_labels = {
            'above_median': 'Zone haute\n(>2727m)',
            'at_median': 'Zone médiane\n(±100m)',
            'below_median': 'Zone basse\n(<2527m)'
        }
        
        # Créer les barres avec les labels améliorés
        x_labels = [zone_labels.get(zone, zone) for zone in zone_means.index]
        bars = ax1.bar(range(len(zone_means)), zone_means.values, 
                      color=[self.zone_colors[z] for z in zone_means.index],
                      alpha=0.7, edgecolor='black', linewidth=1)
        
        # Définir les labels de l'axe x
        ax1.set_xticks(range(len(zone_means)))
        ax1.set_xticklabels(x_labels)
        
        ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax1.set_title('A) Pente moyenne Sen par zone d\'élévation', fontweight='bold')
        ax1.set_ylabel('Changement albédo par an')
        ax1.set_xlabel('Zone d\'élévation')
        
        # Ajouter valeurs sur les barres (à l'intérieur)
        for bar, value in zip(bars, zone_means.values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height/2,
                    f'{value:.4f}', ha='center', va='center',
                    fontweight='bold', fontsize=10, color='white')
        
        # 2. Séries temporelles par zone (pure_ice seulement)
        for zone in self.analyzer.elevation_zones:
            combo = f'pure_ice_{zone}'
            if combo in self.analyzer.valid_combinations:
                mean_col = f"{combo}_mean"
                if mean_col in self.analyzer.annual_data.columns:
                    data = self.analyzer.annual_data[self.analyzer.annual_data[mean_col].notna()]
                    ax2.plot(data['year'], data[mean_col], 
                            color=self.zone_colors[zone], 
                            label=f'Pure ice {zone.replace("_", " ")}',
                            **self.fraction_styles['pure_ice'])
        
        ax2.set_title('B) Évolution albédo pure ice par zone', fontweight='bold')
        ax2.set_xlabel('Année')
        ax2.set_ylabel('Albédo moyen annuel')
        ax2.legend(loc='lower right')
        ax2.grid(True, alpha=0.3)
        
        # 3. Comparaison fractions par zone (at_median)
        for fraction in self.analyzer.fraction_classes:
            combo = f'{fraction}_at_median'
            if combo in self.analyzer.valid_combinations:
                mean_col = f"{combo}_mean"
                if mean_col in self.analyzer.annual_data.columns:
                    data = self.analyzer.annual_data[self.analyzer.annual_data[mean_col].notna()]
                    ax3.plot(data['year'], data[mean_col],
                            color='orange',  # Zone médiane
                            label=f'{fraction.replace("_", " ").title()}',
                            **self.fraction_styles[fraction])
        
        ax3.set_title('C) Comparaison fractions (zone ±100m médiane)', fontweight='bold')
        ax3.set_xlabel('Année')
        ax3.set_ylabel('Albédo moyen annuel')
        ax3.legend(loc='lower left')
        ax3.grid(True, alpha=0.3)
        
        # 4. Significativité statistique
        sig_data = zone_df.groupby('Zone')['Significant'].sum().reindex(self.analyzer.elevation_zones, fill_value=0)
        total_data = zone_df.groupby('Zone').size().reindex(self.analyzer.elevation_zones, fill_value=1)
        percent_sig = (sig_data / total_data) * 100
        
        bars = ax4.bar(percent_sig.index, percent_sig.values,
                      color=[self.zone_colors[z] for z in percent_sig.index],
                      alpha=0.7, edgecolor='black', linewidth=1)
        
        ax4.set_title('D) Tendances significatives par zone (p<0.05)', fontweight='bold')
        ax4.set_ylabel('Pourcentage de tendances significatives')
        ax4.set_xlabel('Zone d\'élévation')
        ax4.set_ylim(0, 105)
        
        # Ajouter valeurs sur les barres
        for bar, value in zip(bars, percent_sig.values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 2,
                    f'{value:.0f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        # Sauvegarder
        save_path = self.output_dir / "elevation_trends_comparison.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Graphique sauvegardé: {save_path}")
        
        plt.show()
        return fig
    
    def plot_transient_snowline_analysis(self, figsize=(12, 8)):
        """
        Graphique spécifique pour l'analyse de la ligne de neige transitoire
        """
        print("🏔️ Création graphique ligne de neige transitoire...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        fig.suptitle('Analyse ligne de neige transitoire - Saskatchewan Glacier\n(Williamson & Menounos 2021)', 
                     fontsize=14, fontweight='bold')
        
        # 1. Pente vs élévation approximative
        elevation_info = self.analyzer.elevation_analysis['elevation_info']
        glacier_median = elevation_info['glacier_median']
        
        # Calculer élévations approximatives des zones
        zone_elevations = {
            'below_median': glacier_median - 150,
            'at_median': glacier_median,
            'above_median': glacier_median + 150
        }
        
        # Extraire données pour pure_ice
        slopes_data = []
        for zone in self.analyzer.elevation_zones:
            combo = f'pure_ice_{zone}'
            if combo in self.analyzer.trends:
                trend = self.analyzer.trends[combo]
                slopes_data.append({
                    'zone': zone,
                    'elevation': zone_elevations[zone],
                    'slope': trend['sens_slope'],
                    'slope_decade': trend['sens_slope_per_decade'],
                    'significant': trend['mk_significant']
                })
        
        slopes_df = pd.DataFrame(slopes_data)
        
        if not slopes_df.empty:
            # Graphique pente vs élévation
            colors = [self.zone_colors[zone] for zone in slopes_df['zone']]
            sizes = [100 if sig else 60 for sig in slopes_df['significant']]
            
            scatter = ax1.scatter(slopes_df['elevation'], slopes_df['slope_decade'], 
                                c=colors, s=sizes, alpha=0.8, edgecolors='black')
            
            # Ligne de tendance
            z = np.polyfit(slopes_df['elevation'], slopes_df['slope_decade'], 1)
            p = np.poly1d(z)
            x_trend = np.linspace(slopes_df['elevation'].min(), slopes_df['elevation'].max(), 100)
            ax1.plot(x_trend, p(x_trend), 'k--', alpha=0.5, label=f'Tendance: {z[0]:.6f}x + {z[1]:.3f}')
            
            # Ligne médiane glacier
            ax1.axvline(x=glacier_median, color='red', linestyle=':', alpha=0.7, 
                       label=f'Médiane glacier ({glacier_median:.0f}m)')
            ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            ax1.set_title('A) Pente Sen vs Élévation (Pure ice)', fontweight='bold')
            ax1.set_xlabel('Élévation approximative (m)')
            ax1.set_ylabel('Changement albédo par décennie')
            ax1.legend(loc='upper right')
            ax1.grid(True, alpha=0.3)
            
            # Annoter les points
            for _, row in slopes_df.iterrows():
                ax1.annotate(row['zone'].replace('_', '\n'), 
                           (row['elevation'], row['slope_decade']),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=8, ha='left')
        
        # 2. Test hypothèse Williamson & Menounos
        transient = self.analyzer.elevation_analysis['transient_snowline']
        zone_slopes = transient['zone_slopes']
        
        # Graphique en barres avec mise en évidence de la zone de déclin maximal
        zones = list(zone_slopes.keys())
        slopes = list(zone_slopes.values())
        colors_bars = ['red' if zone == transient['strongest_decline_zone'] else self.zone_colors[zone] 
                      for zone in zones]
        
        bars = ax2.bar(zones, slopes, color=colors_bars, alpha=0.7, edgecolor='black', linewidth=1)
        
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax2.set_title('B) Test hypothèse ligne de neige transitoire', fontweight='bold')
        ax2.set_ylabel('Pente Sen moyenne par zone')
        ax2.set_xlabel('Zone d\'élévation')
        
        # Ajouter valeurs et annotations
        for bar, value, zone in zip(bars, slopes, zones):
            height = bar.get_height()
            # Valeur numérique au centre de la barre
            ax2.text(bar.get_x() + bar.get_width()/2., height/2,
                    f'{value:.4f}', ha='center', va='center',
                    fontweight='bold', fontsize=10, color='white')
            
            # Annotation "Déclin maximal" en bas de la barre pour éviter l'overlap
            if zone == transient['strongest_decline_zone']:
                ax2.text(bar.get_x() + bar.get_width()/2., -0.008,
                        'Déclin\nmaximal', ha='center', va='top',
                        fontsize=8, fontweight='bold', color='red')
        
        # Ajouter résultat du test
        hypothesis_text = f"Hypothèse supportée: {transient['hypothesis_supported']}\n"
        hypothesis_text += f"Zone déclin maximal: {transient['strongest_decline_zone']}"
        ax2.text(0.02, 0.02, hypothesis_text, transform=ax2.transAxes, 
                fontsize=10, verticalalignment='bottom', horizontalalignment='left',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        plt.tight_layout()
        
        # Sauvegarder
        save_path = self.output_dir / "transient_snowline_analysis.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Graphique sauvegardé: {save_path}")
        
        plt.show()
        return fig
    
    def plot_time_series_matrix(self, figsize=(16, 12)):
        """
        Matrice de séries temporelles pour toutes les combinaisons
        """
        print("📅 Création matrice séries temporelles...")
        
        # Organiser en grille: fractions en lignes, zones en colonnes
        fig, axes = plt.subplots(len(self.analyzer.fraction_classes), len(self.analyzer.elevation_zones), 
                                figsize=figsize)
        fig.suptitle('Séries temporelles albédo par fraction × élévation\n(Saskatchewan Glacier 2010-2024)', 
                     fontsize=16, fontweight='bold')
        
        for i, fraction in enumerate(self.analyzer.fraction_classes):
            for j, zone in enumerate(self.analyzer.elevation_zones):
                ax = axes[i, j] if len(self.analyzer.fraction_classes) > 1 else axes[j]
                
                combo = f'{fraction}_{zone}'
                if combo in self.analyzer.valid_combinations:
                    mean_col = f"{combo}_mean"
                    
                    # Données annuelles
                    if mean_col in self.analyzer.annual_data.columns:
                        annual_data = self.analyzer.annual_data[
                            self.analyzer.annual_data[mean_col].notna()
                        ]
                        
                        if len(annual_data) > 0:
                            ax.plot(annual_data['year'], annual_data[mean_col], 
                                   color=self.zone_colors[zone],
                                   **self.fraction_styles[fraction],
                                   linewidth=2)
                            
                            # Ligne de tendance si significative
                            if combo in self.analyzer.trends and self.analyzer.trends[combo]['mk_significant']:
                                trend = self.analyzer.trends[combo]
                                years = annual_data['year'].values
                                trend_line = trend['linear_slope'] * years + (
                                    annual_data[mean_col].iloc[0] - trend['linear_slope'] * years[0]
                                )
                                ax.plot(years, trend_line, 'r--', alpha=0.6, linewidth=1)
                
                # Configuration de l'axe
                ax.set_title(f'{fraction.replace("_", " ").title()}\n{zone.replace("_", " ").title()}',
                           fontweight='bold', fontsize=10)
                ax.grid(True, alpha=0.3)
                ax.set_ylim(0.3, 0.9)
                
                # Labels seulement sur les bords
                if i == len(self.analyzer.fraction_classes) - 1:
                    ax.set_xlabel('Année')
                if j == 0:
                    ax.set_ylabel('Albédo moyen')
                
                # Ajouter info tendance
                if combo in self.analyzer.trends:
                    trend = self.analyzer.trends[combo]
                    trend_text = f"Slope: {trend['sens_slope']:.4f}"
                    if trend['mk_significant']:
                        trend_text += "*"
                    ax.text(0.05, 0.95, trend_text, transform=ax.transAxes,
                           fontsize=8, verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
        
        plt.tight_layout()
        
        # Sauvegarder
        save_path = self.output_dir / "time_series_matrix.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Graphique sauvegardé: {save_path}")
        
        plt.show()
        return fig
    
    def plot_seasonal_patterns(self, figsize=(14, 10)):
        """
        Analyse des patterns saisonniers par zone d'élévation
        """
        print("🗓️ Création graphique patterns saisonniers...")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle('Patterns saisonniers par zone d\'élévation\n(Pure ice - Saskatchewan Glacier)', 
                     fontsize=14, fontweight='bold')
        
        # Préparer données mensuelles
        monthly_data = self.analyzer.data.copy()
        monthly_data = monthly_data[monthly_data['month'].between(6, 9)]  # Saison été
        
        # 1. Évolution saisonnière moyenne par zone
        for zone in self.analyzer.elevation_zones:
            combo = f'pure_ice_{zone}'
            if combo in self.analyzer.valid_combinations:
                mean_col = f"{combo}_mean"
                if mean_col in monthly_data.columns:
                    monthly_avg = monthly_data.groupby('month')[mean_col].mean()
                    ax1.plot(monthly_avg.index, monthly_avg.values,
                           color=self.zone_colors[zone], 
                           marker='o', linewidth=2, markersize=6,
                           label=f'{zone.replace("_", " ").title()}')
        
        ax1.set_title('A) Évolution saisonnière moyenne (2010-2024)', fontweight='bold')
        ax1.set_xlabel('Mois')
        ax1.set_ylabel('Albédo moyen')
        ax1.set_xticks([6, 7, 8, 9])
        ax1.set_xticklabels(['Juin', 'Juillet', 'Août', 'Septembre'])
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Variabilité saisonnière (écart-type)
        for zone in self.analyzer.elevation_zones:
            combo = f'pure_ice_{zone}'
            if combo in self.analyzer.valid_combinations:
                mean_col = f"{combo}_mean"
                if mean_col in monthly_data.columns:
                    monthly_std = monthly_data.groupby('month')[mean_col].std()
                    ax2.plot(monthly_std.index, monthly_std.values,
                           color=self.zone_colors[zone], 
                           marker='s', linewidth=2, markersize=6,
                           label=f'{zone.replace("_", " ").title()}')
        
        ax2.set_title('B) Variabilité saisonnière (écart-type)', fontweight='bold')
        ax2.set_xlabel('Mois')
        ax2.set_ylabel('Écart-type albédo')
        ax2.set_xticks([6, 7, 8, 9])
        ax2.set_xticklabels(['Juin', 'Juillet', 'Août', 'Septembre'])
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Heatmap albédo par mois × année (zone at_median)
        pivot_data = monthly_data.pivot_table(
            values='pure_ice_at_median_mean',
            index='year',
            columns='month',
            aggfunc='mean'
        )
        
        im = ax3.imshow(pivot_data.values, cmap='RdYlBu_r', aspect='auto', vmin=0.3, vmax=0.9)
        ax3.set_title('C) Heatmap albédo (Zone ±100m médiane)', fontweight='bold')
        ax3.set_xlabel('Mois')
        ax3.set_ylabel('Année')
        ax3.set_xticks(range(len(pivot_data.columns)))
        ax3.set_xticklabels(['Juin', 'Juillet', 'Août', 'Septembre'])
        ax3.set_yticks(range(0, len(pivot_data.index), 3))
        ax3.set_yticklabels(pivot_data.index[::3])
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax3)
        cbar.set_label('Albédo')
        
        # 4. Différence juin-septembre par zone
        june_sept_diff = []
        for zone in self.analyzer.elevation_zones:
            combo = f'pure_ice_{zone}'
            if combo in self.analyzer.valid_combinations:
                mean_col = f"{combo}_mean"
                if mean_col in monthly_data.columns:
                    june_data = monthly_data[monthly_data['month'] == 6][mean_col].mean()
                    sept_data = monthly_data[monthly_data['month'] == 9][mean_col].mean()
                    diff = june_data - sept_data
                    june_sept_diff.append({'zone': zone, 'difference': diff})
        
        if june_sept_diff:
            diff_df = pd.DataFrame(june_sept_diff)
            bars = ax4.bar(diff_df['zone'], diff_df['difference'],
                          color=[self.zone_colors[z] for z in diff_df['zone']],
                          alpha=0.7, edgecolor='black', linewidth=1)
            
            ax4.set_title('D) Différence albédo Juin-Septembre', fontweight='bold')
            ax4.set_ylabel('Différence albédo (Juin - Septembre)')
            ax4.set_xlabel('Zone d\'élévation')
            ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Ajouter valeurs sur les barres
            for bar, value in zip(bars, diff_df['difference']):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                        f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        # Sauvegarder
        save_path = self.output_dir / "seasonal_patterns.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Graphique sauvegardé: {save_path}")
        
        plt.show()
        return fig
    
    def create_all_plots(self):
        """Crée tous les graphiques pour l'analyse"""
        print(f"\n🎨 Génération de tous les graphiques...")
        
        plots_created = []
        
        try:
            fig1 = self.plot_elevation_trends_comparison()
            plots_created.append("elevation_trends_comparison.png")
        except Exception as e:
            print(f"❌ Erreur graphique tendances: {e}")
        
        try:
            fig2 = self.plot_transient_snowline_analysis()
            plots_created.append("transient_snowline_analysis.png")
        except Exception as e:
            print(f"❌ Erreur graphique ligne de neige: {e}")
        
        try:
            fig3 = self.plot_time_series_matrix()
            plots_created.append("time_series_matrix.png")
        except Exception as e:
            print(f"❌ Erreur graphique séries temporelles: {e}")
        
        try:
            fig4 = self.plot_seasonal_patterns()
            plots_created.append("seasonal_patterns.png")
        except Exception as e:
            print(f"❌ Erreur graphique patterns saisonniers: {e}")
        
        print(f"\n✅ {len(plots_created)} graphiques créés:")
        for plot in plots_created:
            print(f"  📊 {plot}")
        
        return plots_created

def create_elevation_visualizations(analyzer, output_dir=None):
    """
    Crée toutes les visualisations pour l'analyse d'élévation
    
    Args:
        analyzer: Instance ElevationAnalyzer avec données et analyses
        output_dir: Répertoire de sortie (optionnel)
    
    Returns:
        ElevationPlotter: Instance configurée
    """
    plotter = ElevationPlotter(analyzer, output_dir)
    plots_created = plotter.create_all_plots()
    
    print(f"\n📊 Visualisations terminées:")
    print(f"📁 Répertoire: {plotter.output_dir}")
    print(f"🎨 Graphiques: {len(plots_created)}")
    
    return plotter

if __name__ == "__main__":
    # Test avec données exemple
    from analysis.elevation_analysis import run_elevation_analysis
    
    analyzer = run_elevation_analysis()
    plotter = create_elevation_visualizations(analyzer)