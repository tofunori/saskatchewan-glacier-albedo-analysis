#!/usr/bin/env python3
"""
Analysis Functions for Saskatchewan Glacier Albedo Analysis
===========================================================

Refactored analysis orchestration with improved error handling and modularity.
This module now imports from specialized modules for better separation of concerns.
"""

import logging
from typing import Optional

# Import refactored modules
from scripts.dataset_validator import check_config, check_datasets_availability
from scripts.analysis_orchestrator import (
    orchestrator,
    run_dataset_analysis,
    run_custom_analysis, 
    run_complete_analysis,
    run_trends_only,
    run_visualizations_only,
    run_pixels_only,
    run_daily_only
)

logger = logging.getLogger(__name__)

# ===========================================
# FONCTIONS D'ANALYSE PRINCIPALES
# ===========================================

def run_complete_analysis():
    """Lance l'analyse complète pour le dataset par défaut"""
    print("\n🚀 ANALYSE COMPLÈTE")
    print("="*50)
    
    try:
        from config import DEFAULT_DATASET
        run_dataset_analysis(DEFAULT_DATASET)
        print("✅ Analyse complète terminée avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse complète: {e}")

def run_trends_only():
    """Lance seulement l'analyse des tendances"""
    print("\n📈 ANALYSE DES TENDANCES")
    print("="*50)
    
    try:
        from config import DEFAULT_DATASET
        run_custom_analysis(DEFAULT_DATASET, 2)
        print("✅ Analyse des tendances terminée")
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse des tendances: {e}")

def run_visualizations_only():
    """Lance seulement les visualisations"""
    print("\n🎨 GÉNÉRATION DES VISUALISATIONS")
    print("="*50)
    
    try:
        from config import DEFAULT_DATASET
        run_custom_analysis(DEFAULT_DATASET, 3)
        print("✅ Visualisations générées")
    except Exception as e:
        print(f"❌ Erreur lors de la génération des visualisations: {e}")

def run_pixels_only():
    """Lance seulement l'analyse des pixels/QA"""
    print("\n🔍 ANALYSE PIXELS/QA")
    print("="*50)
    
    try:
        from config import DEFAULT_DATASET
        run_custom_analysis(DEFAULT_DATASET, 4)
        print("✅ Analyse pixels/QA terminée")
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse pixels/QA: {e}")

def run_daily_only():
    """Lance seulement les graphiques quotidiens"""
    print("\n📅 GRAPHIQUES QUOTIDIENS")
    print("="*50)
    
    try:
        from config import DEFAULT_DATASET
        run_custom_analysis(DEFAULT_DATASET, 5)
        print("✅ Graphiques quotidiens générés")
    except Exception as e:
        print(f"❌ Erreur lors de la génération des graphiques quotidiens: {e}")

# ===========================================
# FONCTIONS D'ANALYSE PAR DATASET
# ===========================================

def run_dataset_analysis(dataset_name):
    """Lance l'analyse complète pour un dataset spécifique"""
    print(f"\n🔍 ANALYSE COMPLÈTE - {dataset_name}")
    print("="*60)
    
    try:
        # Chargement des données
        print("📊 Chargement des données...")
        data = _load_dataset(dataset_name)
        
        # Analyse des tendances
        print("📈 Analyse des tendances...")
        _run_trend_analysis(data, dataset_name)
        
        # Visualisations
        print("🎨 Génération des visualisations...")
        _run_visualizations(data, dataset_name)
        
        # Analyse pixels/QA
        print("🔍 Analyse pixels/QA...")
        _run_pixel_analysis(data, dataset_name)
        
        # Graphiques quotidiens
        print("📅 Graphiques quotidiens...")
        _run_daily_plots(data, dataset_name)
        
        print(f"✅ Analyse complète de {dataset_name} terminée")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse de {dataset_name}: {e}")

def run_custom_analysis(dataset_name, analysis_type):
    """Lance un type d'analyse spécifique pour un dataset"""
    print(f"\n🔍 ANALYSE PERSONNALISÉE - {dataset_name}")
    print("="*60)
    
    try:
        # Chargement des données
        print("📊 Chargement des données...")
        data = _load_dataset(dataset_name)
        
        if analysis_type == 2:
            # Tendances seulement
            print("📈 Analyse des tendances...")
            _run_trend_analysis(data, dataset_name)
            
        elif analysis_type == 3:
            # Visualisations seulement
            print("🎨 Génération des visualisations...")
            _run_visualizations(data, dataset_name)
            
        elif analysis_type == 4:
            # Pixels/QA seulement
            print("🔍 Analyse pixels/QA...")
            _run_pixel_analysis(data, dataset_name)
            
        elif analysis_type == 5:
            # Graphiques quotidiens seulement
            print("📅 Graphiques quotidiens...")
            _run_daily_plots(data, dataset_name)
        
        print(f"✅ Analyse personnalisée de {dataset_name} terminée")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse personnalisée de {dataset_name}: {e}")

# ===========================================
# FONCTIONS DE COMPARAISON
# ===========================================

def run_comparison_analysis():
    """Lance la comparaison complète entre MCD43A3 et MOD10A1"""
    print("\n🔄 COMPARAISON COMPLÈTE MCD43A3 vs MOD10A1")
    print("="*60)
    
    try:
        # Corrélations
        print("📊 Analyse des corrélations...")
        run_correlation_analysis()
        
        # Visualisations comparatives
        print("📈 Visualisations comparatives...")
        run_comparative_visualizations()
        
        print("✅ Comparaison complète terminée")
        
    except Exception as e:
        print(f"❌ Erreur lors de la comparaison: {e}")

def run_correlation_analysis():
    """Lance l'analyse de corrélation entre datasets"""
    print("\n📊 ANALYSE DE CORRÉLATION")
    print("="*50)
    
    try:
        from analysis.comparison import analyze_correlation
        
        # Charger les deux datasets
        mcd43a3_data = _load_dataset('MCD43A3')
        mod10a1_data = _load_dataset('MOD10A1')
        
        # Analyser les corrélations
        correlations = analyze_correlation(mcd43a3_data, mod10a1_data)
        
        # Sauvegarder les résultats
        results_dir = Path("results/comparison")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        print("✅ Analyse de corrélation terminée")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse de corrélation: {e}")

def run_comparative_visualizations():
    """Lance les visualisations comparatives"""
    print("\n📈 VISUALISATIONS COMPARATIVES")
    print("="*50)
    
    try:
        from visualization.comparison_plots import create_comparison_plots
        
        # Charger les deux datasets
        mcd43a3_data = _load_dataset('MCD43A3')
        mod10a1_data = _load_dataset('MOD10A1')
        
        # Créer les visualisations comparatives
        create_comparison_plots(mcd43a3_data, mod10a1_data)
        
        print("✅ Visualisations comparatives générées")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération des visualisations comparatives: {e}")

def run_daily_melt_season_comparison(fraction_choice='pure_ice'):
    """Lance les graphiques quotidiens de comparaison par saison de fonte"""
    print(f"\n📅 GRAPHIQUES QUOTIDIENS - COMPARAISON ({fraction_choice})")
    print("="*60)
    
    try:
        from visualization.comparison_plots import create_daily_melt_season_comparison
        
        # Charger les deux datasets
        mcd43a3_data = _load_dataset('MCD43A3')
        mod10a1_data = _load_dataset('MOD10A1')
        
        # Créer les graphiques par année
        create_daily_melt_season_comparison(mcd43a3_data, mod10a1_data, fraction_choice)
        
        print("✅ Graphiques quotidiens de comparaison générés")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération des graphiques quotidiens: {e}")

# ===========================================
# FONCTIONS SPÉCIALES MOD10A1
# ===========================================

def run_mod10a1_fraction_comparison():
    """Lance la comparaison entre fractions MOD10A1"""
    print("\n🔍 COMPARAISON ENTRE FRACTIONS MOD10A1")
    print("="*50)
    
    try:
        from visualization.pixel_plots.fraction_comparison import create_fraction_comparison_plots
        
        # Charger les données MOD10A1
        data = _load_dataset('MOD10A1')
        
        # Créer les visualisations de comparaison entre fractions
        create_fraction_comparison_plots(data)
        
        print("✅ Comparaison entre fractions MOD10A1 terminée")
        
    except Exception as e:
        print(f"❌ Erreur lors de la comparaison entre fractions: {e}")

def run_elevation_analysis_menu():
    """Lance le menu d'analyse fraction × élévation"""
    print("\n🏔️ ANALYSE FRACTION × ÉLÉVATION")
    print("="*50)
    
    try:
        from analysis.elevation_analysis import run_elevation_analysis
        
        # Lancer l'analyse d'élévation
        run_elevation_analysis()
        
        print("✅ Analyse fraction × élévation terminée")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse fraction × élévation: {e}")

# ===========================================
# FONCTIONS UTILITAIRES INTERNES
# ===========================================

def _load_dataset(dataset_name):
    """Charge un dataset spécifique"""
    try:
        from data.unified_loader import get_albedo_handler
        from config import DATA_MODE, MCD43A3_CONFIG, MOD10A1_CONFIG
        
        if dataset_name == 'MCD43A3':
            config = MCD43A3_CONFIG
        elif dataset_name == 'MOD10A1':
            config = MOD10A1_CONFIG
        else:
            raise ValueError(f"Dataset inconnu: {dataset_name}")
        
        # Use unified loader that respects DATA_MODE setting
        if DATA_MODE.lower() == "database":
            # Database mode: pass dataset name to db_handler
            handler = get_albedo_handler(dataset_name)
        else:
            # CSV mode: pass CSV path to csv_handler  
            handler = get_albedo_handler(config['csv_path'])
            
        data = handler.load_data()
        
        print(f"✅ Dataset {dataset_name} chargé: {len(data)} lignes")
        return data
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement de {dataset_name}: {e}")
        raise

def _run_trend_analysis(data, dataset_name):
    """Lance l'analyse des tendances"""
    try:
        from analysis.trends import analyze_trends
        
        trends_results = analyze_trends(data)
        
        # Sauvegarder les résultats
        results_dir = Path(f"results/{dataset_name.lower()}")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder le tableau de résumé si disponible
        if 'summary_table' in trends_results:
            summary_table = trends_results['summary_table']
            summary_table.to_csv(results_dir / "summary_trends_mean.csv", index=False)
            print(f"📊 Tendances sauvegardées dans {results_dir}/summary_trends_mean.csv")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse des tendances: {e}")

def _run_visualizations(data, dataset_name):
    """Lance les visualisations"""
    try:
        from visualization.charts import create_charts
        
        # Créer les visualisations
        output_dir = f"output/{dataset_name.lower()}"
        create_charts(data, trend_results=None, variable='mean', output_dir=output_dir)
        print(f"📈 Visualisations générées pour {dataset_name}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération des visualisations: {e}")

def _run_pixel_analysis(data, dataset_name):
    """Lance l'analyse des pixels/QA"""
    try:
        from analysis.pixel_analysis import analyze_pixel_quality
        
        analyze_pixel_quality(data, qa_csv_path=None)
        print(f"🔍 Analyse pixels/QA terminée pour {dataset_name}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse pixels/QA: {e}")

def _run_daily_plots(data, dataset_name):
    """Lance les graphiques quotidiens"""
    try:
        from visualization.daily_plots import create_daily_plots
        
        output_dir = f"output/{dataset_name.lower()}"
        create_daily_plots(data, variable='mean', output_dir=output_dir)
        print(f"📅 Graphiques quotidiens générés pour {dataset_name}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération des graphiques quotidiens: {e}")

def run_export_all():
    """Exporte tous les résultats"""
    print("\n📤 EXPORT DE TOUS LES RÉSULTATS")
    print("="*50)
    
    try:
        from utils.exports import export_all_results
        
        export_all_results()
        print("✅ Export terminé")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'export: {e}")