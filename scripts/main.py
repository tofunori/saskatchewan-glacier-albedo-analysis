#!/usr/bin/env python3
"""
SCRIPT PRINCIPAL - Analyse des tendances d'albédo du glacier Saskatchewan
========================================================================

Script interactif avec menu pour choisir les analyses à effectuer.

POUR UTILISER :
1. Modifiez le chemin CSV_PATH dans config.py si nécessaire
2. Exécutez : python main.py  
3. Choisissez les analyses souhaitées dans le menu
4. Consultez les résultats dans le dossier results/
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Ajouter le répertoire du projet au path pour trouver les modules
script_dir = Path(__file__).parent.absolute()
project_dir = script_dir.parent  # Remonte d'un niveau depuis scripts/

# Ajouter le répertoire src au path pour les imports
src_dir = project_dir / 'src'
sys.path.insert(0, str(src_dir))

print(f"📂 Répertoire de travail actuel: {Path.cwd()}")
print(f"📁 Répertoire du projet: {project_dir}")
print(f"📁 Répertoire src: {src_dir}")

# Variable globale pour le répertoire du projet
PROJECT_DIR = project_dir

# Variables globales pour stocker l'état
data_handler = None
trend_calculator = None
basic_results = None
monthly_results = None
analyses_completed = {
    'data_loaded': False,
    'trends_calculated': False,
    'visualizations_done': False,
    'pixel_analysis_done': False,
    'daily_plots_done': False
}

# Imports des modules du package saskatchewan_albedo
try:
    from saskatchewan_albedo.config import CSV_PATH, QA_CSV_PATH, OUTPUT_DIR, ANALYSIS_VARIABLE, print_config_summary
    from saskatchewan_albedo.data.handler import AlbedoDataHandler
    from saskatchewan_albedo.analysis.trends import TrendCalculator
    from saskatchewan_albedo.analysis.pixel_analysis import PixelCountAnalyzer
    from saskatchewan_albedo.visualization.monthly import MonthlyVisualizer
    from saskatchewan_albedo.visualization.pixel_plots import PixelVisualizer
    from saskatchewan_albedo.visualization.charts import ChartGenerator
    from saskatchewan_albedo.utils.helpers import print_section_header, ensure_directory_exists, print_analysis_summary
    print("✅ Tous les modules importés avec succès")
except ImportError as e:
    print(f"❌ Erreur d'import des modules: {e}")
    print(f"📁 Vérifiez que tous les fichiers sont présents dans: {src_dir}")
    sys.exit(1)

def display_menu():
    """
    Affiche le menu principal
    """
    print("\n" + "="*60)
    print("🚀 SASKATCHEWAN GLACIER ALBEDO ANALYSIS MENU")
    print("="*60)
    
    # Afficher l'état des analyses
    print("\n📊 État des analyses:")
    print(f"   • Données chargées: {'✅' if analyses_completed['data_loaded'] else '❌'}")
    print(f"   • Tendances calculées: {'✅' if analyses_completed['trends_calculated'] else '❌'}")
    print(f"   • Visualisations standards: {'✅' if analyses_completed['visualizations_done'] else '❌'}")
    print(f"   • Analyse pixels/QA: {'✅' if analyses_completed['pixel_analysis_done'] else '❌'}")
    print(f"   • Graphiques quotidiens: {'✅' if analyses_completed['daily_plots_done'] else '❌'}")
    
    print("\n📋 Options disponibles:")
    print("   1. 🔄 Run Complete Analysis (Toutes les analyses)")
    print("   2. 📊 Trend Analysis & Statistics")
    print("   3. 🎨 Standard Visualizations") 
    print("   4. 🔍 Pixel & QA Analysis")
    print("   5. 📅 Daily Time Series Plots")
    print("   6. ❌ Exit")
    print("\n" + "-"*60)

def get_menu_choice():
    """
    Obtient et valide le choix de l'utilisateur
    """
    while True:
        choice = input("\n➤ Choisissez une option (1-6): ").strip()
        
        if choice in ['1', '2', '3', '4', '5', '6']:
            return choice
        elif choice.lower() in ['q', 'exit', 'quit']:
            return '6'
        else:
            print("❌ Choix invalide. Veuillez entrer un nombre entre 1 et 6.")

def check_configuration():
    """
    Vérifie la configuration initiale
    """
    print("\n⚙️  VÉRIFICATION DE LA CONFIGURATION")
    print("="*50)
    
    # Vérifier le fichier CSV principal
    if not os.path.exists(CSV_PATH):
        print(f"❌ ERREUR : Fichier CSV non trouvé !")
        print(f"   Chemin configuré : {CSV_PATH}")
        print(f"\n💡 SOLUTION :")
        print(f"   Modifiez la variable CSV_PATH dans config.py")
        return False
    
    print(f"✅ Fichier CSV principal trouvé : {CSV_PATH}")
    
    # Vérifier le fichier QA CSV (optionnel)
    if QA_CSV_PATH and os.path.exists(QA_CSV_PATH):
        print(f"✅ Fichier QA CSV trouvé : {QA_CSV_PATH}")
    else:
        print(f"⚠️  Fichier QA CSV non trouvé (analyse QA 0-3 non disponible)")
    
    # Créer le répertoire de sortie
    output_path = PROJECT_DIR / OUTPUT_DIR
    ensure_directory_exists(str(output_path))
    print(f"📁 Répertoire de sortie : {output_path}/")
    
    return True

def ensure_data_loaded():
    """
    S'assure que les données sont chargées
    """
    global data_handler, analyses_completed
    
    if not analyses_completed['data_loaded']:
        print("\n📊 Chargement des données nécessaire...")
        data_handler = AlbedoDataHandler(CSV_PATH)
        data_handler.load_data()
        data_handler.print_data_summary()
        analyses_completed['data_loaded'] = True
        print("✅ Données chargées avec succès")
    
    return data_handler

def ensure_trends_calculated():
    """
    S'assure que les tendances sont calculées
    """
    global trend_calculator, basic_results, monthly_results, analyses_completed
    
    # D'abord s'assurer que les données sont chargées
    ensure_data_loaded()
    
    if not analyses_completed['trends_calculated']:
        print("\n📊 Calcul des tendances nécessaire...")
        trend_calculator = TrendCalculator(data_handler)
        basic_results = trend_calculator.calculate_basic_trends(ANALYSIS_VARIABLE)
        monthly_results = trend_calculator.calculate_monthly_trends(ANALYSIS_VARIABLE)
        analyses_completed['trends_calculated'] = True
        print("✅ Tendances calculées avec succès")
    
    return trend_calculator, basic_results, monthly_results

def run_complete_analysis():
    """
    Exécute l'analyse complète (comportement original)
    """
    print("\n🔄 EXÉCUTION DE L'ANALYSE COMPLÈTE")
    print("="*60)
    
    # Utiliser la fonction main originale modifiée
    run_original_main_analysis()

def run_trend_analysis():
    """
    Exécute uniquement les analyses de tendances et statistiques
    """
    print_section_header("ANALYSES DE TENDANCES ET STATISTIQUES", level=1)
    
    output_path = PROJECT_DIR / OUTPUT_DIR
    
    try:
        # S'assurer que les données sont chargées
        ensure_data_loaded()
        
        # Calculs statistiques de base
        print_section_header("Analyses de tendances de base", level=2)
        trend_calculator = TrendCalculator(data_handler)
        basic_results = trend_calculator.calculate_basic_trends(ANALYSIS_VARIABLE)
        trend_calculator.print_summary(ANALYSIS_VARIABLE)
        
        # Analyses mensuelles
        print_section_header("Analyses saisonnières et mensuelles", level=2)
        monthly_results = trend_calculator.calculate_monthly_trends(ANALYSIS_VARIABLE)
        
        # Export des résultats
        print_section_header("Export des résultats statistiques", level=2)
        
        # Export du tableau de résumé
        summary_table = trend_calculator.get_summary_table(ANALYSIS_VARIABLE)
        summary_csv_path = str(output_path / f'summary_trends_{ANALYSIS_VARIABLE}.csv')
        summary_table.to_csv(summary_csv_path, index=False)
        print(f"📊 Tableau de résumé exporté : {summary_csv_path}")
        
        # Résumé final
        all_results = {
            'basic_trends': basic_results,
            'monthly_trends': monthly_results,
            'data_summary': data_handler.get_data_summary()
        }
        print_analysis_summary(all_results)
        
        analyses_completed['trends_calculated'] = True
        print("\n✅ Analyses de tendances terminées avec succès")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'analyse des tendances: {e}")
        import traceback
        traceback.print_exc()

def run_standard_visualizations():
    """
    Crée les visualisations standards
    """
    print_section_header("VISUALISATIONS STANDARDS", level=1)
    
    output_path = PROJECT_DIR / OUTPUT_DIR
    
    try:
        # S'assurer que les données et tendances sont calculées
        trend_calculator, basic_results, monthly_results = ensure_trends_calculated()
        
        # Créer le visualiseur mensuel
        monthly_visualizer = MonthlyVisualizer(data_handler)
        
        # Graphiques mensuels
        print_section_header("Création des graphiques mensuels", level=2)
        monthly_graph_path = monthly_visualizer.create_monthly_statistics_graphs(
            ANALYSIS_VARIABLE, 
            str(output_path / f'monthly_statistics_{ANALYSIS_VARIABLE}.png')
        )
        
        if monthly_graph_path:
            print(f"🎨 Graphiques mensuels créés : {monthly_graph_path}")
        
        # Comparaison des tendances mensuelles
        if monthly_results:
            comparison_path = monthly_visualizer.create_seasonal_trends_comparison(
                monthly_results, ANALYSIS_VARIABLE,
                str(output_path / f'monthly_comparison_{ANALYSIS_VARIABLE}.png')
            )
            monthly_visualizer.print_monthly_summary(ANALYSIS_VARIABLE)
        
        # Autres visualisations
        print_section_header("Visualisations additionnelles", level=2)
        
        try:
            chart_generator = ChartGenerator(data_handler)
            
            # Graphique d'aperçu des tendances
            overview_path = chart_generator.create_trend_overview_graph(
                basic_results, ANALYSIS_VARIABLE,
                str(output_path / f'trend_overview_{ANALYSIS_VARIABLE}.png')
            )
            
            # Patterns saisonniers
            patterns_path = chart_generator.create_seasonal_patterns_graph(
                ANALYSIS_VARIABLE,
                str(output_path / f'seasonal_patterns_{ANALYSIS_VARIABLE}.png')
            )
            
            print("✅ Visualisations additionnelles créées")
            
        except Exception as e:
            print(f"⚠️  Erreur lors des visualisations additionnelles: {e}")
        
        analyses_completed['visualizations_done'] = True
        print("\n✅ Visualisations standards terminées avec succès")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des visualisations: {e}")
        import traceback
        traceback.print_exc()

def run_pixel_qa_analysis():
    """
    Exécute l'analyse des pixels et QA
    """
    print_section_header("ANALYSE DES PIXELS ET QA", level=1)
    
    output_path = PROJECT_DIR / OUTPUT_DIR
    
    try:
        # S'assurer que les données sont chargées
        ensure_data_loaded()
        
        # Créer l'analyseur de pixels
        pixel_analyzer = PixelCountAnalyzer(data_handler, qa_csv_path=QA_CSV_PATH)
        
        print_section_header("Analyse des comptages de pixels", level=2)
        monthly_pixel_results = pixel_analyzer.analyze_monthly_pixel_counts()
        
        print_section_header("Analyse des statistiques QA", level=2)
        # Vraies statistiques QA (0-3) si disponibles
        true_qa_results = {}
        if QA_CSV_PATH and os.path.exists(QA_CSV_PATH):
            true_qa_results = pixel_analyzer.analyze_true_qa_statistics()
        
        # Statistiques QA standard
        qa_results = pixel_analyzer.analyze_seasonal_qa_statistics()
        
        # Tendances des pixels totaux
        total_pixel_results = pixel_analyzer.analyze_total_pixel_trends()
        
        # Créer les visualisations
        print_section_header("Création des visualisations pixels/QA", level=2)
        pixel_visualizer = PixelVisualizer(data_handler)
        
        # Graphiques de comptages de pixels
        if monthly_pixel_results:
            pixel_visualizer.create_monthly_pixel_count_plots(
                monthly_pixel_results,
                str(output_path / 'pixel_counts_by_month_fraction.png')
            )
        
        # Graphiques QA vrais (0-3)
        if true_qa_results:
            pixel_visualizer.create_true_qa_plots(
                true_qa_results,
                str(output_path / 'true_qa_scores_analysis.png')
            )
        
        # Graphiques QA standard
        if qa_results:
            pixel_visualizer.create_qa_statistics_plots(
                qa_results,
                str(output_path / 'qa_statistics_by_season.png')
            )
        
        # Heatmap et série temporelle
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
        
        # Export des résultats
        pixel_exports = pixel_analyzer.export_pixel_analysis_results(str(output_path))
        
        analyses_completed['pixel_analysis_done'] = True
        print("\n✅ Analyse pixels/QA terminée avec succès")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'analyse pixels/QA: {e}")
        import traceback
        traceback.print_exc()

def run_daily_timeseries():
    """
    Crée les graphiques de séries temporelles quotidiennes
    """
    print_section_header("GRAPHIQUES DE SÉRIES TEMPORELLES QUOTIDIENNES", level=1)
    
    output_path = PROJECT_DIR / OUTPUT_DIR
    
    try:
        # S'assurer que les données sont chargées
        ensure_data_loaded()
        
        # Créer l'analyseur et le visualiseur
        pixel_analyzer = PixelCountAnalyzer(data_handler, qa_csv_path=QA_CSV_PATH)
        pixel_visualizer = PixelVisualizer(data_handler)
        
        # Graphiques quotidiens pixels/QA par année
        print_section_header("Graphiques quotidiens par saison de fonte", level=2)
        daily_plots = pixel_visualizer.create_daily_melt_season_plots(
            pixel_analyzer, 
            str(output_path)
        )
        print(f"✅ {len(daily_plots)} graphiques quotidiens créés")
        
        # Graphiques quotidiens d'albédo par année
        print_section_header("Graphiques quotidiens d'albédo par année", level=2)
        albedo_plots = create_daily_albedo_plots(data_handler, str(output_path))
        print(f"✅ {len(albedo_plots)} graphiques d'albédo quotidiens créés")
        
        # Graphique de comparaison multi-années
        print_section_header("Graphique de comparaison multi-années", level=2)
        comparison_plot = create_multiyear_daily_comparison(data_handler, str(output_path))
        if comparison_plot:
            print(f"✅ Graphique de comparaison créé: {comparison_plot}")
        
        analyses_completed['daily_plots_done'] = True
        print("\n✅ Graphiques quotidiens terminés avec succès")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des graphiques quotidiens: {e}")
        import traceback
        traceback.print_exc()

def create_daily_albedo_plots(data_handler, output_dir):
    """
    Crée des graphiques d'albédo quotidiens pour chaque année
    """
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from saskatchewan_albedo.config import FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS, MONTH_NAMES, ANALYSIS_VARIABLE
    
    saved_plots = []
    data = data_handler.data
    years = sorted(data['year'].unique())
    
    for year in years:
        print(f"\n🎯 Création du graphique d'albédo pour {year}")
        
        # Filtrer les données pour cette année
        year_data = data[
            (data['year'] == year) & 
            (data['month'].isin([6, 7, 8, 9]))
        ].copy()
        
        if len(year_data) == 0:
            print(f"⚠️ Pas de données pour {year}")
            continue
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.suptitle(f'Albédo Quotidien - Saison de Fonte {year}', 
                     fontsize=16, fontweight='bold')
        
        # Trier par date
        year_data = year_data.sort_values('date')
        
        # Tracer l'albédo pour chaque fraction
        for fraction in FRACTION_CLASSES:
            col_mean = f"{fraction}_{ANALYSIS_VARIABLE}"
            if col_mean in year_data.columns:
                albedo_data = year_data[col_mean].dropna()
                if len(albedo_data) > 0:
                    ax.plot(year_data['date'], year_data[col_mean], 
                           marker='o', markersize=3, linewidth=1.5, alpha=0.8,
                           label=CLASS_LABELS[fraction],
                           color=FRACTION_COLORS.get(fraction, 'gray'))
        
        # Configuration du graphique
        ax.set_xlabel('Date')
        ax.set_ylabel(f'Albédo ({ANALYSIS_VARIABLE.capitalize()})')
        ax.set_ylim([0, 1])
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Ajouter des lignes verticales pour séparer les mois
        for month in [7, 8, 9]:
            month_start = year_data[year_data['month'] == month]['date'].min()
            if not pd.isna(month_start):
                ax.axvline(x=month_start, color='gray', linestyle='--', alpha=0.5)
        
        # Statistiques
        stats_text = f"Période: {year_data['date'].min().strftime('%Y-%m-%d')} à {year_data['date'].max().strftime('%Y-%m-%d')}\n"
        stats_text += f"Observations: {len(year_data)} jours"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                verticalalignment='top', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        # Sauvegarder
        save_path = os.path.join(output_dir, f'daily_albedo_melt_season_{year}.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        saved_plots.append(save_path)
    
    return saved_plots

def create_multiyear_daily_comparison(data_handler, output_dir):
    """
    Crée un graphique de comparaison multi-années
    """
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from saskatchewan_albedo.config import FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS, ANALYSIS_VARIABLE
    
    data = data_handler.data
    
    # Filtrer pour la saison de fonte
    melt_data = data[data['month'].isin([6, 7, 8, 9])].copy()
    
    if len(melt_data) == 0:
        print("⚠️ Pas de données pour créer le graphique multi-années")
        return None
    
    # Créer une colonne jour de l'année pour aligner les données
    melt_data['day_of_year'] = melt_data['date'].dt.dayofyear
    
    # Créer le graphique
    fig, axes = plt.subplots(len(FRACTION_CLASSES), 1, figsize=(14, 12), sharex=True)
    fig.suptitle('Comparaison Multi-Années des Albédos Quotidiens', 
                 fontsize=16, fontweight='bold')
    
    years = sorted(melt_data['year'].unique())
    colors = plt.cm.viridis(np.linspace(0, 1, len(years)))
    
    for idx, fraction in enumerate(FRACTION_CLASSES):
        ax = axes[idx] if len(FRACTION_CLASSES) > 1 else axes
        col_mean = f"{fraction}_{ANALYSIS_VARIABLE}"
        
        if col_mean in melt_data.columns:
            for year_idx, year in enumerate(years):
                year_data = melt_data[melt_data['year'] == year]
                if len(year_data) > 0:
                    ax.plot(year_data['day_of_year'], year_data[col_mean], 
                           alpha=0.7, linewidth=1, color=colors[year_idx],
                           label=str(year) if idx == 0 else "")
            
            ax.set_ylabel(f'{CLASS_LABELS[fraction]}')
            ax.set_ylim([0, 1])
            ax.grid(True, alpha=0.3)
            
            # Ajouter la moyenne sur toutes les années
            mean_by_doy = melt_data.groupby('day_of_year')[col_mean].mean()
            ax.plot(mean_by_doy.index, mean_by_doy.values, 
                   'k-', linewidth=2, label='Moyenne' if idx == 0 else "")
    
    # Configuration finale
    axes[-1].set_xlabel('Jour de l\'année')
    axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left', ncol=2)
    
    plt.tight_layout()
    
    # Sauvegarder
    save_path = os.path.join(output_dir, 'daily_albedo_all_years_comparison.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
    
    return save_path

def run_original_main_analysis():
    """
    Exécute l'analyse complète originale
    """
    output_path = PROJECT_DIR / OUTPUT_DIR
    
    try:
        # ÉTAPE 1: Chargement et préparation des données
        print_section_header("ÉTAPE 1: Chargement des données", level=1)
        
        global data_handler
        data_handler = AlbedoDataHandler(CSV_PATH)
        data_handler.load_data()
        data_handler.print_data_summary()
        analyses_completed['data_loaded'] = True
        
        # ÉTAPE 2: Calculs statistiques de base  
        print_section_header("ÉTAPE 2: Analyses de tendances de base", level=1)
        
        global trend_calculator, basic_results
        trend_calculator = TrendCalculator(data_handler)
        basic_results = trend_calculator.calculate_basic_trends(ANALYSIS_VARIABLE)
        trend_calculator.print_summary(ANALYSIS_VARIABLE)
        
        # ÉTAPE 3: Analyses mensuelles
        print_section_header("ÉTAPE 3: Analyses saisonnières et mensuelles", level=1)
        
        global monthly_results
        monthly_results = trend_calculator.calculate_monthly_trends(ANALYSIS_VARIABLE)
        analyses_completed['trends_calculated'] = True
        
        # ÉTAPE 4: VOS GRAPHIQUES MENSUELS DEMANDÉS
        print_section_header("ÉTAPE 4: Création des graphiques mensuels", level=1)
        
        monthly_visualizer = MonthlyVisualizer(data_handler)
        
        monthly_graph_path = monthly_visualizer.create_monthly_statistics_graphs(
            ANALYSIS_VARIABLE, 
            str(output_path / f'monthly_statistics_{ANALYSIS_VARIABLE}.png')
        )
        
        if monthly_graph_path:
            print(f"🎨 Vos graphiques mensuels créés : {monthly_graph_path}")
        
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
            analyses_completed['visualizations_done'] = True
            
        except ImportError:
            print("⚠️  Module de visualisations additionnelles non disponible")
        
        # ÉTAPE 6: Analyse des comptages de pixels
        print_section_header("ÉTAPE 6: Analyse des comptages de pixels", level=1)
        
        try:
            pixel_analyzer = PixelCountAnalyzer(data_handler, qa_csv_path=QA_CSV_PATH)
            
            monthly_pixel_results = pixel_analyzer.analyze_monthly_pixel_counts()
            true_qa_results = pixel_analyzer.analyze_true_qa_statistics()
            qa_results = pixel_analyzer.analyze_seasonal_qa_statistics()
            total_pixel_results = pixel_analyzer.analyze_total_pixel_trends()
            
            print("✅ Analyses de pixels terminées")
            
        except Exception as e:
            print(f"⚠️  Erreur lors de l'analyse des pixels: {e}")
            monthly_pixel_results = {}
            true_qa_results = {}
            qa_results = {}
            total_pixel_results = {}
        
        # ÉTAPE 7: Visualisations des pixels et QA
        print_section_header("ÉTAPE 7: Visualisations des pixels et QA", level=1)
        
        try:
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
            analyses_completed['pixel_analysis_done'] = True
            
        except Exception as e:
            print(f"⚠️  Erreur lors des visualisations de pixels: {e}")
        
        # ÉTAPE 8: Graphiques quotidiens par année
        print_section_header("ÉTAPE 8: Graphiques quotidiens par saison de fonte", level=1)
        
        try:
            if 'pixel_analyzer' in locals() and 'pixel_visualizer' in locals():
                daily_plots = pixel_visualizer.create_daily_melt_season_plots(
                    pixel_analyzer, 
                    str(output_path)
                )
                print(f"✅ {len(daily_plots)} graphiques quotidiens annuels créés")
                analyses_completed['daily_plots_done'] = True
            
        except Exception as e:
            print(f"⚠️  Erreur lors des graphiques quotidiens: {e}")
        
        # ÉTAPE 9: Exports des résultats
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
            print(f"⚠️  Erreur lors des exports: {e}")
        
        # RÉSUMÉ FINAL
        all_results = {
            'basic_trends': basic_results,
            'monthly_trends': monthly_results if 'monthly_results' in locals() else {},
            'data_summary': data_handler.get_data_summary()
        }
        
        print_analysis_summary(all_results)
        
        # Lister les fichiers générés
        print_section_header("FICHIERS GÉNÉRÉS", level=1)
        list_generated_files(output_path)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DE L'ANALYSE :")
        print(f"   {e}")
        print(f"\n🔍 Détails de l'erreur :")
        import traceback
        traceback.print_exc()
        return False

def list_generated_files(output_path):
    """
    Liste tous les fichiers générés
    """
    generated_files = []
    
    # Parcourir tous les fichiers dans le répertoire de sortie
    for file in output_path.glob('*'):
        if file.is_file():
            size_kb = file.stat().st_size / 1024
            generated_files.append((file.name, size_kb))
    
    # Trier par nom
    generated_files.sort(key=lambda x: x[0])
    
    print(f"\n📁 {len(generated_files)} fichiers dans {output_path}/:")
    for filename, size_kb in generated_files:
        print(f"  ✅ {filename} ({size_kb:.1f} KB)")

def ask_continue():
    """
    Demande à l'utilisateur s'il veut continuer
    """
    while True:
        response = input("\n➤ Voulez-vous effectuer une autre analyse? (o/n): ").strip().lower()
        if response in ['o', 'oui', 'y', 'yes']:
            return True
        elif response in ['n', 'non', 'no']:
            return False
        else:
            print("❌ Réponse invalide. Veuillez répondre par 'o' ou 'n'.")

def main():
    """
    Fonction principale avec menu interactif
    """
    # En-tête de bienvenue
    print("\n" + "="*70)
    print("🚀 SASKATCHEWAN GLACIER ALBEDO TREND ANALYSIS")
    print("="*70)
    print("📅 Session lancée le:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Vérifier la configuration
    print_config_summary()
    
    if not check_configuration():
        print("\n❌ Configuration invalide. Veuillez corriger les erreurs ci-dessus.")
        return
    
    # Boucle du menu principal
    while True:
        display_menu()
        choice = get_menu_choice()
        
        if choice == '1':
            run_complete_analysis()
        elif choice == '2':
            run_trend_analysis()
        elif choice == '3':
            run_standard_visualizations()
        elif choice == '4':
            run_pixel_qa_analysis()
        elif choice == '5':
            run_daily_timeseries()
        elif choice == '6':
            print("\n👋 Au revoir! Merci d'avoir utilisé l'outil d'analyse.")
            break
        
        # Demander si continuer
        if choice != '6' and not ask_continue():
            print("\n👋 Au revoir! Merci d'avoir utilisé l'outil d'analyse.")
            break
    
    print("="*70)

if __name__ == "__main__":
    main()