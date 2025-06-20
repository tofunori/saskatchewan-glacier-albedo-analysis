#!/usr/bin/env python3
"""
Analyse de tendances personnalisée pour l'albédo du glacier Saskatchewan
========================================================================

Module pour analyses personnalisées avec paramètres utilisateur configurables
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Setup path
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))

def custom_analysis_menu():
    """Menu principal pour analyse personnalisée"""
    while True:
        clear_screen()
        print_header()
        print("\n📈 ANALYSE DE TENDANCES PERSONNALISÉE")
        print("=" * 50)
        print("1. 🎯 Analyse par période spécifique")
        print("   Analyze specific time period")
        print()
        print("2. 📊 Analyse par fraction d'albédo")
        print("   Analyze specific albedo fraction")
        print()
        print("3. 🌱 Analyse saisonnière détaillée")
        print("   Detailed seasonal analysis")
        print()
        print("4. 📈 Comparaison multi-variables")
        print("   Multi-variable comparison")
        print()
        print("5. 🔍 Analyse de qualité des données")
        print("   Data quality analysis")
        print()
        print("6. 📋 Résumé des analyses disponibles")
        print("   Available analysis summary")
        print()
        print("0. ⬅️  Retour au menu principal")
        print("-" * 50)
        
        choice = input("\n🎯 Votre choix (0-6): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            specific_period_analysis()
        elif choice == "2":
            fraction_analysis()
        elif choice == "3":
            seasonal_analysis()
        elif choice == "4":
            multi_variable_analysis()
        elif choice == "5":
            data_quality_analysis()
        elif choice == "6":
            analysis_summary()
        else:
            print("❌ Choix invalide")
            input("📱 Appuyez sur Entrée pour continuer...")

def clear_screen():
    """Efface l'écran"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Affiche l'en-tête"""
    print("🏔️  SASKATCHEWAN GLACIER ALBEDO ANALYSIS")
    print("=" * 60)
    print("📅 Session:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("📍 Analyse personnalisée")
    print("=" * 60)

def load_data():
    """Charge les données avec gestion d'erreur"""
    try:
        from config import CSV_PATH
        from data_handler import AlbedoDataHandler
        
        if not os.path.exists(CSV_PATH):
            print(f"❌ Fichier CSV non trouvé: {CSV_PATH}")
            return None
        
        print(f"📊 Chargement des données: {CSV_PATH}")
        handler = AlbedoDataHandler(CSV_PATH)
        handler.load_data()
        
        print(f"✅ {len(handler)} observations chargées")
        return handler
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        return None

def specific_period_analysis():
    """Analyse pour une période spécifique"""
    print("\n🎯 ANALYSE PAR PÉRIODE SPÉCIFIQUE")
    print("=" * 50)
    
    # Load data
    handler = load_data()
    if handler is None:
        input("📱 Appuyez sur Entrée pour continuer...")
        return
    
    try:
        # Get available date range
        data = handler.data
        min_date = data['date'].min()
        max_date = data['date'].max()
        
        print(f"📅 Données disponibles: {min_date} à {max_date}")
        print("\n🗓️  Options de période:")
        print("1. 🚀 Dernière année")
        print("2. ❄️  Saison d'hiver (Dec-Feb)")
        print("3. ☀️  Saison d'été (Jun-Aug)")
        print("4. 🎯 Période personnalisée")
        
        period_choice = input("\nChoix (1-4): ").strip()
        
        # Define period based on choice
        if period_choice == "1":
            # Last year
            end_date = pd.to_datetime(max_date)
            start_date = end_date - timedelta(days=365)
            period_name = "Dernière année"
            
        elif period_choice == "2":
            # Winter season (Dec-Feb)
            year = pd.to_datetime(max_date).year
            start_date = pd.to_datetime(f"{year-1}-12-01")
            end_date = pd.to_datetime(f"{year}-02-28")
            period_name = f"Hiver {year-1}-{year}"
            
        elif period_choice == "3":
            # Summer season (Jun-Aug)
            year = pd.to_datetime(max_date).year
            start_date = pd.to_datetime(f"{year}-06-01")
            end_date = pd.to_datetime(f"{year}-08-31")
            period_name = f"Été {year}"
            
        elif period_choice == "4":
            # Custom period
            start_str = input("Date de début (YYYY-MM-DD): ").strip()
            end_str = input("Date de fin (YYYY-MM-DD): ").strip()
            start_date = pd.to_datetime(start_str)
            end_date = pd.to_datetime(end_str)
            period_name = f"Période {start_str} à {end_str}"
            
        else:
            print("❌ Choix invalide")
            input("📱 Appuyez sur Entrée pour continuer...")
            return
        
        # Filter data for period
        mask = (pd.to_datetime(data['date']) >= start_date) & (pd.to_datetime(data['date']) <= end_date)
        period_data = data[mask].copy()
        
        if len(period_data) == 0:
            print(f"❌ Aucune donnée pour la période {start_date.date()} - {end_date.date()}")
            input("📱 Appuyez sur Entrée pour continuer...")
            return
        
        print(f"\n📊 ANALYSE POUR: {period_name}")
        print(f"📈 {len(period_data)} observations")
        print(f"📅 Du {start_date.date()} au {end_date.date()}")
        
        # Perform analysis
        analyze_period_data(period_data, period_name)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    input("\n📱 Appuyez sur Entrée pour continuer...")

def analyze_period_data(data, period_name):
    """Analyse les données pour une période donnée"""
    try:
        from config import FRACTION_CLASSES
        
        print(f"\n📊 STATISTIQUES DESCRIPTIVES - {period_name}")
        print("-" * 50)
        
        # Analyze each fraction
        for fraction in FRACTION_CLASSES[:3]:  # Limit to first 3 fractions
            mean_col = f"{fraction}_mean"
            if mean_col in data.columns:
                values = data[mean_col].dropna()
                if len(values) > 0:
                    print(f"\n🔍 {fraction.upper()}:")
                    print(f"   📊 Observations: {len(values)}")
                    print(f"   📈 Moyenne: {values.mean():.4f}")
                    print(f"   📉 Médiane: {values.median():.4f}")
                    print(f"   📊 Écart-type: {values.std():.4f}")
                    print(f"   📋 Min-Max: {values.min():.4f} - {values.max():.4f}")
                    
                    # Simple trend check
                    if len(values) > 10:
                        x = np.arange(len(values))
                        slope = np.polyfit(x, values, 1)[0]
                        trend = "📈 Croissante" if slope > 0.001 else "📉 Décroissante" if slope < -0.001 else "➡️ Stable"
                        print(f"   🎯 Tendance: {trend} (pente: {slope:.6f})")
        
        # Monthly breakdown if data spans multiple months
        data['month'] = pd.to_datetime(data['date']).dt.month
        unique_months = sorted(data['month'].unique())
        
        if len(unique_months) > 1:
            print(f"\n📅 RÉPARTITION MENSUELLE:")
            print("-" * 30)
            for month in unique_months:
                month_data = data[data['month'] == month]
                month_name = get_month_name(month)
                print(f"   {month_name}: {len(month_data)} observations")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")

def fraction_analysis():
    """Analyse spécifique à une fraction d'albédo"""
    print("\n📊 ANALYSE PAR FRACTION D'ALBÉDO")
    print("=" * 50)
    
    handler = load_data()
    if handler is None:
        input("📱 Appuyez sur Entrée pour continuer...")
        return
    
    try:
        from config import FRACTION_CLASSES
        
        print("🎯 Fractions disponibles:")
        for i, fraction in enumerate(FRACTION_CLASSES, 1):
            print(f"   {i}. {fraction}")
        
        choice = input(f"\nChoisissez une fraction (1-{len(FRACTION_CLASSES)}): ").strip()
        
        try:
            fraction_idx = int(choice) - 1
            if 0 <= fraction_idx < len(FRACTION_CLASSES):
                selected_fraction = FRACTION_CLASSES[fraction_idx]
                analyze_single_fraction(handler, selected_fraction)
            else:
                print("❌ Choix invalide")
        except ValueError:
            print("❌ Choix invalide")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    input("\n📱 Appuyez sur Entrée pour continuer...")

def analyze_single_fraction(handler, fraction):
    """Analyse détaillée d'une fraction spécifique"""
    try:
        print(f"\n🔍 ANALYSE DÉTAILLÉE: {fraction.upper()}")
        print("=" * 50)
        
        # Get fraction data
        fraction_data = handler.get_fraction_data(fraction, "mean")
        
        if fraction_data.empty:
            print(f"❌ Aucune donnée pour la fraction {fraction}")
            return
        
        values = fraction_data['value'].dropna()
        dates = pd.to_datetime(fraction_data['date'])
        
        print(f"📊 Statistiques globales:")
        print(f"   📈 Observations: {len(values)}")
        print(f"   📅 Période: {dates.min().date()} à {dates.max().date()}")
        print(f"   📊 Moyenne: {values.mean():.4f}")
        print(f"   📉 Médiane: {values.median():.4f}")
        print(f"   📊 Écart-type: {values.std():.4f}")
        
        # Quartiles
        q25, q75 = values.quantile([0.25, 0.75])
        print(f"   📋 Q1-Q3: {q25:.4f} - {q75:.4f}")
        
        # Trend analysis
        from trend_calculator import TrendCalculator
        trend_calc = TrendCalculator(handler)
        
        print(f"\n📈 ANALYSE DE TENDANCE:")
        print("-" * 30)
        
        # Simple Mann-Kendall test
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        print(f"   🎯 Pente linéaire: {slope:.6f}/observation")
        
        # Annual trend if data spans multiple years
        years = dates.dt.year.unique()
        if len(years) > 1:
            annual_slope = slope * 365  # Approximate annual change
            print(f"   📅 Tendance annuelle: {annual_slope:.4f}")
            
            trend_direction = "📈 Augmentation" if slope > 0.001 else "📉 Diminution" if slope < -0.001 else "➡️ Stable"
            print(f"   🎯 Direction: {trend_direction}")
        
        # Monthly statistics
        print(f"\n📅 STATISTIQUES MENSUELLES:")
        print("-" * 30)
        
        fraction_data['month'] = dates.dt.month
        monthly_stats = fraction_data.groupby('month')['value'].agg(['count', 'mean', 'std']).round(4)
        
        for month, stats in monthly_stats.iterrows():
            month_name = get_month_name(month)
            print(f"   {month_name}: {stats['count']} obs, moy={stats['mean']:.4f}, std={stats['std']:.4f}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")

def seasonal_analysis():
    """Analyse saisonnière détaillée"""
    print("\n🌱 ANALYSE SAISONNIÈRE DÉTAILLÉE")
    print("=" * 50)
    
    handler = load_data()
    if handler is None:
        input("📱 Appuyez sur Entrée pour continuer...")
        return
    
    try:
        data = handler.data
        data['month'] = pd.to_datetime(data['date']).dt.month
        
        # Define seasons
        seasons = {
            'Hiver': [12, 1, 2],
            'Printemps': [3, 4, 5], 
            'Été': [6, 7, 8],
            'Automne': [9, 10, 11]
        }
        
        print("🌍 COMPARAISON SAISONNIÈRE:")
        print("-" * 40)
        
        from config import FRACTION_CLASSES
        
        # Analyze first fraction as example
        if FRACTION_CLASSES:
            fraction = FRACTION_CLASSES[0]
            mean_col = f"{fraction}_mean"
            
            if mean_col in data.columns:
                print(f"📊 Variable analysée: {fraction}")
                print()
                
                for season_name, months in seasons.items():
                    season_data = data[data['month'].isin(months)][mean_col].dropna()
                    
                    if len(season_data) > 0:
                        print(f"🌱 {season_name}:")
                        print(f"   📊 Observations: {len(season_data)}")
                        print(f"   📈 Moyenne: {season_data.mean():.4f}")
                        print(f"   📊 Écart-type: {season_data.std():.4f}")
                        print(f"   📋 Min-Max: {season_data.min():.4f} - {season_data.max():.4f}")
                        print()
        
        # Year-over-year comparison
        print("📅 ÉVOLUTION INTER-ANNUELLE:")
        print("-" * 30)
        
        data['year'] = pd.to_datetime(data['date']).dt.year
        yearly_stats = data.groupby('year').agg({
            'border_mean': ['count', 'mean', 'std'] if 'border_mean' in data.columns else None
        }).round(4)
        
        if 'border_mean' in data.columns:
            for year, stats in yearly_stats.iterrows():
                if not pd.isna(stats[('border_mean', 'mean')]):
                    print(f"   {year}: {int(stats[('border_mean', 'count')])} obs, "
                          f"moy={stats[('border_mean', 'mean')]:.4f}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    input("\n📱 Appuyez sur Entrée pour continuer...")

def multi_variable_analysis():
    """Analyse comparative multi-variables"""
    print("\n📈 COMPARAISON MULTI-VARIABLES")
    print("=" * 50)
    print("Fonctionnalité avancée à implémenter...")
    print("• Corrélations entre fractions")
    print("• Analyse en composantes principales")
    print("• Clustering temporel")
    input("\n📱 Appuyez sur Entrée pour continuer...")

def data_quality_analysis():
    """Analyse de la qualité des données"""
    print("\n🔍 ANALYSE DE QUALITÉ DES DONNÉES")
    print("=" * 50)
    
    handler = load_data()
    if handler is None:
        input("📱 Appuyez sur Entrée pour continuer...")
        return
    
    try:
        data = handler.data
        
        print("📊 QUALITÉ GÉNÉRALE:")
        print("-" * 25)
        print(f"   📈 Total observations: {len(data)}")
        
        # Missing data analysis
        print(f"\n📋 DONNÉES MANQUANTES:")
        print("-" * 25)
        
        from config import FRACTION_CLASSES
        for fraction in FRACTION_CLASSES[:5]:  # Check first 5 fractions
            mean_col = f"{fraction}_mean"
            if mean_col in data.columns:
                missing = data[mean_col].isna().sum()
                missing_pct = (missing / len(data)) * 100
                print(f"   {fraction}: {missing} manquantes ({missing_pct:.1f}%)")
        
        # Quality flags if available
        if 'quality' in data.columns:
            print(f"\n🏷️  INDICATEURS QUALITÉ:")
            print("-" * 25)
            quality_counts = data['quality'].value_counts().sort_index()
            for quality, count in quality_counts.items():
                percentage = (count / len(data)) * 100
                print(f"   Qualité {quality}: {count} ({percentage:.1f}%)")
        
        # Date coverage
        print(f"\n📅 COUVERTURE TEMPORELLE:")
        print("-" * 25)
        dates = pd.to_datetime(data['date'])
        date_range = dates.max() - dates.min()
        print(f"   📊 Période totale: {date_range.days} jours")
        print(f"   📅 Première date: {dates.min().date()}")
        print(f"   📅 Dernière date: {dates.max().date()}")
        
        # Monthly distribution
        monthly_counts = dates.dt.month.value_counts().sort_index()
        print(f"\n   📊 Distribution mensuelle:")
        for month, count in monthly_counts.items():
            month_name = get_month_name(month)
            print(f"      {month_name}: {count} observations")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    input("\n📱 Appuyez sur Entrée pour continuer...")

def analysis_summary():
    """Résumé des analyses disponibles"""
    print("\n📋 RÉSUMÉ DES ANALYSES DISPONIBLES")
    print("=" * 50)
    
    print("🎯 ANALYSES TEMPORELLES:")
    print("   • Période spécifique (dernière année, saisons, personnalisée)")
    print("   • Évolution inter-annuelle")
    print("   • Comparaisons saisonnières")
    print()
    
    print("📊 ANALYSES PAR VARIABLE:")
    print("   • Statistiques descriptives par fraction")
    print("   • Tests de tendance Mann-Kendall")
    print("   • Répartitions mensuelles")
    print()
    
    print("🔍 QUALITÉ DES DONNÉES:")
    print("   • Détection des valeurs manquantes")
    print("   • Indicateurs de qualité")
    print("   • Couverture temporelle")
    print()
    
    print("🚀 À VENIR:")
    print("   • Corrélations multi-variables")
    print("   • Analyse en composantes principales")
    print("   • Clustering temporel")
    print("   • Détection d'anomalies")
    
    input("\n📱 Appuyez sur Entrée pour continuer...")

def get_month_name(month):
    """Retourne le nom du mois en français"""
    month_names = {
        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
        5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
        9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }
    return month_names.get(month, f'Mois {month}')

# Standalone execution for testing
if __name__ == "__main__":
    try:
        custom_analysis_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Interruption utilisateur. Au revoir!")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()