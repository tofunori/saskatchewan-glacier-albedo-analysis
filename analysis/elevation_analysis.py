#!/usr/bin/env python3
"""
ANALYSE FRACTION × ÉLÉVATION - Méthodologie Williamson & Menounos (2021)
========================================================================

Module d'analyse des données d'albédo selon les fractions de couverture
glacier et les zones d'élévation, suivant la méthodologie de
Williamson & Menounos (2021) adaptée au glacier Saskatchewan.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from scipy import stats
from sklearn.linear_model import TheilSenRegressor

# Import optionnel de pymannkendall avec fallback
try:
    import pymannkendall as mk
    HAS_PYMANNKENDALL = True
except ImportError:
    HAS_PYMANNKENDALL = False
    warnings.warn("pymannkendall non disponible. Utilisation de scipy.stats pour les tendances.")

def manual_mann_kendall(data):
    """Implémentation simplifiée de Mann-Kendall si pymannkendall n'est pas disponible"""
    n = len(data)
    if n < 3:
        return {'trend': 'no trend', 'p': 1.0, 'Tau': 0.0}
    
    # Calculer S (somme des signes)
    S = 0
    for i in range(n-1):
        for j in range(i+1, n):
            S += np.sign(data[j] - data[i])
    
    # Calculer la variance
    var_S = n * (n - 1) * (2 * n + 5) / 18
    
    # Calculer Z
    if S > 0:
        Z = (S - 1) / np.sqrt(var_S)
    elif S < 0:
        Z = (S + 1) / np.sqrt(var_S)
    else:
        Z = 0
    
    # P-value approximative
    p_value = 2 * (1 - stats.norm.cdf(abs(Z)))
    
    # Tau de Kendall
    tau = S / (0.5 * n * (n - 1))
    
    # Déterminer la tendance
    if p_value < 0.05:
        trend = 'decreasing' if S < 0 else 'increasing'
    else:
        trend = 'no trend'
    
    return {'trend': trend, 'p': p_value, 'Tau': tau}

def manual_sens_slope(data):
    """Calcul simplifié de la pente de Sen"""
    n = len(data)
    if n < 2:
        return 0.0
    
    slopes = []
    for i in range(n-1):
        for j in range(i+1, n):
            slope = (data[j] - data[i]) / (j - i)
            slopes.append(slope)
    
    return np.median(slopes) if slopes else 0.0

class ElevationAnalyzer:
    """
    Analyseur pour les données d'albédo par fraction × élévation
    """
    
    def __init__(self, csv_path, output_dir="results/elevation_analysis"):
        """
        Initialise l'analyseur
        
        Args:
            csv_path: Chemin vers le CSV des données fraction × élévation
            output_dir: Répertoire de sortie pour les résultats
        """
        self.csv_path = Path(csv_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration des zones et fractions
        self.elevation_zones = ['above_median', 'at_median', 'below_median']
        self.fraction_classes = ['mostly_ice', 'pure_ice']
        self.combinations = []
        
        # Générer toutes les combinaisons
        for fraction in self.fraction_classes:
            for zone in self.elevation_zones:
                self.combinations.append(f"{fraction}_{zone}")
        
        self.data = None
        self.annual_data = None
        self.trends = {}
        
        print(f"📊 ElevationAnalyzer initialisé")
        print(f"📁 CSV: {self.csv_path}")
        print(f"📁 Sortie: {self.output_dir}")
        print(f"🔢 Combinaisons: {len(self.combinations)}")
    
    def load_data(self):
        """Charge et valide les données"""
        print(f"\n📂 Chargement des données: {self.csv_path}")
        
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {self.csv_path}")
        
        self.data = pd.read_csv(self.csv_path)
        print(f"✅ {len(self.data)} observations chargées")
        
        # Convertir la date
        self.data['date'] = pd.to_datetime(self.data['date'])
        self.data['year'] = self.data['date'].dt.year
        self.data['month'] = self.data['date'].dt.month
        self.data['doy'] = self.data['date'].dt.dayofyear
        
        # Valider les colonnes essentielles
        self._validate_columns()
        
        # Créer données annuelles
        self._create_annual_data()
        
        print(f"📅 Période: {self.data['date'].min()} à {self.data['date'].max()}")
        print(f"🗓️ Années: {self.data['year'].min()}-{self.data['year'].max()}")
        
    def _validate_columns(self):
        """Valide la présence des colonnes nécessaires"""
        required_base_cols = [
            'date', 'year', 'glacier_median_elevation', 
            'above_median_threshold', 'below_median_threshold'
        ]
        
        missing_cols = [col for col in required_base_cols if col not in self.data.columns]
        if missing_cols:
            raise ValueError(f"Colonnes manquantes: {missing_cols}")
        
        # Vérifier les colonnes de données pour chaque combinaison
        missing_combinations = []
        for combination in self.combinations:
            mean_col = f"{combination}_mean"
            count_col = f"{combination}_count"
            if mean_col not in self.data.columns or count_col not in self.data.columns:
                missing_combinations.append(combination)
        
        if missing_combinations:
            print(f"⚠️ Combinaisons avec données manquantes: {missing_combinations}")
        
        self.valid_combinations = [c for c in self.combinations if c not in missing_combinations]
        print(f"✅ Combinaisons valides: {len(self.valid_combinations)}")
    
    def _create_annual_data(self):
        """Crée les moyennes annuelles pour l'analyse de tendance"""
        annual_means = []
        
        for year in sorted(self.data['year'].unique()):
            year_data = self.data[self.data['year'] == year]
            annual_row = {'year': year}
            
            for combination in self.valid_combinations:
                mean_col = f"{combination}_mean"
                count_col = f"{combination}_count"
                
                # Filtrer les données valides (avec pixels suffisants)
                valid_data = year_data[
                    (year_data[count_col] >= 3) & 
                    (year_data[mean_col].notna())
                ]
                
                if len(valid_data) > 0:
                    annual_row[f"{combination}_mean"] = valid_data[mean_col].mean()
                    annual_row[f"{combination}_count"] = len(valid_data)
                    annual_row[f"{combination}_total_pixels"] = valid_data[count_col].sum()
                else:
                    annual_row[f"{combination}_mean"] = np.nan
                    annual_row[f"{combination}_count"] = 0
                    annual_row[f"{combination}_total_pixels"] = 0
            
            annual_means.append(annual_row)
        
        self.annual_data = pd.DataFrame(annual_means)
        print(f"📊 Données annuelles créées: {len(self.annual_data)} années")
    
    def calculate_trends(self):
        """Calcule les tendances pour chaque combinaison"""
        print(f"\n📈 Calcul des tendances Mann-Kendall...")
        
        self.trends = {}
        
        for combination in self.valid_combinations:
            mean_col = f"{combination}_mean"
            
            if mean_col not in self.annual_data.columns:
                continue
            
            # Données valides pour cette combinaison
            valid_data = self.annual_data[self.annual_data[mean_col].notna()]
            
            if len(valid_data) < 3:  # Minimum 3 années pour une tendance
                print(f"⚠️ {combination}: Données insuffisantes ({len(valid_data)} années)")
                continue
            
            years = valid_data['year'].values
            albedo = valid_data[mean_col].values
            
            try:
                # Test Mann-Kendall (avec ou sans pymannkendall)
                if HAS_PYMANNKENDALL:
                    mk_result = mk.original_test(albedo)
                    # pymannkendall n'a pas sens_estimator, utiliser la méthode manuelle
                    sen_slope = manual_sens_slope(albedo)
                else:
                    mk_result = manual_mann_kendall(albedo)
                    sen_slope = manual_sens_slope(albedo)
                    # Créer un objet compatible avec les attributs attendus
                    class MKResult:
                        def __init__(self, result_dict):
                            self.trend = result_dict['trend']
                            self.p = result_dict['p']
                            self.Tau = result_dict['Tau']
                    mk_result = MKResult(mk_result)
                
                # Régression linéaire pour comparaison
                lr_slope, lr_intercept, lr_r, lr_p, lr_se = stats.linregress(years, albedo)
                
                # Theil-Sen estimator (plus robuste)
                ts_reg = TheilSenRegressor(random_state=42)
                ts_reg.fit(years.reshape(-1, 1), albedo)
                ts_slope = ts_reg.coef_[0]
                
                # Statistiques descriptives
                albedo_stats = {
                    'mean': np.mean(albedo),
                    'std': np.std(albedo),
                    'min': np.min(albedo),
                    'max': np.max(albedo),
                    'range': np.max(albedo) - np.min(albedo)
                }
                
                # Changement total sur la période
                total_change = albedo[-1] - albedo[0]
                relative_change = (total_change / albedo[0]) * 100
                
                # Déterminer zone et fraction
                parts = combination.split('_')
                fraction = parts[0] + '_' + parts[1]  # mostly_ice ou pure_ice
                zone = '_'.join(parts[2:])  # above_median, at_median, below_median
                
                self.trends[combination] = {
                    'fraction_class': fraction,
                    'elevation_zone': zone,
                    'years_analyzed': len(valid_data),
                    'period': f"{years[0]}-{years[-1]}",
                    
                    # Mann-Kendall
                    'mk_trend': mk_result.trend,
                    'mk_p_value': mk_result.p,
                    'mk_tau': mk_result.Tau,
                    'mk_significant': mk_result.p < 0.05,
                    
                    # Sen's slope
                    'sens_slope': sen_slope,
                    'sens_slope_per_decade': sen_slope * 10,
                    
                    # Régression linéaire
                    'linear_slope': lr_slope,
                    'linear_r': lr_r,
                    'linear_p': lr_p,
                    
                    # Theil-Sen
                    'theilsen_slope': ts_slope,
                    
                    # Statistiques descriptives
                    **albedo_stats,
                    
                    # Changements
                    'total_change': total_change,
                    'relative_change_percent': relative_change,
                    
                    # Classification de tendance
                    'trend_direction': 'decreasing' if sen_slope < 0 else 'increasing' if sen_slope > 0 else 'stable',
                    'trend_magnitude': 'strong' if abs(sen_slope) > 0.01 else 'moderate' if abs(sen_slope) > 0.005 else 'weak'
                }
                
                print(f"✅ {combination}: {mk_result.trend} (p={mk_result.p:.3f}, slope={sen_slope:.4f})")
                
            except Exception as e:
                print(f"❌ Erreur pour {combination}: {e}")
                continue
        
        print(f"📊 Tendances calculées pour {len(self.trends)} combinaisons")
    
    def analyze_elevation_dependency(self):
        """Analyse la dépendance à l'élévation selon Williamson & Menounos"""
        print(f"\n🏔️ Analyse dépendance élévation (Williamson & Menounos 2021)...")
        
        # Extraire les informations d'élévation
        elevation_info = {
            'glacier_median': self.data['glacier_median_elevation'].iloc[0],
            'above_threshold': self.data['above_median_threshold'].iloc[0],
            'below_threshold': self.data['below_median_threshold'].iloc[0]
        }
        
        print(f"📊 Élévation médiane glacier: {elevation_info['glacier_median']:.1f}m")
        print(f"📊 Seuil zone haute: >{elevation_info['above_threshold']:.1f}m")
        print(f"📊 Seuil zone basse: <{elevation_info['below_threshold']:.1f}m")
        
        # Analyser les tendances par zone d'élévation
        elevation_analysis = {}
        
        for zone in self.elevation_zones:
            zone_trends = {combo: trend for combo, trend in self.trends.items() 
                          if trend['elevation_zone'] == zone}
            
            if not zone_trends:
                continue
            
            # Moyennes des pentes par zone
            sens_slopes = [trend['sens_slope'] for trend in zone_trends.values()]
            linear_slopes = [trend['linear_slope'] for trend in zone_trends.values()]
            
            # Significativité
            significant_trends = [trend for trend in zone_trends.values() if trend['mk_significant']]
            
            elevation_analysis[zone] = {
                'combinations_count': len(zone_trends),
                'mean_sens_slope': np.mean(sens_slopes),
                'mean_linear_slope': np.mean(linear_slopes),
                'significant_trends': len(significant_trends),
                'percent_significant': (len(significant_trends) / len(zone_trends)) * 100,
                'dominant_trend': 'decreasing' if np.mean(sens_slopes) < 0 else 'increasing',
                'trends': zone_trends
            }
        
        # Test de l'hypothèse de ligne de neige transitoire
        # Selon Williamson & Menounos: les tendances les plus fortes devraient être à ±100m de la médiane
        zone_slopes = {zone: analysis['mean_sens_slope'] for zone, analysis in elevation_analysis.items()}
        
        # Identifier la zone avec la tendance la plus forte (valeur absolue)
        if zone_slopes:
            strongest_decline_zone = min(zone_slopes.keys(), key=lambda z: zone_slopes[z])
        else:
            strongest_decline_zone = 'no_data'
            zone_slopes = {'no_data': 0.0}
        
        transient_snowline_hypothesis = {
            'strongest_decline_zone': strongest_decline_zone,
            'at_median_strongest': strongest_decline_zone == 'at_median',
            'zone_slopes': zone_slopes,
            'hypothesis_supported': strongest_decline_zone == 'at_median'
        }
        
        self.elevation_analysis = {
            'elevation_info': elevation_info,
            'zone_analysis': elevation_analysis,
            'transient_snowline': transient_snowline_hypothesis
        }
        
        # Afficher résultats
        print(f"\n📈 RÉSULTATS PAR ZONE D'ÉLÉVATION:")
        for zone, analysis in elevation_analysis.items():
            print(f"• {zone}: {analysis['mean_sens_slope']:.4f}/an ({analysis['percent_significant']:.1f}% significatif)")
        
        print(f"\n🎯 HYPOTHÈSE LIGNE DE NEIGE TRANSITOIRE:")
        print(f"• Zone de déclin le plus fort: {strongest_decline_zone}")
        print(f"• Hypothèse supportée: {transient_snowline_hypothesis['hypothesis_supported']}")
        
        return self.elevation_analysis
    
    def create_summary_report(self):
        """Crée un rapport de synthèse"""
        print(f"\n📋 Création du rapport de synthèse...")
        
        # Vérifier si des tendances ont été calculées
        if not self.trends:
            print("⚠️ Aucune tendance calculée - impossible de créer le rapport")
            return None
        
        # Créer DataFrame des tendances
        trends_df = pd.DataFrame([
            {
                'combination': combo,
                'fraction_class': trend['fraction_class'],
                'elevation_zone': trend['elevation_zone'],
                'years_analyzed': trend['years_analyzed'],
                'sens_slope_per_year': trend['sens_slope'],
                'sens_slope_per_decade': trend['sens_slope_per_decade'],
                'mk_trend': trend['mk_trend'],
                'mk_p_value': trend['mk_p_value'],
                'mk_significant': trend['mk_significant'],
                'mean_albedo': trend['mean'],
                'total_change_2010_2024': trend['total_change'],
                'relative_change_percent': trend['relative_change_percent'],
                'trend_direction': trend['trend_direction'],
                'trend_magnitude': trend['trend_magnitude']
            }
            for combo, trend in self.trends.items()
        ])
        
        # Sauvegarder le rapport détaillé
        trends_path = self.output_dir / "elevation_trends_detailed.csv"
        trends_df.to_csv(trends_path, index=False)
        print(f"✅ Rapport détaillé: {trends_path}")
        
        # Créer résumé par zone
        zone_summary = []
        for zone in self.elevation_zones:
            zone_data = trends_df[trends_df['elevation_zone'] == zone]
            if len(zone_data) > 0:
                zone_summary.append({
                    'elevation_zone': zone,
                    'combinations_count': len(zone_data),
                    'mean_slope': zone_data['sens_slope_per_year'].mean(),
                    'significant_trends': zone_data['mk_significant'].sum(),
                    'percent_significant': (zone_data['mk_significant'].sum() / len(zone_data)) * 100,
                    'mean_albedo': zone_data['mean_albedo'].mean(),
                    'mean_change_percent': zone_data['relative_change_percent'].mean()
                })
        
        zone_summary_df = pd.DataFrame(zone_summary)
        zone_path = self.output_dir / "elevation_zones_summary.csv"
        zone_summary_df.to_csv(zone_path, index=False)
        print(f"✅ Résumé par zone: {zone_path}")
        
        return trends_df, zone_summary_df
    
    def export_williamson_menounos_format(self):
        """Exporte les résultats au format Williamson & Menounos pour comparaison"""
        print(f"\n📤 Export format Williamson & Menounos (2021)...")
        
        # Format comparable au tableau de l'article
        wm_format = []
        
        # Vérifier que self.elevation_analysis existe
        if not self.elevation_analysis or 'elevation_info' not in self.elevation_analysis:
            print("⚠️ Informations d'élévation manquantes pour l'export")
            return None
        
        for combo, trend in self.trends.items():
            # Calculer élévation moyenne approximative pour chaque zone
            glacier_median = self.elevation_analysis['elevation_info']['glacier_median']
            
            zone_elevations = {
                'above_median': glacier_median + 150,  # Approximation centre zone haute
                'at_median': glacier_median,           # Zone médiane
                'below_median': glacier_median - 150   # Approximation centre zone basse
            }
            
            elevation_zone = trend['elevation_zone']
            if elevation_zone not in zone_elevations:
                print(f"⚠️ Zone d'élévation inconnue: {elevation_zone}")
                continue
            
            wm_format.append({
                'Region': 'Saskatchewan_Glacier',
                'Elevation_Zone': elevation_zone,
                'Fraction_Class': trend['fraction_class'],
                'Approx_Elevation_m': zone_elevations[elevation_zone],
                'Sen_Slope_per_year': trend['sens_slope'],
                'Sen_Slope_per_decade': trend['sens_slope_per_decade'],
                'Mann_Kendall_Trend': trend['mk_trend'],
                'P_Value': trend['mk_p_value'],
                'Tau': trend['mk_tau'],
                'Significant_5pct': trend['mk_significant'],
                'Mean_Albedo_2010_2024': trend['mean'],
                'Total_Change': trend['total_change'],
                'Relative_Change_Percent': trend['relative_change_percent'],
                'Years_Analyzed': trend['years_analyzed'],
                'Period': trend['period']
            })
        
        wm_df = pd.DataFrame(wm_format)
        wm_path = self.output_dir / "saskatchewan_williamson_menounos_format.csv"
        wm_df.to_csv(wm_path, index=False)
        print(f"✅ Format Williamson & Menounos: {wm_path}")
        
        return wm_df

def run_elevation_analysis(csv_path=None, output_dir="results/elevation_analysis"):
    """
    Lance l'analyse complète des données fraction × élévation
    
    Args:
        csv_path: Chemin vers le CSV (None = utilise config par défaut)
        output_dir: Répertoire de sortie
    
    Returns:
        ElevationAnalyzer: Instance configurée avec tous les résultats
    """
    if csv_path is None:
        csv_path = "data/csv/MOD10A1_daily_elevation_2010_2024.csv"
    
    print(f"\n{'='*60}")
    print(f"🏔️ ANALYSE FRACTION × ÉLÉVATION - WILLIAMSON & MENOUNOS (2021)")
    print(f"{'='*60}")
    
    try:
        # Initialiser l'analyseur
        analyzer = ElevationAnalyzer(csv_path, output_dir)
        
        # Charger les données
        analyzer.load_data()
        
        # Calculer les tendances
        analyzer.calculate_trends()
        
        # Analyser la dépendance à l'élévation
        analyzer.analyze_elevation_dependency()
        
        # Créer les rapports
        trends_df, zone_summary_df = analyzer.create_summary_report()
        
        # Export format Williamson & Menounos
        try:
            wm_df = analyzer.export_williamson_menounos_format()
        except Exception as e:
            print(f"⚠️ Erreur lors de l'export Williamson & Menounos: {e}")
            wm_df = None
        
        print(f"\n✅ ANALYSE TERMINÉE")
        print(f"📁 Résultats dans: {analyzer.output_dir}")
        print(f"📊 {len(analyzer.trends)} combinaisons analysées")
        print(f"🎯 Hypothèse ligne de neige transitoire: {analyzer.elevation_analysis['transient_snowline']['hypothesis_supported']}")
        
        return analyzer
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        raise e

if __name__ == "__main__":
    # Test de l'analyseur
    analyzer = run_elevation_analysis()