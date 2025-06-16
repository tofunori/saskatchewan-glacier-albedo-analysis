#!/usr/bin/env python3
"""
MENU POUR VS CODE INTERACTIVE WINDOW
===================================

Ce script définit des fonctions simples que vous pouvez appeler directement
dans la fenêtre interactive de VS Code.

UTILISATION DANS VS CODE:
1. Exécutez ce fichier (Ctrl+F5)
2. Dans le terminal interactif, tapez simplement:
   
   option1()  # Pour l'analyse complète
   option2()  # Pour les tendances
   option3()  # Pour les visualisations  
   option4()  # Pour les pixels/QA
   option5()  # Pour les graphiques quotidiens
   menu()     # Pour revoir le menu

C'est tout! Pas d'input() qui ne fonctionne pas.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set matplotlib to non-interactive backend
import matplotlib
matplotlib.use('Agg')

# Ajouter le répertoire du projet au path
script_dir = Path(__file__).parent.absolute()
project_dir = script_dir.parent
src_dir = project_dir / 'src'
sys.path.insert(0, str(src_dir))

print(f"📂 Répertoire de travail: {Path.cwd()}")
print(f"📁 Répertoire du projet: {project_dir}")
print(f"📁 Répertoire src: {src_dir}")

PROJECT_DIR = project_dir

# Imports
try:
    from saskatchewan_albedo.config import CSV_PATH, QA_CSV_PATH, OUTPUT_DIR, ANALYSIS_VARIABLE, print_config_summary
    from saskatchewan_albedo.data.handler import AlbedoDataHandler
    from saskatchewan_albedo.analysis.trends import TrendCalculator
    from saskatchewan_albedo.analysis.pixel_analysis import PixelCountAnalyzer
    from saskatchewan_albedo.visualization.monthly import MonthlyVisualizer
    from saskatchewan_albedo.visualization.pixel_plots import PixelVisualizer
    from saskatchewan_albedo.visualization.charts import ChartGenerator
    from saskatchewan_albedo.utils.helpers import print_section_header, ensure_directory_exists, print_analysis_summary
    print("✅ Modules importés avec succès")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)

def check_config():
    """Vérifie la configuration"""
    if not os.path.exists(CSV_PATH):
        print(f"❌ Fichier CSV non trouvé: {CSV_PATH}")
        return False
    print(f"✅ Fichier CSV trouvé: {CSV_PATH}")
    
    output_path = PROJECT_DIR / OUTPUT_DIR
    ensure_directory_exists(str(output_path))
    print(f"📁 Répertoire de sortie: {output_path}/")
    return True

def menu():
    """Affiche le menu des options"""
    print("\n" + "="*60)
    print("🚀 MENU D'ANALYSE - VS CODE INTERACTIVE")
    print("="*60)
    print()
    print("Tapez directement ces commandes:")
    print()
    print("option1()  📊 Analyse complète (toutes les étapes)")
    print("option2()  📈 Analyses de tendances seulement")
    print("option3()  🎨 Visualisations seulement")
    print("option4()  🔍 Analyse pixels/QA seulement")
    print("option5()  📅 Graphiques quotidiens seulement")
    print()
    print("menu()     📋 Revoir ce menu")
    print()
    print("="*60)

def option1():
    """1️⃣ Analyse complète"""
    if not check_config():
        return
    
    print("\n🔄 LANCEMENT DE L'ANALYSE COMPLÈTE...")
    output_path = PROJECT_DIR / OUTPUT_DIR
    
    try:
        # Chargement des données
        print_section_header("CHARGEMENT DES DONNÉES", level=1)
        data_handler = AlbedoDataHandler(CSV_PATH)
        data_handler.load_data()
        data_handler.print_data_summary()
        
        # Tendances
        print_section_header("CALCUL DES TENDANCES", level=1)
        trend_calculator = TrendCalculator(data_handler)
        basic_results = trend_calculator.calculate_basic_trends(ANALYSIS_VARIABLE)
        trend_calculator.print_summary(ANALYSIS_VARIABLE)
        monthly_results = trend_calculator.calculate_monthly_trends(ANALYSIS_VARIABLE)
        
        # Visualisations
        print_section_header("CRÉATION DES VISUALISATIONS", level=1)
        monthly_visualizer = MonthlyVisualizer(data_handler)
        
        monthly_visualizer.create_monthly_statistics_graphs(
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
        
        # Pixels
        print_section_header("ANALYSE DES PIXELS", level=1)
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
            pixel_visualizer.create_true_qa_plots(
                true_qa_results,
                str(output_path / 'true_qa_scores_analysis.png')
            )
        
        if qa_results:
            pixel_visualizer.create_qa_statistics_plots(
                qa_results,
                str(output_path / 'qa_statistics_by_season.png')
            )
        
        # Graphiques quotidiens
        print_section_header("GRAPHIQUES QUOTIDIENS", level=1)
        daily_plots = pixel_visualizer.create_daily_melt_season_plots(
            pixel_analyzer, str(output_path)
        )
        print(f"✅ {len(daily_plots)} graphiques quotidiens créés")
        
        # Exports
        print_section_header("EXPORTS", level=1)
        summary_table = trend_calculator.get_summary_table(ANALYSIS_VARIABLE)
        summary_table.to_csv(str(output_path / f'summary_trends_{ANALYSIS_VARIABLE}.csv'), index=False)
        
        monthly_table = monthly_visualizer.create_monthly_summary_table(ANALYSIS_VARIABLE)
        if not monthly_table.empty:
            monthly_table.to_csv(str(output_path / f'monthly_stats_{ANALYSIS_VARIABLE}.csv'), index=False)
        
        data_handler.export_cleaned_data(str(output_path / f'cleaned_data_{ANALYSIS_VARIABLE}.csv'))
        pixel_analyzer.export_pixel_analysis_results(str(output_path))
        
        print("\n🎉 ANALYSE COMPLÈTE TERMINÉE AVEC SUCCÈS!")
        _list_files(output_path)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

def option2():
    """2️⃣ Analyses de tendances seulement"""
    if not check_config():
        return
    
    print("\n📈 LANCEMENT ANALYSE DES TENDANCES...")
    output_path = PROJECT_DIR / OUTPUT_DIR
    
    try:
        data_handler = AlbedoDataHandler(CSV_PATH)
        data_handler.load_data()
        
        trend_calculator = TrendCalculator(data_handler)
        basic_results = trend_calculator.calculate_basic_trends(ANALYSIS_VARIABLE)
        trend_calculator.print_summary(ANALYSIS_VARIABLE)
        monthly_results = trend_calculator.calculate_monthly_trends(ANALYSIS_VARIABLE)
        
        # Export
        summary_table = trend_calculator.get_summary_table(ANALYSIS_VARIABLE)
        summary_table.to_csv(str(output_path / f'summary_trends_{ANALYSIS_VARIABLE}.csv'), index=False)
        
        all_results = {
            'basic_trends': basic_results,
            'monthly_trends': monthly_results,
            'data_summary': data_handler.get_data_summary()
        }
        print_analysis_summary(all_results)
        
        print("\n✅ ANALYSES DE TENDANCES TERMINÉES!")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")

def option3():
    """3️⃣ Visualisations seulement"""
    if not check_config():
        return
    
    print("\n🎨 LANCEMENT DES VISUALISATIONS...")
    output_path = PROJECT_DIR / OUTPUT_DIR
    
    try:
        data_handler = AlbedoDataHandler(CSV_PATH)
        data_handler.load_data()
        
        trend_calculator = TrendCalculator(data_handler)
        basic_results = trend_calculator.calculate_basic_trends(ANALYSIS_VARIABLE)
        monthly_results = trend_calculator.calculate_monthly_trends(ANALYSIS_VARIABLE)
        
        monthly_visualizer = MonthlyVisualizer(data_handler)
        
        monthly_visualizer.create_monthly_statistics_graphs(
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
        
        print("\n✅ VISUALISATIONS TERMINÉES!")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")

def option4():
    """4️⃣ Analyse pixels/QA seulement"""
    if not check_config():
        return
    
    print("\n🔍 LANCEMENT ANALYSE PIXELS/QA...")
    output_path = PROJECT_DIR / OUTPUT_DIR
    
    try:
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
            pixel_visualizer.create_true_qa_plots(
                true_qa_results,
                str(output_path / 'true_qa_scores_analysis.png')
            )
        
        if qa_results:
            pixel_visualizer.create_qa_statistics_plots(
                qa_results,
                str(output_path / 'qa_statistics_by_season.png')
            )
        
        pixel_analyzer.export_pixel_analysis_results(str(output_path))
        
        print("\n✅ ANALYSE PIXELS/QA TERMINÉE!")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")

def option5():
    """5️⃣ Graphiques quotidiens seulement"""
    if not check_config():
        return
    
    print("\n📅 LANCEMENT GRAPHIQUES QUOTIDIENS...")
    output_path = PROJECT_DIR / OUTPUT_DIR
    
    try:
        data_handler = AlbedoDataHandler(CSV_PATH)
        data_handler.load_data()
        
        pixel_analyzer = PixelCountAnalyzer(data_handler, qa_csv_path=QA_CSV_PATH)
        pixel_visualizer = PixelVisualizer(data_handler)
        
        daily_plots = pixel_visualizer.create_daily_melt_season_plots(
            pixel_analyzer, str(output_path)
        )
        
        print(f"\n✅ {len(daily_plots)} GRAPHIQUES QUOTIDIENS CRÉÉS!")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")

def _list_files(output_path):
    """Liste les fichiers générés"""
    files = list(output_path.glob('*'))
    if files:
        print(f"\n📁 {len(files)} fichiers générés:")
        for file in sorted(files)[:10]:  # Afficher les 10 premiers
            if file.is_file():
                size_kb = file.stat().st_size / 1024
                print(f"  ✅ {file.name} ({size_kb:.1f} KB)")
        if len(files) > 10:
            print(f"  ... et {len(files)-10} autres fichiers")

# Afficher le menu au démarrage
print("\n" + "="*70)
print("🚀 SASKATCHEWAN GLACIER ALBEDO ANALYSIS")
print("   VS CODE INTERACTIVE WINDOW")
print("="*70)

print_config_summary()

print("\n💡 PRÊT À UTILISER!")
menu()

print("\n🎯 Tapez une commande ci-dessus pour commencer!")
print("   Exemple: option1() puis Entrée")