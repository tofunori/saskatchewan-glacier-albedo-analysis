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
from sklearn.utils import resample
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
    
    def advanced_seasonal_analysis(self, variable='mean'):
        """
        Analyse saisonnière avancée mois par mois (avril-mai focus)
        """
        print(f"\n🗓️  Analyse saisonnière détaillée ({variable})...")
        
        # Ajouter les mois si pas déjà fait
        if 'month' not in self.data.columns:
            self.data['month'] = self.data['date'].dt.month
        
        monthly_results = {}
        months = [6, 7, 8, 9]  # Juin à Septembre
        month_names = {6: 'Juin', 7: 'Juillet', 8: 'Août', 9: 'Septembre'}
        
        for month in months:
            print(f"\n--- {month_names[month]} ---")
            monthly_data = self.data[self.data['month'] == month]
            
            if len(monthly_data) < 10:
                print(f"Pas assez de données pour {month_names[month]}")
                continue
            
            monthly_results[month_names[month]] = {}
            
            for fraction in self.fraction_classes:
                col_name = f"{fraction}_{variable}"
                
                if col_name not in monthly_data.columns:
                    continue
                
                data_clean = monthly_data.dropna(subset=[col_name])
                
                if len(data_clean) < 5:
                    continue
                
                values = data_clean[col_name].values
                time_data = data_clean['decimal_year'].values
                
                # Mann-Kendall standard
                if PYMANNKENDALL_AVAILABLE:
                    mk_result = mk.original_test(values)
                else:
                    mk_result = self._manual_mann_kendall(values)
                
                # Pente de Sen avec intervalle de confiance
                sen_slope, sen_intercept, sen_lo, sen_up = theilslopes(values, time_data, alpha=0.05)
                
                monthly_results[month_names[month]][fraction] = {
                    'trend': mk_result.trend if PYMANNKENDALL_AVAILABLE else mk_result['trend'],
                    'p_value': mk_result.p if PYMANNKENDALL_AVAILABLE else mk_result['p_value'],
                    'sen_slope': sen_slope,
                    'sen_slope_ci_low': sen_lo,
                    'sen_slope_ci_high': sen_up,
                    'n_obs': len(data_clean)
                }
                
                trend_symbol = "📈" if sen_slope > 0 else "📉" if sen_slope < 0 else "➡️"
                significance = "***" if monthly_results[month_names[month]][fraction]['p_value'] < 0.001 else "**" if monthly_results[month_names[month]][fraction]['p_value'] < 0.01 else "*" if monthly_results[month_names[month]][fraction]['p_value'] < 0.05 else ""
                
                print(f"  {trend_symbol} {self.class_labels[fraction]}: {sen_slope:.6f}/an [{sen_lo:.6f}, {sen_up:.6f}] {significance}")
        
        return monthly_results
    
    def modified_mann_kendall_analysis(self, variable='mean'):
        """
        Analyse Mann-Kendall modifiée avec contrôle d'autocorrélation
        """
        print(f"\n🔄 Analyse Mann-Kendall modifiée (contrôle autocorrélation) ({variable})...")
        
        modified_results = {}
        
        for fraction in self.fraction_classes:
            col_name = f"{fraction}_{variable}"
            
            if col_name not in self.data.columns:
                continue
            
            # Préparer les données
            df_clean = self.data.dropna(subset=[col_name]).sort_values('date')
            
            if len(df_clean) < 15:
                continue
            
            values = df_clean[col_name].values
            time_data = df_clean['decimal_year'].values
            
            # Test d'autocorrélation (Ljung-Box)
            from scipy.stats import jarque_bera
            
            # Calculer l'autocorrélation lag-1
            autocorr_lag1 = np.corrcoef(values[:-1], values[1:])[0, 1]
            
            # Mann-Kendall modifié si autocorrélation significative
            if PYMANNKENDALL_AVAILABLE and abs(autocorr_lag1) > 0.1:
                try:
                    # Mann-Kendall modifié avec pymannkendall
                    mk_modified = mk.hamed_rao_modification_test(values)
                    mk_standard = mk.original_test(values)
                    
                    # Pré-blanchiment (pre-whitening)
                    prewhitened_values = self._prewhiten_series(values)
                    mk_prewhitened = mk.original_test(prewhitened_values)
                    
                except:
                    mk_modified = mk_standard = mk_prewhitened = None
            else:
                mk_standard = mk.original_test(values) if PYMANNKENDALL_AVAILABLE else self._manual_mann_kendall(values)
                mk_modified = mk_prewhitened = None
            
            # Pente de Sen
            sen_slope, _, _, _ = theilslopes(values, time_data)
            
            modified_results[fraction] = {
                'autocorr_lag1': autocorr_lag1,
                'standard_trend': mk_standard.trend if PYMANNKENDALL_AVAILABLE else mk_standard['trend'],
                'standard_p': mk_standard.p if PYMANNKENDALL_AVAILABLE else mk_standard['p_value'],
                'modified_trend': mk_modified.trend if mk_modified else None,
                'modified_p': mk_modified.p if mk_modified else None,
                'prewhitened_trend': mk_prewhitened.trend if mk_prewhitened else None,
                'prewhitened_p': mk_prewhitened.p if mk_prewhitened else None,
                'sen_slope': sen_slope,
                'n_obs': len(df_clean)
            }
            
            # Affichage
            autocorr_status = "🔴 Forte" if abs(autocorr_lag1) > 0.3 else "🟡 Modérée" if abs(autocorr_lag1) > 0.1 else "🟢 Faible"
            
            print(f"\n  {self.class_labels[fraction]}:")
            print(f"    Autocorrélation lag-1: {autocorr_lag1:.3f} {autocorr_status}")
            print(f"    Standard MK: {modified_results[fraction]['standard_trend']} (p={modified_results[fraction]['standard_p']:.4f})")
            
            if mk_modified:
                print(f"    Modifié MK: {modified_results[fraction]['modified_trend']} (p={modified_results[fraction]['modified_p']:.4f})")
            
            if mk_prewhitened:
                print(f"    Pré-blanchi MK: {modified_results[fraction]['prewhitened_trend']} (p={modified_results[fraction]['prewhitened_p']:.4f})")
        
        return modified_results
    
    def _prewhiten_series(self, series):
        """
        Pré-blanchiment d'une série temporelle (remove AR(1) component)
        """
        # Estimation du coefficient AR(1)
        rho = np.corrcoef(series[:-1], series[1:])[0, 1]
        
        # Série pré-blanchie
        prewhitened = np.zeros(len(series))
        prewhitened[0] = series[0]
        
        for i in range(1, len(series)):
            prewhitened[i] = series[i] - rho * series[i-1]
        
        return prewhitened[1:]  # Enlever le premier élément
    
    def bootstrap_confidence_intervals(self, variable='mean', n_bootstrap=1000):
        """
        Calcul d'intervalles de confiance par bootstrap pour les pentes de Sen
        """
        print(f"\n🎲 Analyse bootstrap des intervalles de confiance ({variable}, {n_bootstrap} itérations)...")
        
        bootstrap_results = {}
        
        for fraction in self.fraction_classes:
            col_name = f"{fraction}_{variable}"
            
            if col_name not in self.data.columns:
                continue
            
            # Préparer les données
            df_clean = self.data.dropna(subset=[col_name])
            
            if len(df_clean) < 10:
                continue
            
            values = df_clean[col_name].values
            time_data = df_clean['decimal_year'].values
            
            # Bootstrap des pentes
            bootstrap_slopes = []
            
            for i in range(n_bootstrap):
                # Échantillonnage bootstrap
                indices = resample(range(len(values)), n_samples=len(values), random_state=i)
                boot_values = values[indices]
                boot_time = time_data[indices]
                
                # Trier par temps pour maintenir l'ordre temporel
                sort_indices = np.argsort(boot_time)
                boot_values = boot_values[sort_indices]
                boot_time = boot_time[sort_indices]
                
                # Calculer la pente de Sen
                try:
                    sen_slope, _, _, _ = theilslopes(boot_values, boot_time)
                    bootstrap_slopes.append(sen_slope)
                except:
                    continue
            
            if len(bootstrap_slopes) < 100:
                print(f"⚠️  Pas assez d'échantillons bootstrap valides pour {fraction}")
                continue
            
            # Statistiques bootstrap
            bootstrap_slopes = np.array(bootstrap_slopes)
            
            bootstrap_results[fraction] = {
                'original_slope': self.results[variable][fraction]['sen_slope'],
                'bootstrap_mean': np.mean(bootstrap_slopes),
                'bootstrap_std': np.std(bootstrap_slopes),
                'ci_2.5': np.percentile(bootstrap_slopes, 2.5),
                'ci_97.5': np.percentile(bootstrap_slopes, 97.5),
                'bootstrap_slopes': bootstrap_slopes
            }
            
            # Affichage
            original = bootstrap_results[fraction]['original_slope']
            ci_low = bootstrap_results[fraction]['ci_2.5']
            ci_high = bootstrap_results[fraction]['ci_97.5']
            
            print(f"  {self.class_labels[fraction]}:")
            print(f"    Pente originale: {original:.6f}/an")
            print(f"    IC 95%: [{ci_low:.6f}, {ci_high:.6f}]/an")
            print(f"    Écart-type bootstrap: {bootstrap_results[fraction]['bootstrap_std']:.6f}")
        
        return bootstrap_results
    
    def create_spatial_slope_analysis(self, variable='mean'):
        """
        Analyse spatiale des pentes par fraction (préparation pour cartographie)
        """
        print(f"\n🗺️  Préparation de l'analyse spatiale des pentes ({variable})...")
        
        if variable not in self.results:
            print("⚠️  Calculer les tendances d'abord!")
            return None
        
        # Créer un DataFrame pour la cartographie
        spatial_data = []
        
        for fraction in self.fraction_classes:
            if fraction in self.results[variable]:
                result = self.results[variable][fraction]
                
                # Coordonnées fictives pour démonstration (à remplacer par vraies coordonnées)
                # En réalité, ces données viendraient de GEE avec lat/lon
                fraction_mapping = {
                    'border': {'center_fraction': 0.125, 'color': 'red'},
                    'mixed_low': {'center_fraction': 0.375, 'color': 'orange'},
                    'mixed_high': {'center_fraction': 0.625, 'color': 'yellow'},
                    'mostly_ice': {'center_fraction': 0.825, 'color': 'lightblue'},
                    'pure_ice': {'center_fraction': 0.95, 'color': 'blue'}
                }
                
                spatial_data.append({
                    'fraction_class': fraction,
                    'fraction_label': self.class_labels[fraction],
                    'center_fraction': fraction_mapping[fraction]['center_fraction'],
                    'sen_slope': result['sen_slope'],
                    'sen_slope_per_decade': result['sen_slope_per_decade'],
                    'p_value': result['p_value'],
                    'trend': result['trend'],
                    'significance': "***" if result['p_value'] < 0.001 else "**" if result['p_value'] < 0.01 else "*" if result['p_value'] < 0.05 else "ns",
                    'color': fraction_mapping[fraction]['color']
                })
        
        spatial_df = pd.DataFrame(spatial_data)
        
        # Créer une visualisation des pentes spatiales
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Graphique 1: Pentes par fraction
        colors = [row['color'] for _, row in spatial_df.iterrows()]
        bars = ax1.bar(spatial_df['fraction_label'], spatial_df['sen_slope'], color=colors, alpha=0.7)
        
        # Ajouter les barres d'erreur si bootstrap disponible
        if hasattr(self, 'bootstrap_results') and variable in self.bootstrap_results:
            errors = []
            for fraction in self.fraction_classes:
                if fraction in self.bootstrap_results[variable]:
                    boot_std = self.bootstrap_results[variable][fraction]['bootstrap_std']
                    errors.append(boot_std)
                else:
                    errors.append(0)
            
            ax1.errorbar(spatial_df['fraction_label'], spatial_df['sen_slope'], 
                        yerr=errors, fmt='none', ecolor='black', capsize=5)
        
        ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax1.set_title('Pentes de Sen par fraction de couverture', fontweight='bold')
        ax1.set_ylabel('Pente de Sen (changement/an)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Ajouter les p-values sur les barres
        for i, (_, row) in enumerate(spatial_df.iterrows()):
            ax1.text(i, row['sen_slope'] + 0.0001, row['significance'], 
                    ha='center', va='bottom', fontweight='bold')
        
        # Graphique 2: Changement par décennie
        bars2 = ax2.bar(spatial_df['fraction_label'], spatial_df['sen_slope_per_decade'], 
                       color=colors, alpha=0.7)
        
        ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax2.set_title('Changement projeté par décennie', fontweight='bold')
        ax2.set_ylabel('Changement d\'albédo par décennie')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Sauvegarder le graphique
        output_filename = f'spatial_slope_analysis_{variable}.png'
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        print(f"\n✅ GRAPHIQUE SPATIAL CRÉÉ: {output_filename}")
        
        # Afficher le graphique
        plt.show()
        
        print("\n📋 Résumé spatial des pentes:")
        print(spatial_df[['fraction_label', 'sen_slope', 'sen_slope_per_decade', 'significance']].to_string(index=False))
        
        return spatial_df
    
    def export_text_report(self, output_path='saskatchewan_albedo_statistical_report.txt'):
        """
        Exporte un rapport texte complet de toutes les analyses statistiques
        """
        print(f"\n📝 Génération du rapport texte: {output_path}...")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # En-tête
            f.write("="*80 + "\n")
            f.write("RAPPORT STATISTIQUE COMPLET - ANALYSE D'ALBÉDO GLACIER SASKATCHEWAN\n")
            f.write("="*80 + "\n\n")
            f.write(f"Date de génération: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Période analysée: {self.data['date'].min().strftime('%Y-%m-%d')} à {self.data['date'].max().strftime('%Y-%m-%d')}\n")
            f.write(f"Nombre total d'observations: {len(self.data)}\n")
            f.write("\n" + "-"*80 + "\n\n")
            
            # 1. RÉSUMÉ DES TENDANCES PRINCIPALES
            f.write("1. RÉSUMÉ DES TENDANCES PRINCIPALES (TEST MANN-KENDALL)\n")
            f.write("="*60 + "\n\n")
            
            for variable in self.results:
                f.write(f"Variable analysée: {variable.upper()}\n")
                f.write("-"*40 + "\n")
                
                # Tableau des résultats
                f.write(f"{'Fraction':<25} {'Tendance':<12} {'p-value':<10} {'Tau':<8} {'Pente Sen (/an)':<15} {'Sign.':<5}\n")
                f.write("-"*80 + "\n")
                
                for fraction in self.fraction_classes:
                    if fraction in self.results[variable]:
                        r = self.results[variable][fraction]
                        sig = "***" if r['p_value'] < 0.001 else "**" if r['p_value'] < 0.01 else "*" if r['p_value'] < 0.05 else "ns"
                        f.write(f"{self.class_labels[fraction]:<25} {r['trend']:<12} {r['p_value']:<10.4f} {r['tau']:<8.3f} {r['sen_slope']:<15.6f} {sig:<5}\n")
                
                f.write("\n")
            
            # 2. ANALYSE SAISONNIÈRE DÉTAILLÉE
            if hasattr(self, 'monthly_results'):
                f.write("\n" + "-"*80 + "\n")
                f.write("2. ANALYSE SAISONNIÈRE DÉTAILLÉE (PAR MOIS)\n")
                f.write("="*60 + "\n\n")
                
                for month, fractions in self.monthly_results.items():
                    f.write(f"\n{month.upper()}\n")
                    f.write("-"*30 + "\n")
                    f.write(f"{'Fraction':<25} {'Pente Sen':<12} {'IC 95% Bas':<12} {'IC 95% Haut':<12} {'p-value':<10} {'Sign.':<5}\n")
                    f.write("-"*80 + "\n")
                    
                    for fraction, results in fractions.items():
                        sig = "***" if results['p_value'] < 0.001 else "**" if results['p_value'] < 0.01 else "*" if results['p_value'] < 0.05 else "ns"
                        f.write(f"{self.class_labels[fraction]:<25} {results['sen_slope']:<12.6f} {results['sen_slope_ci_low']:<12.6f} {results['sen_slope_ci_high']:<12.6f} {results['p_value']:<10.4f} {sig:<5}\n")
            
            # 3. CONTRÔLE D'AUTOCORRÉLATION
            if hasattr(self, 'modified_results'):
                f.write("\n" + "-"*80 + "\n")
                f.write("3. CONTRÔLE D'AUTOCORRÉLATION\n")
                f.write("="*60 + "\n\n")
                
                f.write(f"{'Fraction':<25} {'Autocorr Lag-1':<15} {'Status':<15} {'MK Standard':<15} {'MK Modifié':<15} {'MK Pré-blanchi':<15}\n")
                f.write("-"*100 + "\n")
                
                for fraction, results in self.modified_results.items():
                    if fraction in self.class_labels:
                        autocorr = results['autocorr_lag1']
                        status = "Forte" if abs(autocorr) > 0.3 else "Modérée" if abs(autocorr) > 0.1 else "Faible"
                        
                        mk_std = f"{results['standard_trend']} (p={results['standard_p']:.3f})" if results['standard_trend'] else "N/A"
                        mk_mod = f"{results['modified_trend']} (p={results['modified_p']:.3f})" if results['modified_trend'] else "N/A"
                        mk_pw = f"{results['prewhitened_trend']} (p={results['prewhitened_p']:.3f})" if results['prewhitened_trend'] else "N/A"
                        
                        f.write(f"{self.class_labels[fraction]:<25} {autocorr:<15.3f} {status:<15} {mk_std:<15} {mk_mod:<15} {mk_pw:<15}\n")
            
            # 4. INTERVALLES DE CONFIANCE BOOTSTRAP
            if hasattr(self, 'bootstrap_results'):
                f.write("\n" + "-"*80 + "\n")
                f.write("4. INTERVALLES DE CONFIANCE BOOTSTRAP (1000 itérations)\n")
                f.write("="*60 + "\n\n")
                
                for variable, results in self.bootstrap_results.items():
                    f.write(f"\nVariable: {variable.upper()}\n")
                    f.write("-"*40 + "\n")
                    f.write(f"{'Fraction':<25} {'Pente Originale':<15} {'IC 2.5%':<15} {'IC 97.5%':<15} {'Écart-type':<15}\n")
                    f.write("-"*80 + "\n")
                    
                    for fraction, boot_results in results.items():
                        if fraction in self.class_labels:
                            f.write(f"{self.class_labels[fraction]:<25} {boot_results['original_slope']:<15.6f} {boot_results['ci_2.5']:<15.6f} {boot_results['ci_97.5']:<15.6f} {boot_results['bootstrap_std']:<15.6f}\n")
            
            # 5. STATISTIQUES DESCRIPTIVES
            f.write("\n" + "-"*80 + "\n")
            f.write("5. STATISTIQUES DESCRIPTIVES PAR FRACTION\n")
            f.write("="*60 + "\n\n")
            
            for fraction in self.fraction_classes:
                f.write(f"\n{self.class_labels[fraction].upper()}\n")
                f.write("-"*30 + "\n")
                
                for var in ['mean', 'median']:
                    col_name = f"{fraction}_{var}"
                    if col_name in self.data.columns:
                        data = self.data[col_name].dropna()
                        if len(data) > 0:
                            f.write(f"\nAlbédo {var}:\n")
                            f.write(f"  Moyenne: {data.mean():.4f}\n")
                            f.write(f"  Médiane: {data.median():.4f}\n")
                            f.write(f"  Écart-type: {data.std():.4f}\n")
                            f.write(f"  Min: {data.min():.4f}\n")
                            f.write(f"  Max: {data.max():.4f}\n")
                            f.write(f"  Q1: {data.quantile(0.25):.4f}\n")
                            f.write(f"  Q3: {data.quantile(0.75):.4f}\n")
                            f.write(f"  IQR: {data.quantile(0.75) - data.quantile(0.25):.4f}\n")
            
            # 6. RÉSUMÉ SPATIAL DES PENTES
            f.write("\n" + "-"*80 + "\n")
            f.write("6. RÉSUMÉ SPATIAL DES PENTES\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"{'Fraction':<25} {'Pente Sen (/an)':<20} {'Changement /décennie':<20} {'Significativité':<15}\n")
            f.write("-"*80 + "\n")
            
            for fraction in self.fraction_classes:
                if fraction in self.results.get('mean', {}):
                    r = self.results['mean'][fraction]
                    sig = "***" if r['p_value'] < 0.001 else "**" if r['p_value'] < 0.01 else "*" if r['p_value'] < 0.05 else "ns"
                    f.write(f"{self.class_labels[fraction]:<25} {r['sen_slope']:<20.6f} {r['sen_slope_per_decade']:<20.5f} {sig:<15}\n")
            
            # 7. INTERPRÉTATION ET RECOMMANDATIONS
            f.write("\n" + "-"*80 + "\n")
            f.write("7. INTERPRÉTATION AUTOMATIQUE\n")
            f.write("="*60 + "\n\n")
            
            # Compter les tendances significatives
            sig_decreasing = 0
            sig_increasing = 0
            total_fractions = 0
            
            for variable in self.results:
                for fraction, r in self.results[variable].items():
                    if r['p_value'] < 0.05:
                        if r['sen_slope'] < 0:
                            sig_decreasing += 1
                        else:
                            sig_increasing += 1
                    total_fractions += 1
            
            f.write(f"Nombre total de tests effectués: {total_fractions}\n")
            f.write(f"Tendances décroissantes significatives: {sig_decreasing}\n")
            f.write(f"Tendances croissantes significatives: {sig_increasing}\n")
            f.write(f"Pas de tendance significative: {total_fractions - sig_decreasing - sig_increasing}\n\n")
            
            # Recommandations basées sur l'autocorrélation
            if hasattr(self, 'modified_results'):
                high_autocorr = sum(1 for r in self.modified_results.values() if abs(r['autocorr_lag1']) > 0.3)
                if high_autocorr > 0:
                    f.write(f"⚠️  ATTENTION: {high_autocorr} fraction(s) avec forte autocorrélation détectée.\n")
                    f.write("   Recommandation: Utiliser les résultats Mann-Kendall modifiés ou pré-blanchis.\n\n")
            
            # Signal le plus fort
            strongest_signal = None
            max_slope = 0
            for fraction, r in self.results.get('mean', {}).items():
                if r['p_value'] < 0.05 and abs(r['sen_slope']) > abs(max_slope):
                    max_slope = r['sen_slope']
                    strongest_signal = fraction
            
            if strongest_signal:
                f.write(f"📊 Signal le plus fort détecté: {self.class_labels[strongest_signal]}\n")
                f.write(f"   Pente: {max_slope:.6f}/an ({max_slope*10:.5f}/décennie)\n")
                f.write(f"   p-value: {self.results['mean'][strongest_signal]['p_value']:.4f}\n")
            
            # Pied de page
            f.write("\n" + "="*80 + "\n")
            f.write("FIN DU RAPPORT STATISTIQUE\n")
            f.write("="*80 + "\n")
        
        print(f"✓ Rapport texte généré: {output_path}")
        return output_path
    
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
            
            # Résultats avancés si disponibles
            if hasattr(self, 'monthly_results'):
                # Convertir les résultats mensuels en DataFrame
                monthly_data = []
                for month, fractions in self.monthly_results.items():
                    for fraction, results in fractions.items():
                        monthly_data.append({
                            'Mois': month,
                            'Fraction': self.class_labels.get(fraction, fraction),
                            'Tendance': results.get('trend', 'N/A'),
                            'Pente Sen': results.get('sen_slope', 0),
                            'IC Bas': results.get('sen_slope_ci_low', 0),
                            'IC Haut': results.get('sen_slope_ci_high', 0),
                            'p-value': results.get('p_value', 1),
                            'N obs': results.get('n_obs', 0)
                        })
                if monthly_data:
                    monthly_df = pd.DataFrame(monthly_data)
                    monthly_df.to_excel(writer, sheet_name='Analyse_Mensuelle', index=False)
            
            # Résultats bootstrap si disponibles
            if hasattr(self, 'bootstrap_results'):
                bootstrap_data = []
                for variable, results in self.bootstrap_results.items():
                    for fraction, boot_results in results.items():
                        bootstrap_data.append({
                            'Variable': variable,
                            'Fraction': self.class_labels.get(fraction, fraction),
                            'Pente Originale': boot_results['original_slope'],
                            'IC 2.5%': boot_results['ci_2.5'],
                            'IC 97.5%': boot_results['ci_97.5'],
                            'Écart-type Bootstrap': boot_results['bootstrap_std']
                        })
                if bootstrap_data:
                    bootstrap_df = pd.DataFrame(bootstrap_data)
                    bootstrap_df.to_excel(writer, sheet_name='Bootstrap_IC', index=False)
            
            # Données brutes (limitées pour éviter fichiers trop gros)
            if self.data is not None:
                # Limiter aux colonnes essentielles
                essential_cols = ['date', 'year', 'doy', 'decimal_year', 'season']
                for fraction in self.fraction_classes:
                    for var in ['mean', 'median']:
                        col = f'{fraction}_{var}'
                        if col in self.data.columns:
                            essential_cols.append(col)
                
                data_subset = self.data[essential_cols].head(1000)  # Limiter à 1000 lignes
                data_subset.to_excel(writer, sheet_name='Données_échantillon', index=False)
        
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
        
        # ANALYSES AVANCÉES
        print("\n" + "="*60)
        print("🔬 ANALYSES AVANCÉES")
        
        # 1. Analyse saisonnière détaillée
        monthly_results = analyzer.advanced_seasonal_analysis('mean')
        analyzer.monthly_results = monthly_results  # Stocker pour l'export
        
        # 2. Contrôle d'autocorrélation
        modified_results = analyzer.modified_mann_kendall_analysis('mean')
        analyzer.modified_results = modified_results  # Stocker pour l'export
        
        # 3. Intervalles de confiance bootstrap
        bootstrap_results = analyzer.bootstrap_confidence_intervals('mean', n_bootstrap=1000)
        analyzer.bootstrap_results = {'mean': bootstrap_results}
        
        # 4. Analyse spatiale des pentes
        spatial_results = analyzer.create_spatial_slope_analysis('mean')
        
        # Exporter les résultats Excel
        analyzer.export_results('saskatchewan_albedo_trend_analysis_advanced.xlsx')
        
        # Générer le rapport texte complet
        analyzer.export_text_report('saskatchewan_albedo_statistical_report.txt')
        
        print("\n" + "="*60)
        print("✅ ANALYSE TERMINÉE!")
        print("\n📊 FICHIERS GÉNÉRÉS:")
        print("  📈 Graphiques de tendances: saskatchewan_albedo_trends_mean.png")
        print("  📈 Graphiques de tendances: saskatchewan_albedo_trends_median.png")
        print("  🗺️  Cartographie spatiale: spatial_slope_analysis_mean.png")
        print("  📋 Résultats Excel standard: saskatchewan_albedo_trend_analysis.xlsx")
        print("  📋 Résultats Excel avancés: saskatchewan_albedo_trend_analysis_advanced.xlsx")
        print("  📝 Rapport statistique complet: saskatchewan_albedo_statistical_report.txt")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()