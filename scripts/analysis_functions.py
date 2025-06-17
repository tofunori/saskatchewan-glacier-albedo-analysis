#!/usr/bin/env python3
"""
FONCTIONS D'ANALYSE - Modules séparés pour main.py
=================================================

Ce module contient toutes les fonctions d'analyse pour alléger main.py
"""

import os
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set matplotlib to non-interactive backend
import matplotlib
matplotlib.use('Agg')

# Ajouter le répertoire src au path
script_dir = Path(__file__).parent.absolute()
project_dir = script_dir.parent
src_dir = project_dir / 'src'
sys.path.insert(0, str(src_dir))

PROJECT_DIR = project_dir

# Imports
import numpy as np
from config import CSV_PATH, QA_CSV_PATH, OUTPUT_DIR, ANALYSIS_VARIABLE, FRACTION_CLASSES
from data.handler import AlbedoDataHandler
from analysis.trends import TrendCalculator
from analysis.pixel_analysis import PixelCountAnalyzer
from visualization.monthly import MonthlyVisualizer
from visualization.pixel_plots import PixelVisualizer
from visualization.charts import ChartGenerator
from visualization.daily_plots import create_daily_albedo_plots
from utils.helpers import print_section_header, ensure_directory_exists, print_analysis_summary

def check_config():
    """Vérifie la configuration"""
    if not os.path.exists(CSV_PATH):
        print(f"❌ Fichier CSV non trouvé: {CSV_PATH}")
        return False
    print(f"✅ Fichier CSV principal trouvé : {CSV_PATH}")
    
    if QA_CSV_PATH and os.path.exists(QA_CSV_PATH):
        print(f"✅ Fichier QA CSV trouvé : {QA_CSV_PATH}")
    else:
        print(f"⚠️  Fichier QA CSV non trouvé (analyse QA 0-3 non disponible)")
    
    output_path = PROJECT_DIR / OUTPUT_DIR
    ensure_directory_exists(str(output_path))
    print(f"📁 Répertoire de sortie : {output_path}/")
    
    return True


def run_complete_analysis():
    """Exécute l'analyse complète (comme main_backup.py)"""
    output_path = PROJECT_DIR / OUTPUT_DIR
    
    try:
        print_section_header("ANALYSE COMPLÈTE - TOUTES LES ÉTAPES", level=1)
        
        # ÉTAPE 1: Chargement des données
        print_section_header("ÉTAPE 1: Chargement des données", level=1)
        data_handler = AlbedoDataHandler(CSV_PATH)
        data_handler.load_data()
        data_handler.print_data_summary()
        
        # ÉTAPE 2: Calculs statistiques de base  
        print_section_header("ÉTAPE 2: Analyses de tendances de base", level=1)
        trend_calculator = TrendCalculator(data_handler)
        basic_results = trend_calculator.calculate_basic_trends(ANALYSIS_VARIABLE)
        trend_calculator.print_summary(ANALYSIS_VARIABLE)
        
        # ÉTAPE 3: Analyses mensuelles
        print_section_header("ÉTAPE 3: Analyses saisonnières et mensuelles", level=1)
        monthly_results = trend_calculator.calculate_monthly_trends(ANALYSIS_VARIABLE)
        
        # ÉTAPE 4: Graphiques mensuels
        print_section_header("ÉTAPE 4: Création des graphiques mensuels", level=1)
        monthly_visualizer = MonthlyVisualizer(data_handler)
        
        monthly_graph_path = monthly_visualizer.create_monthly_statistics_graphs(
            ANALYSIS_VARIABLE, 
            str(output_path / f'monthly_statistics_{ANALYSIS_VARIABLE}.png')
        )
        
        if monthly_graph_path:
            print(f"🎨 Graphiques mensuels créés : {monthly_graph_path}")
        
        if monthly_results:
            comparison_path = monthly_visualizer.create_seasonal_trends_comparison(
                monthly_results, ANALYSIS_VARIABLE,
                str(output_path / f'monthly_comparison_{ANALYSIS_VARIABLE}.png')
            )
            monthly_visualizer.print_monthly_summary(ANALYSIS_VARIABLE)
        
        # ÉTAPE 5: Autres visualisations
        print_section_header("ÉTAPE 5: Visualisations additionnelles", level=1)
        try:
            chart_generator = ChartGenerator(data_handler)
            
            overview_path = chart_generator.create_trend_overview_graph(
                basic_results, ANALYSIS_VARIABLE,
                str(output_path / f'trend_overview_{ANALYSIS_VARIABLE}.png')
            )
            
            patterns_path = chart_generator.create_seasonal_patterns_graph(
                ANALYSIS_VARIABLE,
                str(output_path / f'seasonal_patterns_{ANALYSIS_VARIABLE}.png')
            )
            
            print("✅ Visualisations additionnelles créées")
        except Exception as e:
            print(f"⚠️  Erreur visualisations additionnelles: {e}")
        
        # ÉTAPE 6: Analyse des pixels
        print_section_header("ÉTAPE 6: Analyse des comptages de pixels", level=1)
        try:
            pixel_analyzer = PixelCountAnalyzer(data_handler, qa_csv_path=QA_CSV_PATH)
            
            monthly_pixel_results = pixel_analyzer.analyze_monthly_pixel_counts()
            true_qa_results = pixel_analyzer.analyze_true_qa_statistics()
            qa_results = pixel_analyzer.analyze_seasonal_qa_statistics()
            total_pixel_results = pixel_analyzer.analyze_total_pixel_trends()
            
            print("✅ Analyses de pixels terminées")
        except Exception as e:
            print(f"⚠️  Erreur analyse pixels: {e}")
            monthly_pixel_results = {}
            true_qa_results = {}
            qa_results = {}
            total_pixel_results = {}
        
        # ÉTAPE 7: Visualisations pixels/QA
        print_section_header("ÉTAPE 7: Visualisations des pixels et QA", level=1)
        try:
            pixel_visualizer = PixelVisualizer(data_handler)
            
            if monthly_pixel_results:
                pixel_visualizer.create_monthly_pixel_count_plots(
                    monthly_pixel_results,
                    str(output_path / 'pixel_counts_by_month_fraction.png')
                )
            
            if true_qa_results:
                pixel_visualizer.create_qa_statistics_plots(
                    true_qa_results,
                    str(output_path / 'qa_statistics_by_season.png')
                )
            
            if monthly_pixel_results and qa_results:
                pixel_visualizer.create_pixel_availability_heatmap(
                    monthly_pixel_results, qa_results,
                    str(output_path / 'pixel_availability_heatmap.png')
                )
            
            if total_pixel_results:
                pixel_visualizer.create_total_pixels_timeseries(
                    total_pixel_results,
                    str(output_path / 'total_pixels_timeseries.png')
                )
            
            print("✅ Visualisations de pixels créées")
        except Exception as e:
            print(f"⚠️  Erreur visualisations pixels: {e}")
        
        # ÉTAPE 8: Graphiques quotidiens
        print_section_header("ÉTAPE 8: Graphiques quotidiens par saison de fonte", level=1)
        try:
            # Graphiques quotidiens pixels/QA
            if 'pixel_analyzer' in locals() and 'pixel_visualizer' in locals():
                daily_plots = pixel_visualizer.create_daily_melt_season_plots(
                    pixel_analyzer, 
                    str(output_path)
                )
                print(f"✅ {len(daily_plots)} graphiques quotidiens pixels/QA créés")
            
            # Graphiques quotidiens d'albédo - DÉSACTIVÉ
            # albedo_plots = create_daily_albedo_plots(data_handler, str(output_path))
            # print(f"✅ {len(albedo_plots)} graphiques quotidiens d'albédo créés")
            albedo_plots = []
            
        except Exception as e:
            print(f"⚠️  Erreur graphiques quotidiens: {e}")
        
        # ÉTAPE 9: Exports
        print_section_header("ÉTAPE 9: Export des résultats", level=1)
        try:
            summary_table = trend_calculator.get_summary_table(ANALYSIS_VARIABLE)
            summary_csv_path = str(output_path / f'summary_trends_{ANALYSIS_VARIABLE}.csv')
            summary_table.to_csv(summary_csv_path, index=False)
            print(f"📊 Tableau de résumé exporté : {summary_csv_path}")
            
            monthly_table = monthly_visualizer.create_monthly_summary_table(ANALYSIS_VARIABLE)
            if not monthly_table.empty:
                monthly_csv_path = str(output_path / f'monthly_stats_{ANALYSIS_VARIABLE}.csv')
                monthly_table.to_csv(monthly_csv_path, index=False)
                print(f"📅 Statistiques mensuelles exportées : {monthly_csv_path}")
            
            cleaned_data_path = data_handler.export_cleaned_data(
                str(output_path / f'cleaned_data_{ANALYSIS_VARIABLE}.csv')
            )
            
            if 'pixel_analyzer' in locals():
                pixel_exports = pixel_analyzer.export_pixel_analysis_results(str(output_path))
        except Exception as e:
            print(f"⚠️  Erreur exports: {e}")
        
        # RÉSUMÉ FINAL
        all_results = {
            'basic_trends': basic_results,
            'monthly_trends': monthly_results,
            'data_summary': data_handler.get_data_summary()
        }
        
        print_analysis_summary(all_results)
        
        print_section_header("FICHIERS GÉNÉRÉS", level=1)
        list_files(output_path)
        
        print("\n🎉 ANALYSE COMPLÈTE TERMINÉE AVEC SUCCÈS !")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DE L'ANALYSE : {e}")
        import traceback
        traceback.print_exc()
        return False

def run_trends_only():
    """Exécute seulement les analyses de tendances"""
    output_path = PROJECT_DIR / OUTPUT_DIR
    
    try:
        print_section_header("ANALYSES DE TENDANCES SEULEMENT", level=1)
        
        data_handler = AlbedoDataHandler(CSV_PATH)
        data_handler.load_data()
        data_handler.print_data_summary()
        
        trend_calculator = TrendCalculator(data_handler)
        basic_results = trend_calculator.calculate_basic_trends(ANALYSIS_VARIABLE)
        trend_calculator.print_summary(ANALYSIS_VARIABLE)
        
        monthly_results = trend_calculator.calculate_monthly_trends(ANALYSIS_VARIABLE)
        
        # Export
        summary_table = trend_calculator.get_summary_table(ANALYSIS_VARIABLE)
        summary_csv_path = str(output_path / f'summary_trends_{ANALYSIS_VARIABLE}.csv')
        summary_table.to_csv(summary_csv_path, index=False)
        print(f"📊 Tableau de résumé exporté : {summary_csv_path}")
        
        all_results = {
            'basic_trends': basic_results,
            'monthly_trends': monthly_results,
            'data_summary': data_handler.get_data_summary()
        }
        print_analysis_summary(all_results)
        
        print("\n✅ ANALYSES DE TENDANCES TERMINÉES !")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        return False

def run_visualizations_only():
    """Exécute seulement les visualisations"""
    output_path = PROJECT_DIR / OUTPUT_DIR
    
    try:
        print_section_header("VISUALISATIONS SEULEMENT", level=1)
        
        data_handler = AlbedoDataHandler(CSV_PATH)
        data_handler.load_data()
        
        trend_calculator = TrendCalculator(data_handler)
        basic_results = trend_calculator.calculate_basic_trends(ANALYSIS_VARIABLE)
        monthly_results = trend_calculator.calculate_monthly_trends(ANALYSIS_VARIABLE)
        
        monthly_visualizer = MonthlyVisualizer(data_handler)
        
        monthly_graph_path = monthly_visualizer.create_monthly_statistics_graphs(
            ANALYSIS_VARIABLE, 
            str(output_path / f'monthly_statistics_{ANALYSIS_VARIABLE}.png')
        )
        
        if monthly_results:
            monthly_visualizer.create_seasonal_trends_comparison(
                monthly_results, ANALYSIS_VARIABLE,
                str(output_path / f'monthly_comparison_{ANALYSIS_VARIABLE}.png')
            )
        
        try:
            chart_generator = ChartGenerator(data_handler)
            chart_generator.create_trend_overview_graph(
                basic_results, ANALYSIS_VARIABLE,
                str(output_path / f'trend_overview_{ANALYSIS_VARIABLE}.png')
            )
            chart_generator.create_seasonal_patterns_graph(
                ANALYSIS_VARIABLE,
                str(output_path / f'seasonal_patterns_{ANALYSIS_VARIABLE}.png')
            )
        except:
            pass
        
        print("\n✅ VISUALISATIONS TERMINÉES !")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        return False

def run_pixels_only():
    """Exécute seulement l'analyse des pixels"""
    output_path = PROJECT_DIR / OUTPUT_DIR
    
    try:
        print_section_header("ANALYSE PIXELS/QA SEULEMENT", level=1)
        
        data_handler = AlbedoDataHandler(CSV_PATH)
        data_handler.load_data()
        
        pixel_analyzer = PixelCountAnalyzer(data_handler, qa_csv_path=QA_CSV_PATH)
        monthly_pixel_results = pixel_analyzer.analyze_monthly_pixel_counts()
        true_qa_results = pixel_analyzer.analyze_true_qa_statistics()
        qa_results = pixel_analyzer.analyze_seasonal_qa_statistics()
        total_pixel_results = pixel_analyzer.analyze_total_pixel_trends()
        
        pixel_visualizer = PixelVisualizer(data_handler)
        
        if monthly_pixel_results:
            pixel_visualizer.create_monthly_pixel_count_plots(
                monthly_pixel_results,
                str(output_path / 'pixel_counts_by_month_fraction.png')
            )
        
        if true_qa_results:
            pixel_visualizer.create_qa_statistics_plots(
                true_qa_results,
                str(output_path / 'qa_statistics_by_season.png')
            )
        
        pixel_analyzer.export_pixel_analysis_results(str(output_path))
        
        print("\n✅ ANALYSE PIXELS/QA TERMINÉE !")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        return False

def run_daily_only():
    """Exécute seulement les graphiques quotidiens"""
    output_path = PROJECT_DIR / OUTPUT_DIR
    
    try:
        print_section_header("GRAPHIQUES QUOTIDIENS SEULEMENT", level=1)
        
        data_handler = AlbedoDataHandler(CSV_PATH)
        data_handler.load_data()
        
        # Graphiques quotidiens pixels/QA
        print_section_header("Graphiques quotidiens pixels/QA", level=2)
        pixel_analyzer = PixelCountAnalyzer(data_handler, qa_csv_path=QA_CSV_PATH)
        
        # Load QA data before creating visualizations
        pixel_analyzer.load_qa_data()
        
        pixel_visualizer = PixelVisualizer(data_handler)
        
        daily_plots = pixel_visualizer.create_daily_melt_season_plots(
            pixel_analyzer, 
            str(output_path)
        )
        print(f"✅ {len(daily_plots)} graphiques quotidiens pixels/QA créés")
        
        # Graphiques quotidiens d'albédo - DÉSACTIVÉ
        # albedo_plots = create_daily_albedo_plots(data_handler, str(output_path))
        # print(f"✅ {len(albedo_plots)} graphiques quotidiens d'albédo créés")
        albedo_plots = []
        
        print(f"\n✅ GRAPHIQUES QUOTIDIENS TERMINÉS !")
        print(f"   📊 {len(daily_plots)} graphiques pixels/QA")
        print(f"   📈 {len(albedo_plots)} graphiques d'albédo")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        return False

def list_files(output_path):
    """Liste les fichiers générés"""
    files = list(output_path.glob('*'))
    if files:
        print(f"\n📁 {len(files)} fichiers dans {output_path}/:")
        for file in sorted(files):
            if file.is_file():
                size_kb = file.stat().st_size / 1024
                print(f"  ✅ {file.name} ({size_kb:.1f} KB)")

# ============================================================================
# NOUVELLES FONCTIONS POUR SUPPORT MULTI-DATASETS
# ============================================================================

def check_datasets_availability():
    """Vérifie la disponibilité des datasets"""
    try:
        from config import get_available_datasets
        datasets = get_available_datasets()
        
        available_count = 0
        for name, info in datasets.items():
            if info['csv_exists']:
                available_count += 1
        
        if available_count == 0:
            print("❌ Aucun dataset disponible")
            return False
        
        print(f"✅ {available_count} dataset(s) disponible(s)")
        return True
        
    except Exception as e:
        print(f"❌ Erreur vérification datasets: {e}")
        return False

def run_dataset_analysis(dataset_name):
    """Exécute l'analyse pour un dataset spécifique"""
    # Créer le dossier spécifique au dataset
    dataset_output_path = PROJECT_DIR / OUTPUT_DIR / dataset_name.lower()
    ensure_directory_exists(str(dataset_output_path))
    
    try:
        from config import get_dataset_config, print_config_summary
        from data.dataset_manager import DatasetManager
        
        print_section_header(f"ANALYSE DATASET {dataset_name}", level=1)
        print(f"📁 Dossier de sortie: {dataset_output_path}")
        
        # Afficher la configuration du dataset
        print_config_summary(dataset_name)
        
        # Charger le dataset
        manager = DatasetManager()
        dataset = manager.load_dataset(dataset_name)
        
        # Créer le data handler compatible
        config = get_dataset_config(dataset_name)
        data_handler = AlbedoDataHandler(config['csv_path'])
        data_handler.load_data()
        
        # Exécuter l'analyse complète avec ce dataset
        trend_calculator = TrendCalculator(data_handler)
        basic_results = trend_calculator.calculate_basic_trends(ANALYSIS_VARIABLE)
        trend_calculator.print_summary(ANALYSIS_VARIABLE)
        
        # Visualisations
        print_section_header("Visualisations standards", level=2)
        monthly_visualizer = MonthlyVisualizer(data_handler)
        # Créer les graphiques mensuels avec le nom correct de la méthode
        monthly_plot_path = monthly_visualizer.create_monthly_statistics_graphs(
            ANALYSIS_VARIABLE, 
            save_path=str(dataset_output_path / f'monthly_statistics_{ANALYSIS_VARIABLE}.png')
        )
        monthly_plots = [monthly_plot_path] if monthly_plot_path else []
        
        # Export des résultats de tendances
        summary_table = trend_calculator.get_summary_table(ANALYSIS_VARIABLE)
        trend_path = str(dataset_output_path / f'summary_trends_{ANALYSIS_VARIABLE}.csv')
        summary_table.to_csv(trend_path, index=False)
        print(f"📊 Résultats de tendances exportés : {trend_path}")
        
        print(f"\n✅ ANALYSE {dataset_name} TERMINÉE !")
        print(f"📁 Tous les résultats dans: {dataset_output_path}")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR ANALYSE {dataset_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comparison_analysis():
    """Exécute l'analyse comparative complète"""
    # Créer le dossier pour les comparaisons
    comparison_output_path = PROJECT_DIR / OUTPUT_DIR / "comparison"
    ensure_directory_exists(str(comparison_output_path))
    
    try:
        from data.dataset_manager import DatasetManager
        from analysis.comparison import ComparisonAnalyzer
        from visualization.comparison_plots import ComparisonVisualizer
        
        print_section_header("ANALYSE COMPARATIVE MCD43A3 vs MOD10A1", level=1)
        print(f"📁 Dossier de sortie: {comparison_output_path}")
        
        # Préparer les données de comparaison
        manager = DatasetManager()
        comparison_data = manager.prepare_comparison_data(sync_dates=True)
        manager.print_comparison_summary()
        
        # Analyses statistiques
        print_section_header("Analyses statistiques comparatives", level=2)
        analyzer = ComparisonAnalyzer(comparison_data)
        
        # Corrélations
        correlations = analyzer.calculate_correlations('pearson')
        
        # Différences
        differences = analyzer.calculate_differences()
        
        # Patterns temporels
        temporal_patterns = analyzer.analyze_temporal_patterns()
        
        # Comparaison des tendances
        trend_comparison = analyzer.compare_trend_analyses()
        
        # Résumé
        analyzer.print_summary()
        
        # Visualisations
        print_section_header("Visualisations comparatives", level=2)
        visualizer = ComparisonVisualizer(comparison_data, str(comparison_output_path))
        plots = visualizer.generate_all_plots()
        
        # Exports
        analyzer.export_comparison_results(str(comparison_output_path))
        
        print(f"\n✅ ANALYSE COMPARATIVE TERMINÉE !")
        print(f"   📊 {len(plots)} graphiques générés")
        print(f"📁 Tous les résultats dans: {comparison_output_path}")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR ANALYSE COMPARATIVE: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_correlation_analysis():
    """Exécute seulement l'analyse de corrélation"""
    # Créer le dossier pour les comparaisons
    comparison_output_path = PROJECT_DIR / OUTPUT_DIR / "comparison"
    ensure_directory_exists(str(comparison_output_path))
    
    try:
        from data.dataset_manager import DatasetManager
        from analysis.comparison import ComparisonAnalyzer
        
        print_section_header("ANALYSE DE CORRÉLATION", level=1)
        print(f"📁 Dossier de sortie: {comparison_output_path}")
        
        manager = DatasetManager()
        comparison_data = manager.prepare_comparison_data(sync_dates=True)
        
        analyzer = ComparisonAnalyzer(comparison_data)
        
        # Corrélations Pearson et Spearman
        print_section_header("Corrélations Pearson", level=2)
        pearson_corr = analyzer.calculate_correlations('pearson')
        
        print_section_header("Corrélations Spearman", level=2)
        spearman_corr = analyzer.calculate_correlations('spearman')
        
        # Export
        corr_path = str(comparison_output_path / 'correlations_detailed.csv')
        import pandas as pd
        
        corr_df = pd.DataFrame({
            'fraction': FRACTION_CLASSES,
            'pearson_r': [pearson_corr.get(f, {}).get('correlation', np.nan) for f in FRACTION_CLASSES],
            'pearson_p': [pearson_corr.get(f, {}).get('p_value', np.nan) for f in FRACTION_CLASSES],
            'spearman_r': [spearman_corr.get(f, {}).get('correlation', np.nan) for f in FRACTION_CLASSES],
            'spearman_p': [spearman_corr.get(f, {}).get('p_value', np.nan) for f in FRACTION_CLASSES]
        })
        corr_df.to_csv(corr_path, index=False)
        
        print(f"\n✅ ANALYSE DE CORRÉLATION TERMINÉE !")
        print(f"   📊 Résultats exportés: {corr_path}")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR ANALYSE CORRÉLATION: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_daily_melt_season_comparison(fraction='pure_ice'):
    """Exécute la génération de graphiques quotidiens de saison de fonte pour comparaison"""
    comparison_output_path = PROJECT_DIR / OUTPUT_DIR / "comparison"
    ensure_directory_exists(str(comparison_output_path))
    
    try:
        from data.dataset_manager import DatasetManager
        from visualization.comparison_plots import ComparisonVisualizer
        
        print_section_header(f"GRAPHIQUES QUOTIDIENS SAISON DE FONTE - {fraction.upper()}", level=1)
        print(f"📁 Dossier de sortie: {comparison_output_path}")
        
        # Préparer les données de comparaison
        manager = DatasetManager()
        comparison_data = manager.prepare_comparison_data(sync_dates=False)  # Pas de sync pour avoir toutes les données
        
        # Créer les visualisations
        visualizer = ComparisonVisualizer(comparison_data, str(comparison_output_path))
        daily_plots = visualizer.plot_daily_melt_season_comparison(fraction, save=True)
        
        print(f"\n✅ GRAPHIQUES QUOTIDIENS SAISON DE FONTE TERMINÉS !")
        print(f"   📊 {len(daily_plots)} graphiques générés pour {fraction}")
        print(f"📁 Graphiques sauvegardés dans: {comparison_output_path}")
        
        # Lister les fichiers créés
        for plot_path in daily_plots:
            print(f"  ✓ {plot_path}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR GRAPHIQUES QUOTIDIENS: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_custom_analysis(dataset_name, analysis_type):
    """Exécute une analyse personnalisée"""
    try:
        print_section_header(f"ANALYSE PERSONNALISÉE - {dataset_name}", level=1)
        
        if analysis_type == 1:  # Analyse complète
            return run_dataset_analysis(dataset_name)
        elif analysis_type == 2:  # Tendances seulement
            return _run_trends_for_dataset(dataset_name)
        elif analysis_type == 3:  # Visualisations seulement
            return _run_visualizations_for_dataset(dataset_name)
        elif analysis_type == 4:  # Pixels/QA seulement
            return _run_pixels_for_dataset(dataset_name)
        elif analysis_type == 5:  # Graphiques quotidiens
            return _run_daily_for_dataset(dataset_name)
        else:
            print("❌ Type d'analyse invalide")
            return False
            
    except Exception as e:
        print(f"\n❌ ERREUR ANALYSE PERSONNALISÉE: {e}")
        return False

def _run_trends_for_dataset(dataset_name):
    """Exécute les tendances pour un dataset spécifique"""
    try:
        from config import get_dataset_config
        
        # Créer le dossier spécifique au dataset
        dataset_output_path = PROJECT_DIR / OUTPUT_DIR / dataset_name.lower()
        ensure_directory_exists(str(dataset_output_path))
        
        config = get_dataset_config(dataset_name)
        data_handler = AlbedoDataHandler(config['csv_path'])
        data_handler.load_data()
        
        trend_calculator = TrendCalculator(data_handler)
        basic_results = trend_calculator.calculate_basic_trends(ANALYSIS_VARIABLE)
        trend_calculator.print_summary(ANALYSIS_VARIABLE)
        
        # Export des résultats
        summary_table = trend_calculator.get_summary_table(ANALYSIS_VARIABLE)
        trend_path = str(dataset_output_path / f'summary_trends_{ANALYSIS_VARIABLE}.csv')
        summary_table.to_csv(trend_path, index=False)
        print(f"📊 Résultats de tendances exportés : {trend_path}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur tendances {dataset_name}: {e}")
        return False

def _run_visualizations_for_dataset(dataset_name):
    """Exécute les visualisations pour un dataset spécifique"""
    try:
        from config import get_dataset_config
        
        # Créer le dossier spécifique au dataset
        dataset_output_path = PROJECT_DIR / OUTPUT_DIR / dataset_name.lower()
        ensure_directory_exists(str(dataset_output_path))
        
        config = get_dataset_config(dataset_name)
        data_handler = AlbedoDataHandler(config['csv_path'])
        data_handler.load_data()
        
        monthly_visualizer = MonthlyVisualizer(data_handler)
        # Créer les graphiques mensuels
        monthly_plot_path = monthly_visualizer.create_monthly_statistics_graphs(
            ANALYSIS_VARIABLE,
            save_path=str(dataset_output_path / f'monthly_statistics_{ANALYSIS_VARIABLE}.png')
        )
        plots = [monthly_plot_path] if monthly_plot_path else []
        
        print(f"✅ {len(plots)} visualisations créées pour {dataset_name}")
        print(f"📁 Résultats sauvegardés dans: {dataset_output_path}")
        return True
    except Exception as e:
        print(f"❌ Erreur visualisations {dataset_name}: {e}")
        return False

def _run_pixels_for_dataset(dataset_name):
    """Exécute l'analyse pixels pour un dataset spécifique"""
    try:
        from config import get_dataset_config
        
        # Créer le dossier spécifique au dataset
        dataset_output_path = PROJECT_DIR / OUTPUT_DIR / dataset_name.lower()
        ensure_directory_exists(str(dataset_output_path))
        
        config = get_dataset_config(dataset_name)
        data_handler = AlbedoDataHandler(config['csv_path'])
        data_handler.load_data()
        
        qa_path = config.get('qa_csv_path')
        if qa_path and os.path.exists(qa_path):
            pixel_analyzer = PixelCountAnalyzer(data_handler, qa_csv_path=qa_path)
            pixel_analyzer.load_qa_data()
            
            pixel_visualizer = PixelVisualizer(data_handler)
            plots = pixel_visualizer.create_daily_melt_season_plots(
                pixel_analyzer, 
                str(dataset_output_path),
                dataset_suffix=f"_{dataset_name.lower()}"
            )
            
            print(f"✅ {len(plots)} analyses pixels créées pour {dataset_name}")
            print(f"📁 Résultats sauvegardés dans: {dataset_output_path}")
        else:
            print(f"⚠️ Pas de données QA disponibles pour {dataset_name}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur pixels {dataset_name}: {e}")
        return False

def _run_daily_for_dataset(dataset_name):
    """Exécute les graphiques quotidiens pour un dataset spécifique"""
    try:
        return _run_pixels_for_dataset(dataset_name)  # Même fonction pour l'instant
    except Exception as e:
        print(f"❌ Erreur quotidien {dataset_name}: {e}")
        return False

def run_comparative_visualizations():
    """Génère toutes les visualisations comparatives"""
    try:
        from data.dataset_manager import DatasetManager
        from visualization.comparison_plots import ComparisonVisualizer
        
        # Créer le dossier pour les comparaisons
        comparison_output_path = PROJECT_DIR / OUTPUT_DIR / "comparison"
        ensure_directory_exists(str(comparison_output_path))
        
        print_section_header("VISUALISATIONS COMPARATIVES", level=1)
        print(f"📁 Dossier de sortie: {comparison_output_path}")
        
        manager = DatasetManager()
        comparison_data = manager.prepare_comparison_data(sync_dates=True)
        
        visualizer = ComparisonVisualizer(comparison_data, str(comparison_output_path))
        plots = visualizer.generate_all_plots()
        
        print(f"\n✅ VISUALISATIONS COMPARATIVES TERMINÉES !")
        print(f"   📈 {len(plots)} graphiques générés")
        print(f"📁 Tous les résultats dans: {comparison_output_path}")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR VISUALISATIONS: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_export_all():
    """Exporte tous les résultats disponibles"""
    try:
        print_section_header("EXPORT DE TOUS LES RÉSULTATS", level=1)
        
        output_path = PROJECT_DIR / OUTPUT_DIR
        success_count = 0
        
        # Export MCD43A3
        try:
            run_dataset_analysis('MCD43A3')
            success_count += 1
        except Exception as e:
            print(f"⚠️ Échec export MCD43A3: {e}")
        
        # Export MOD10A1
        try:
            run_dataset_analysis('MOD10A1')
            success_count += 1
        except Exception as e:
            print(f"⚠️ Échec export MOD10A1: {e}")
        
        # Export comparaison
        try:
            run_comparison_analysis()
            success_count += 1
        except Exception as e:
            print(f"⚠️ Échec export comparaison: {e}")
        
        print(f"\n✅ EXPORTS TERMINÉS !")
        print(f"   📊 {success_count}/3 analyses exportées avec succès")
        list_files(output_path)
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR EXPORTS: {e}")
        return False

def run_mod10a1_fraction_comparison():
    """Exécute la comparaison des fractions MOD10A1"""
    try:
        from config import get_dataset_config, FRACTION_CLASSES, CLASS_LABELS
        
        print_section_header("COMPARAISON DES FRACTIONS MOD10A1", level=1)
        
        # Créer le dossier de sortie spécifique
        output_path = PROJECT_DIR / OUTPUT_DIR / "mod10a1" / "fraction_comparison"
        ensure_directory_exists(str(output_path))
        print(f"📁 Dossier de sortie: {output_path}")
        
        # Charger les données MOD10A1
        config = get_dataset_config('MOD10A1')
        data_handler = AlbedoDataHandler(config['csv_path'])
        data_handler.load_data()
        
        print(f"✅ Données MOD10A1 chargées: {len(data_handler.data)} observations")
        print(f"📅 Période: {data_handler.data['date'].min()} à {data_handler.data['date'].max()}")
        
        # Sélection interactive des fractions
        selected_fractions = _select_fractions_for_comparison()
        
        # Créer le visualiseur
        pixel_visualizer = PixelVisualizer(data_handler)
        
        # Filtrer les données pour les fractions sélectionnées si nécessaire
        if selected_fractions != 'all':
            print(f"🎯 Fractions sélectionnées: {[CLASS_LABELS[f] for f in selected_fractions]}")
            # Modifier temporairement les fractions du visualiseur
            original_fractions = pixel_visualizer.fraction_classes.copy()
            pixel_visualizer.fraction_classes = selected_fractions
        else:
            print(f"🎯 Toutes les fractions sélectionnées: {[CLASS_LABELS[f] for f in FRACTION_CLASSES]}")
        
        # Générer les comparaisons
        print_section_header("Génération des graphiques de comparaison", level=2)
        plots = pixel_visualizer.plot_mod10a1_fraction_comparison(save_dir=str(output_path))
        
        # Restaurer les fractions originales si modifiées
        if selected_fractions != 'all':
            pixel_visualizer.fraction_classes = original_fractions
        
        # Résumé des résultats
        print(f"\n✅ COMPARAISON DES FRACTIONS MOD10A1 TERMINÉE !")
        print(f"   📊 {len(plots)} graphiques générés")
        print(f"   📁 Résultats sauvegardés dans: {output_path}")
        
        # Lister les fichiers créés
        for plot_path in plots:
            filename = os.path.basename(plot_path)
            print(f"  ✓ {filename}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR COMPARAISON FRACTIONS MOD10A1: {e}")
        import traceback
        traceback.print_exc()
        return False

def _select_fractions_for_comparison():
    """Permet à l'utilisateur de sélectionner les fractions à comparer"""
    from config import FRACTION_CLASSES, CLASS_LABELS
    
    print_section_header("SÉLECTION DES FRACTIONS À COMPARER", level=3)
    print("Choisissez les fractions à inclure dans la comparaison:")
    print()
    
    # Afficher toutes les fractions disponibles
    for i, fraction in enumerate(FRACTION_CLASSES, 1):
        print(f"{i}️⃣  {CLASS_LABELS[fraction]}")
    
    print(f"{len(FRACTION_CLASSES) + 1}️⃣  Toutes les fractions (recommandé)")
    print()
    print("-" * 60)
    
    while True:
        try:
            choice = input(f"➤ Votre choix (1-{len(FRACTION_CLASSES) + 1}): ").strip()
            
            if choice == str(len(FRACTION_CLASSES) + 1):
                # Toutes les fractions
                return 'all'
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(FRACTION_CLASSES):
                # Une seule fraction sélectionnée - demander si l'utilisateur veut en ajouter d'autres
                selected = [FRACTION_CLASSES[choice_num - 1]]
                print(f"✅ Fraction sélectionnée: {CLASS_LABELS[selected[0]]}")
                
                # Demander si l'utilisateur veut ajouter d'autres fractions
                print("\nVoulez-vous ajouter d'autres fractions? (o/n)")
                add_more = input("➤ ").strip().lower()
                
                if add_more in ['o', 'oui', 'y', 'yes']:
                    return _select_multiple_fractions(selected)
                else:
                    return selected
            else:
                print(f"❌ '{choice}' n'est pas valide. Tapez un chiffre de 1 à {len(FRACTION_CLASSES) + 1}.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interruption.")
            return 'all'  # Valeur par défaut
        except ValueError:
            print(f"❌ Erreur de saisie. Tapez un chiffre de 1 à {len(FRACTION_CLASSES) + 1}.")
        except:
            print(f"❌ Erreur de saisie. Tapez un chiffre de 1 à {len(FRACTION_CLASSES) + 1}.")

def _select_multiple_fractions(already_selected):
    """Permet la sélection de fractions multiples"""
    from config import FRACTION_CLASSES, CLASS_LABELS
    
    available = [f for f in FRACTION_CLASSES if f not in already_selected]
    
    print(f"\nFractions déjà sélectionnées: {[CLASS_LABELS[f] for f in already_selected]}")
    print("Fractions disponibles:")
    print()
    
    for i, fraction in enumerate(available, 1):
        print(f"{i}️⃣  {CLASS_LABELS[fraction]}")
    
    print(f"{len(available) + 1}️⃣  Terminer la sélection")
    print()
    
    while True:
        try:
            choice = input(f"➤ Ajouter une fraction (1-{len(available) + 1}): ").strip()
            
            if choice == str(len(available) + 1):
                # Terminer
                return already_selected
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(available):
                new_fraction = available[choice_num - 1]
                already_selected.append(new_fraction)
                available.remove(new_fraction)
                
                print(f"✅ Ajouté: {CLASS_LABELS[new_fraction]}")
                print(f"📋 Sélection actuelle: {[CLASS_LABELS[f] for f in already_selected]}")
                
                if not available:
                    print("✅ Toutes les fractions ont été sélectionnées!")
                    return already_selected
                    
                # Demander si l'utilisateur veut continuer
                print("\nAjouter une autre fraction? (o/n)")
                cont = input("➤ ").strip().lower()
                if cont not in ['o', 'oui', 'y', 'yes']:
                    return already_selected
            else:
                print(f"❌ '{choice}' n'est pas valide. Tapez un chiffre de 1 à {len(available) + 1}.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interruption.")
            return already_selected
        except ValueError:
            print(f"❌ Erreur de saisie. Tapez un chiffre de 1 à {len(available) + 1}.")
        except:
            print(f"❌ Erreur de saisie. Tapez un chiffre de 1 à {len(available) + 1}.")