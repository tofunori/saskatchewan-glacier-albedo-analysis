#!/usr/bin/env python3
"""
SCRIPT PRINCIPAL INTERACTIF - Pour VS Code Interactive Window
============================================================

Ce script fonctionne exactement comme l'ancien main_backup.py mais avec
des options de menu simples pour VS Code.

POUR UTILISER DANS VS CODE:
1. Ouvrez ce fichier dans VS Code
2. Exécutez le script avec Ctrl+F5 ou clic droit "Run Python File in Terminal"
3. Choisissez une option dans le menu qui apparaît
4. Consultez les résultats dans le dossier results/

MENU:
1 = Analyse complète (tout)
2 = Tendances seulement  
3 = Visualisations seulement
4 = Pixels/QA seulement
5 = Graphiques quotidiens seulement
6 = Quitter
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set matplotlib to non-interactive backend to prevent blocking
import matplotlib
matplotlib.use('Agg')

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

# Imports des modules du package saskatchewan_albedo
try:
    from saskatchewan_albedo.config import (CSV_PATH, QA_CSV_PATH, OUTPUT_DIR, ANALYSIS_VARIABLE, 
                                           print_config_summary, FRACTION_CLASSES, CLASS_LABELS, FRACTION_COLORS)
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

def show_menu():
    """Affiche le menu d'options"""
    print("\n" + "="*60)
    print("🚀 MENU D'ANALYSE - CHOISISSEZ UNE OPTION")
    print("="*60)
    print()
    print("1️⃣  Analyse complète (toutes les étapes)")
    print("2️⃣  Analyses de tendances et statistiques")
    print("3️⃣  Visualisations standards") 
    print("4️⃣  Analyse des pixels et QA")
    print("5️⃣  Graphiques de séries temporelles quotidiennes")
    print("6️⃣  Quitter")
    print()
    print("-" * 60)

def get_choice():
    """Obtient le choix de l'utilisateur de manière simple"""
    print("\n" + "="*60)
    print("SÉLECTION DE L'ANALYSE")
    print("="*60)
    print()
    print("Tapez le numéro de votre choix puis appuyez sur Entrée:")
    print("1 = Analyse complète")
    print("2 = Tendances")
    print("3 = Visualisations")
    print("4 = Pixels/QA")
    print("5 = Graphiques quotidiens")
    print("6 = Quitter")
    print()
    
    while True:
        try:
            choice = input("➤ Votre choix (1-6): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6']:
                return int(choice)
            else:
                print(f"❌ '{choice}' n'est pas valide. Tapez un chiffre de 1 à 6.")
        except KeyboardInterrupt:
            print("\n\n👋 Interruption. Au revoir!")
            return 6
        except:
            print("❌ Erreur de saisie. Tapez un chiffre de 1 à 6.")

def check_config():
    """Vérifie la configuration"""
    print("\n⚙️  VÉRIFICATION DE LA CONFIGURATION")
    print("="*50)
    
    if not os.path.exists(CSV_PATH):
        print(f"❌ ERREUR : Fichier CSV non trouvé !")
        print(f"   Chemin configuré : {CSV_PATH}")
        print(f"\n💡 SOLUTION :")
        print(f"   Modifiez la variable CSV_PATH dans config.py")
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
            
            # Graphiques quotidiens d'albédo
            albedo_plots = create_daily_albedo_plots(data_handler, str(output_path))
            print(f"✅ {len(albedo_plots)} graphiques quotidiens d'albédo créés")
            
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
        
        print("\n✅ ANALYSE PIXELS/QA TERMINÉE !")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        return False

def create_daily_albedo_plots(data_handler, output_dir):
    """
    Crée des graphiques d'albédo quotidiens pour chaque année
    
    Args:
        data_handler: AlbedoDataHandler instance with loaded data
        output_dir (str): Directory to save the plots
        
    Returns:
        list: Paths to saved plots for each year
    """
    import matplotlib.pyplot as plt
    import pandas as pd
    
    print_section_header("Création des graphiques d'albédo quotidiens", level=2)
    
    saved_plots = []
    data = data_handler.data
    years = sorted(data['year'].unique())
    
    print(f"📅 Années disponibles: {years}")
    
    for year in years:
        print(f"\n🎯 Création du graphique d'albédo pour {year}")
        
        # Filtrer les données pour cette année (saison de fonte)
        year_data = data[
            (data['year'] == year) & 
            (data['month'].isin([6, 7, 8, 9]))
        ].copy()
        
        if len(year_data) == 0:
            print(f"⚠️ Pas de données pour {year}")
            continue
        
        # Trier par date
        year_data = year_data.sort_values('date')
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.suptitle(f'Albédo Quotidien - Saison de Fonte {year}', 
                     fontsize=16, fontweight='bold')
        
        # Tracer l'albédo pour chaque fraction
        for fraction in FRACTION_CLASSES:
            col_mean = f"{fraction}_{ANALYSIS_VARIABLE}"
            if col_mean in year_data.columns:
                albedo_data = year_data[col_mean].dropna()
                if len(albedo_data) > 0:
                    # Plot only non-null values
                    valid_data = year_data[year_data[col_mean].notna()]
                    ax.plot(valid_data['date'], valid_data[col_mean], 
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
        plt.close()  # Close figure to free memory
        
        print(f"✅ Graphique d'albédo {year} sauvegardé: {save_path}")
        saved_plots.append(save_path)
    
    return saved_plots

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
        pixel_visualizer = PixelVisualizer(data_handler)
        
        daily_plots = pixel_visualizer.create_daily_melt_season_plots(
            pixel_analyzer, 
            str(output_path)
        )
        print(f"✅ {len(daily_plots)} graphiques quotidiens pixels/QA créés")
        
        # Graphiques quotidiens d'albédo
        albedo_plots = create_daily_albedo_plots(data_handler, str(output_path))
        print(f"✅ {len(albedo_plots)} graphiques quotidiens d'albédo créés")
        
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

def main():
    """Fonction principale simple pour VS Code"""
    print("\n" + "="*70)
    print("🚀 SASKATCHEWAN GLACIER ALBEDO TREND ANALYSIS")
    print("="*70)
    print("📅 Session lancée le:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    print_config_summary()
    
    if not check_config():
        print("\n❌ Configuration invalide.")
        return
    
    while True:
        show_menu()
        choice = get_choice()
        
        if choice == 1:
            run_complete_analysis()
        elif choice == 2:
            run_trends_only()
        elif choice == 3:
            run_visualizations_only()
        elif choice == 4:
            run_pixels_only()
        elif choice == 5:
            run_daily_only()
        elif choice == 6:
            print("\n👋 Au revoir!")
            break
        
        print("\n" + "="*60)
        try:
            cont = input("➤ Continuer avec une autre analyse? (o/n): ").strip().lower()
            if cont not in ['o', 'oui', 'y', 'yes']:
                print("\n👋 Au revoir!")
                break
        except:
            break

if __name__ == "__main__":
    main()