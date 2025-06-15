#!/usr/bin/env python3
"""
Exemple d'utilisation du package Saskatchewan Albedo Trend Analysis
==================================================================

Ce script montre comment utiliser la nouvelle structure modulaire
pour analyser les tendances d'albédo du glacier Saskatchewan.
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire du package au path
sys.path.insert(0, str(Path(__file__).parent))

def example_complete_analysis():
    """
    Exemple d'analyse complète avec tous les modules
    """
    print("🔬 EXEMPLE: Analyse complète avec structure modulaire")
    print("="*60)
    
    # Chemin vers vos données CSV (à adapter)
    csv_path = "daily_albedo_by_fraction_optimized.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Fichier non trouvé: {csv_path}")
        print("Modifiez le chemin dans ce script pour pointer vers votre fichier CSV")
        return
    
    # Utilisation de la fonction principale
    from trend_analysis import run_complete_analysis
    
    results = run_complete_analysis(
        csv_path=csv_path,
        output_dir='analysis_results_modular',
        variable='mean'
    )
    
    if results:
        print("✅ Analyse complète terminée avec succès!")
        print(f"📁 Résultats dans: analysis_results_modular/")
    else:
        print("❌ Échec de l'analyse")

def example_step_by_step():
    """
    Exemple d'utilisation étape par étape avec les modules individuels
    """
    print("\n🧩 EXEMPLE: Utilisation modulaire étape par étape")
    print("="*50)
    
    csv_path = "daily_albedo_by_fraction_optimized.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Fichier non trouvé: {csv_path}")
        return
    
    try:
        # Import des modules nécessaires
        from trend_analysis import (
            SaskatchewanDataLoader,
            BasicTrendAnalyzer, 
            SeasonalAnalyzer,
            AlbedoVisualizer,
            ResultsExporter
        )
        
        # 1. Chargement des données
        print("📊 Étape 1: Chargement des données")
        data_loader = SaskatchewanDataLoader(csv_path)
        data_loader.load_data()
        data_loader.print_data_summary()
        
        # 2. Analyses de base
        print("\n📈 Étape 2: Analyses de tendances de base")
        basic_analyzer = BasicTrendAnalyzer(data_loader)
        basic_results = basic_analyzer.calculate_trends('mean')
        basic_analyzer.print_summary('mean')
        
        # 3. Analyses saisonnières + graphiques mensuels demandés
        print("\n📅 Étape 3: Analyses saisonnières et graphiques mensuels")
        seasonal_analyzer = SeasonalAnalyzer(data_loader)
        monthly_results = seasonal_analyzer.analyze_monthly_trends('mean')
        
        # Créer les graphiques de statistiques mensuelles demandés
        monthly_graph = seasonal_analyzer.create_monthly_statistics_graphs('mean')
        print(f"✅ Graphiques mensuels créés: {monthly_graph}")
        
        # 4. Visualisations principales
        print("\n🎨 Étape 4: Création des visualisations")
        visualizer = AlbedoVisualizer(data_loader)
        
        # Aperçu des tendances
        overview_graph = visualizer.create_trend_overview_graph(basic_results, 'mean')
        print(f"✅ Aperçu des tendances: {overview_graph}")
        
        # Patterns saisonniers
        seasonal_graph = visualizer.create_seasonal_patterns_graph('mean')
        print(f"✅ Patterns saisonniers: {seasonal_graph}")
        
        # 5. Export des résultats
        print("\n💾 Étape 5: Export des résultats")
        exporter = ResultsExporter(data_loader)
        
        # Rapport texte complet
        all_results = {
            'metadata': {
                'csv_path': csv_path,
                'data_summary': data_loader.get_data_summary()
            },
            'basic_trends': basic_results,
            'monthly_trends': monthly_results
        }
        
        text_report = exporter.export_text_report(all_results, 'mean')
        print(f"✅ Rapport texte: {text_report}")
        
        # CSV de résumé
        summary_csv = exporter.export_summary_csv(basic_results, 'mean')
        print(f"✅ Résumé CSV: {summary_csv}")
        
        print("\n🎉 Analyse modulaire terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse modulaire: {e}")
        import traceback
        traceback.print_exc()

def example_quick_analysis():
    """
    Exemple d'analyse rapide
    """
    print("\n⚡ EXEMPLE: Analyse rapide")
    print("="*30)
    
    csv_path = "daily_albedo_by_fraction_optimized.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Fichier non trouvé: {csv_path}")
        return
    
    from trend_analysis import run_quick_analysis
    
    results = run_quick_analysis(csv_path, variable='mean')
    
    if results:
        print("✅ Analyse rapide terminée!")
        print(f"📊 {len(results['basic_trends'])} fractions analysées")

def example_single_fraction():
    """
    Exemple d'analyse d'une seule fraction
    """
    print("\n🎯 EXEMPLE: Analyse d'une fraction spécifique")
    print("="*45)
    
    csv_path = "daily_albedo_by_fraction_optimized.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Fichier non trouvé: {csv_path}")
        return
    
    from trend_analysis import analyze_single_fraction
    
    # Analyser la fraction "pure_ice" en détail
    result = analyze_single_fraction(
        csv_path=csv_path,
        fraction='pure_ice',
        variable='mean',
        save_graphs=True
    )
    
    if result:
        print("✅ Analyse de fraction terminée!")

def show_package_structure():
    """
    Affiche la structure du package modulaire
    """
    print("\n📁 STRUCTURE DU PACKAGE MODULAIRE")
    print("="*40)
    print("""
trend_analysis/
├── __init__.py              # Point d'entrée du package
├── config.py               # Configuration et constantes
├── utils.py                # Fonctions utilitaires
├── data_loader.py          # Chargement et préparation des données
├── basic_trends.py         # Tests Mann-Kendall et Sen's slope de base
├── seasonal_analysis.py    # Analyses saisonnières et mensuelles
├── advanced_analysis.py    # Autocorrélation, bootstrap, tests avancés  
├── spatial_analysis.py     # Cartographie et analyses spatiales
├── visualizations.py       # Tous les graphiques et visualisations
├── exports.py             # Exports Excel, texte et CSV
└── main.py                # Orchestration et fonctions principales

NOUVEAUTÉS:
• 🎨 Graphiques de statistiques mensuelles (demandés par l'utilisateur)
• 📊 Structure modulaire claire et organisée  
• 🔧 Import robuste avec gestion d'erreurs
• 📝 Documentation complète de chaque module
• 🚀 Fonctions d'analyse rapide et par fraction
• 💾 Exports multiples (Excel, texte, CSV)
    """)

if __name__ == "__main__":
    print("🚀 EXEMPLES D'UTILISATION - SASKATCHEWAN ALBEDO TREND ANALYSIS")
    print("="*70)
    
    # Afficher la structure
    show_package_structure()
    
    # Vérifier si le fichier CSV existe
    csv_path = "daily_albedo_by_fraction_optimized.csv"
    
    if not os.path.exists(csv_path):
        print(f"\n⚠️  ATTENTION: Fichier CSV non trouvé: {csv_path}")
        print("Pour exécuter les exemples, modifiez le chemin dans ce script")
        print("ou placez votre fichier CSV dans le répertoire courant.")
        print("\nStructure attendue du CSV:")
        print("- date, year, month, doy, decimal_year")
        print("- border_mean, border_median, mixed_low_mean, etc.")
        print("- min_pixels_threshold (optionnel)")
        sys.exit(1)
    
    # Demander à l'utilisateur quel exemple exécuter
    print(f"\n✅ Fichier CSV trouvé: {csv_path}")
    print("\nChoisissez un exemple à exécuter:")
    print("1. Analyse complète (recommandé)")
    print("2. Analyse étape par étape") 
    print("3. Analyse rapide")
    print("4. Analyse d'une fraction")
    print("5. Tous les exemples")
    
    choice = input("\nVotre choix (1-5): ").strip()
    
    if choice == "1":
        example_complete_analysis()
    elif choice == "2":
        example_step_by_step()
    elif choice == "3":
        example_quick_analysis()
    elif choice == "4":
        example_single_fraction()
    elif choice == "5":
        example_complete_analysis()
        example_step_by_step()
        example_quick_analysis()
        example_single_fraction()
    else:
        print("❌ Choix invalide. Exécution de l'analyse complète par défaut.")
        example_complete_analysis()
    
    print("\n🎯 Exemples terminés! Consultez les fichiers générés.")