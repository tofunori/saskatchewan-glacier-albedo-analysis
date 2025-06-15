#!/usr/bin/env python3
"""
Saskatchewan Glacier Albedo Trend Analysis
==========================================

Script d'analyse statistique pour les données d'albédo du glacier Saskatchewan.
Effectue les tests de Mann-Kendall et calcule la pente de Sen pour détecter
les tendances temporelles dans les données d'albédo par fraction de couverture.

Auteur: Analyse automatisée Claude Code
Usage: python albedo_trend_analysis.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Imports pour l'analyse statistique
try:
    import pymannkendall as mk
    PYMANNKENDALL_AVAILABLE = True
except ImportError:
    print("⚠️  pymannkendall non installé. Installation: pip install pymannkendall")
    PYMANNKENDALL_AVAILABLE = False

from scipy import stats
from scipy.stats import theilslopes
import os

# Configuration des graphiques
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class SaskatchewanAlbedoAnalyzer:
    """
    Analyseur de tendances d'albédo pour le glacier Saskatchewan
    """
    
    def __init__(self, csv_path):
        """
        Initialise l'analyseur avec le fichier CSV
        
        Args:
            csv_path (str): Chemin vers le fichier CSV des données quotidiennes
        """
        self.csv_path = csv_path
        self.data = None
        self.fraction_classes = ['border', 'mixed_low', 'mixed_high', 'mostly_ice', 'pure_ice']
        self.class_labels = {
            'border': '0-25% (Bordure)',
            'mixed_low': '25-50% (Mixte bas)',
            'mixed_high': '50-75% (Mixte haut)',
            'mostly_ice': '75-90% (Majoritaire)',
            'pure_ice': '90-100% (Pur)'
        }
        self.results = {}
        
    def load_data(self):
        """
        Charge et prépare les données CSV
        """
        print("📊 Chargement des données...")
        
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Fichier non trouvé: {self.csv_path}")
        
        # Charger le CSV
        self.data = pd.read_csv(self.csv_path)
        
        # Convertir la date
        self.data['date'] = pd.to_datetime(self.data['date'])
        
        # Filtrer les données avec seuil minimum de pixels
        if 'min_pixels_threshold' in self.data.columns:
            initial_count = len(self.data)
            self.data = self.data[self.data['min_pixels_threshold'] == True]
            filtered_count = len(self.data)
            print(f"✓ Données filtrées: {filtered_count}/{initial_count} observations gardées")
        
        # Créer la saison
        self.data['month'] = self.data['date'].dt.month
        self.data['season_label'] = self.data['month'].map({
            6: 'Début été', 7: 'Début été',
            8: 'Mi-été', 
            9: 'Fin été'
        })
        
        print(f"✓ {len(self.data)} observations chargées")
        print(f"✓ Période: {self.data['date'].min().strftime('%Y-%m-%d')} à {self.data['date'].max().strftime('%Y-%m-%d')}")
        
        return self
    
    def calculate_trends(self, variable='mean'):
        """
        Calcule les tendances Mann-Kendall et pente de Sen pour chaque fraction
        
        Args:
            variable (str): Variable à analyser ('mean' ou 'median')
        """
        print(f"\n🔍 Analyse des tendances ({variable})...")
        
        results = {}
        
        for fraction in self.fraction_classes:
            col_name = f"{fraction}_{variable}"
            
            if col_name not in self.data.columns:
                print(f"⚠️  Colonne {col_name} non trouvée")
                continue
            
            # Préparer les données (supprimer les NaN)
            df_clean = self.data.dropna(subset=[col_name])
            
            if len(df_clean) < 10:
                print(f"⚠️  Pas assez de données pour {fraction}")
                continue
            
            # Données pour l'analyse
            values = df_clean[col_name].values
            time_data = df_clean['decimal_year'].values
            
            # Analyse Mann-Kendall
            if PYMANNKENDALL_AVAILABLE:
                mk_result = mk.original_test(values)
                mk_seasonal = mk.seasonal_test(values, period=12)
            else:
                # Fallback avec scipy
                mk_result = self._manual_mann_kendall(values)
                mk_seasonal = None
            
            # Pente de Sen
            sen_slope, sen_intercept, _, _ = theilslopes(values, time_data)
            
            # Régression linéaire pour comparaison
            linear_slope, linear_intercept, r_value, p_value, std_err = stats.linregress(time_data, values)
            
            # Stocker les résultats
            results[fraction] = {
                'n_observations': len(df_clean),
                'mean_albedo': np.mean(values),
                'std_albedo': np.std(values),
                'trend': mk_result.trend if PYMANNKENDALL_AVAILABLE else mk_result['trend'],
                'p_value': mk_result.p if PYMANNKENDALL_AVAILABLE else mk_result['p_value'],
                'tau': mk_result.Tau if PYMANNKENDALL_AVAILABLE else mk_result['tau'],
                'sen_slope': sen_slope,
                'sen_slope_per_year': sen_slope,
                'sen_slope_per_decade': sen_slope * 10,
                'linear_slope': linear_slope,
                'linear_r2': r_value**2,
                'linear_p': p_value,
                'seasonal_mk': mk_seasonal.trend if mk_seasonal else None,
                'seasonal_p': mk_seasonal.p if mk_seasonal else None
            }
            
            # Affichage des résultats
            trend_symbol = "📈" if sen_slope > 0 else "📉" if sen_slope < 0 else "➡️"
            significance = "***" if results[fraction]['p_value'] < 0.001 else "**" if results[fraction]['p_value'] < 0.01 else "*" if results[fraction]['p_value'] < 0.05 else ""
            
            print(f"  {trend_symbol} {self.class_labels[fraction]}:")
            print(f"    Tendance: {results[fraction]['trend']} {significance}")
            print(f"    Pente Sen: {sen_slope:.6f}/an ({sen_slope*10:.5f}/décennie)")
            print(f"    p-value: {results[fraction]['p_value']:.4f}")
            print(f"    Tau Kendall: {results[fraction]['tau']:.3f}")
        
        self.results[variable] = results
        return results
    
    def _manual_mann_kendall(self, data):
        """
        Implémentation manuelle du test Mann-Kendall si pymannkendall n'est pas disponible
        """
        n = len(data)
        s = 0
        
        for i in range(n-1):
            for j in range(i+1, n):
                s += np.sign(data[j] - data[i])
        
        var_s = n * (n - 1) * (2 * n + 5) / 18
        
        if s > 0:
            z = (s - 1) / np.sqrt(var_s)
        elif s < 0:
            z = (s + 1) / np.sqrt(var_s)
        else:
            z = 0
        
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))
        tau = s / (n * (n - 1) / 2)
        
        if p_value < 0.05:
            trend = 'increasing' if s > 0 else 'decreasing'
        else:
            trend = 'no trend'
        
        return {
            'trend': trend,
            'p_value': p_value,
            'tau': tau,
            's': s,
            'z': z
        }
    
    def plot_trends(self, variable='mean', save_path=None):
        """
        Crée des graphiques des tendances
        """
        print(f"\n📊 Création des graphiques ({variable})...")
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'Tendances d\'albédo par fraction de couverture ({variable})', fontsize=16, fontweight='bold')
        
        # Couleurs pour chaque fraction
        colors = ['red', 'orange', 'gold', 'lightblue', 'blue']
        
        for i, fraction in enumerate(self.fraction_classes):
            row = i // 3
            col = i % 3
            ax = axes[row, col]
            
            col_name = f"{fraction}_{variable}"
            
            if col_name in self.data.columns and fraction in self.results[variable]:
                # Données
                data_clean = self.data.dropna(subset=[col_name])
                x = data_clean['decimal_year']
                y = data_clean[col_name]
                
                # Points de données
                ax.scatter(x, y, alpha=0.6, color=colors[i], s=20)
                
                # Ligne de tendance Sen
                results = self.results[variable][fraction]
                x_trend = np.array([x.min(), x.max()])
                y_trend = results['sen_slope'] * x_trend + (y.mean() - results['sen_slope'] * x.mean())
                
                trend_color = 'red' if results['sen_slope'] < 0 else 'green' if results['sen_slope'] > 0 else 'gray'
                ax.plot(x_trend, y_trend, color=trend_color, linewidth=2, 
                       label=f"Sen: {results['sen_slope']:.5f}/an")
                
                # Titre et labels
                significance = "***" if results['p_value'] < 0.001 else "**" if results['p_value'] < 0.01 else "*" if results['p_value'] < 0.05 else ""
                ax.set_title(f"{self.class_labels[fraction]} {significance}\np={results['p_value']:.4f}", fontweight='bold')
                ax.set_xlabel('Année')
                ax.set_ylabel(f'Albédo {variable}')
                ax.legend()
                ax.grid(True, alpha=0.3)
        
        # Supprimer le subplot vide
        fig.delaxes(axes[1, 2])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Graphique sauvé: {save_path}")
        
        plt.show()
    
    def create_summary_table(self, variable='mean'):
        """
        Crée un tableau de résumé des tendances
        """
        print(f"\n📋 Tableau de résumé ({variable})...")
        
        if variable not in self.results:
            print("⚠️  Calculer les tendances d'abord!")
            return None
        
        # Créer le DataFrame de résumé
        summary_data = []
        
        for fraction in self.fraction_classes:
            if fraction in self.results[variable]:
                result = self.results[variable][fraction]
                
                summary_data.append({
                    'Fraction': self.class_labels[fraction],
                    'N obs': result['n_observations'],
                    'Albédo moyen': f"{result['mean_albedo']:.3f}",
                    'Tendance': result['trend'],
                    'Pente Sen (/an)': f"{result['sen_slope']:.6f}",
                    'Pente Sen (/décennie)': f"{result['sen_slope_per_decade']:.5f}",
                    'Tau Kendall': f"{result['tau']:.3f}",
                    'p-value': f"{result['p_value']:.4f}",
                    'Significativité': "***" if result['p_value'] < 0.001 else "**" if result['p_value'] < 0.01 else "*" if result['p_value'] < 0.05 else "ns"
                })
        
        summary_df = pd.DataFrame(summary_data)
        print(summary_df.to_string(index=False))
        
        return summary_df
    
    def seasonal_analysis(self, variable='mean'):
        """
        Analyse saisonnière des tendances
        """
        print(f"\n🌤️  Analyse saisonnière ({variable})...")
        
        seasonal_results = {}
        
        for season in ['Début été', 'Mi-été', 'Fin été']:
            print(f"\n--- {season} ---")
            seasonal_data = self.data[self.data['season_label'] == season]
            
            if len(seasonal_data) < 10:
                print(f"Pas assez de données pour {season}")
                continue
            
            seasonal_results[season] = {}
            
            for fraction in self.fraction_classes:
                col_name = f"{fraction}_{variable}"
                
                if col_name not in seasonal_data.columns:
                    continue
                
                data_clean = seasonal_data.dropna(subset=[col_name])
                
                if len(data_clean) < 5:
                    continue
                
                values = data_clean[col_name].values
                time_data = data_clean['decimal_year'].values
                
                # Mann-Kendall
                if PYMANNKENDALL_AVAILABLE:
                    mk_result = mk.original_test(values)
                else:
                    mk_result = self._manual_mann_kendall(values)
                
                # Pente de Sen
                sen_slope, _, _, _ = theilslopes(values, time_data)
                
                seasonal_results[season][fraction] = {
                    'trend': mk_result.trend if PYMANNKENDALL_AVAILABLE else mk_result['trend'],
                    'p_value': mk_result.p if PYMANNKENDALL_AVAILABLE else mk_result['p_value'],
                    'sen_slope': sen_slope,
                    'n_obs': len(data_clean)
                }
                
                trend_symbol = "📈" if sen_slope > 0 else "📉" if sen_slope < 0 else "➡️"
                significance = "***" if seasonal_results[season][fraction]['p_value'] < 0.001 else "**" if seasonal_results[season][fraction]['p_value'] < 0.01 else "*" if seasonal_results[season][fraction]['p_value'] < 0.05 else ""
                
                print(f"  {trend_symbol} {self.class_labels[fraction]}: {seasonal_results[season][fraction]['trend']} {significance} (p={seasonal_results[season][fraction]['p_value']:.4f})")
        
        return seasonal_results
    
    def export_results(self, output_path='saskatchewan_trend_results.xlsx'):
        """
        Exporte les résultats vers un fichier Excel
        """
        print(f"\n💾 Export des résultats vers {output_path}...")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Résumé des tendances
            for variable in self.results:
                summary_df = self.create_summary_table(variable)
                if summary_df is not None:
                    summary_df.to_excel(writer, sheet_name=f'Tendances_{variable}', index=False)
            
            # Données brutes
            if self.data is not None:
                self.data.to_excel(writer, sheet_name='Données_brutes', index=False)
        
        print(f"✓ Résultats exportés: {output_path}")

def main():
    """
    Fonction principale d'analyse
    """
    print("🏔️  ANALYSE DES TENDANCES D'ALBÉDO - GLACIER SASKATCHEWAN")
    print("=" * 60)
    
    # Chemin vers le fichier CSV (à ajuster selon votre configuration)
    csv_file = "daily_albedo_mann_kendall_ready_2010_2024.csv"
    
    # Vérifier si le fichier existe
    if not os.path.exists(csv_file):
        print(f"❌ Fichier non trouvé: {csv_file}")
        print("Veuillez:")
        print("1. Exporter le CSV depuis Google Earth Engine")
        print("2. Placer le fichier dans le même dossier que ce script")
        print("3. Vérifier le nom du fichier")
        return
    
    try:
        # Initialiser l'analyseur
        analyzer = SaskatchewanAlbedoAnalyzer(csv_file)
        
        # Charger les données
        analyzer.load_data()
        
        # Analyser les tendances pour mean et median
        print("\n" + "="*60)
        analyzer.calculate_trends('mean')
        
        # Créer les graphiques
        analyzer.plot_trends('mean', 'saskatchewan_albedo_trends_mean.png')
        
        # Tableau de résumé
        summary_table = analyzer.create_summary_table('mean')
        
        # Analyse saisonnière
        seasonal_results = analyzer.seasonal_analysis('mean')
        
        # Analyser aussi median si disponible
        if 'border_median' in analyzer.data.columns:
            print("\n" + "="*60)
            analyzer.calculate_trends('median')
            analyzer.plot_trends('median', 'saskatchewan_albedo_trends_median.png')
        
        # Exporter les résultats
        analyzer.export_results('saskatchewan_albedo_trend_analysis.xlsx')
        
        print("\n" + "="*60)
        print("✅ ANALYSE TERMINÉE!")
        print("📊 Graphiques créés: saskatchewan_albedo_trends_*.png")
        print("📋 Résultats Excel: saskatchewan_albedo_trend_analysis.xlsx")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()