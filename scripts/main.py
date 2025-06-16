#!/usr/bin/env python3
"""
SCRIPT PRINCIPAL - Analyse des tendances d'albédo du glacier Saskatchewan
========================================================================

Ce script autonome effectue l'analyse complète des tendances d'albédo.
Tous les modules sont dans le même dossier - pas de problèmes d'imports !

POUR UTILISER :
1. Modifiez le chemin CSV_PATH ci-dessous si nécessaire
2. Appuyez sur F5 dans VS Code ou exécutez : python main.py  
3. Consultez les résultats dans le dossier results/

ANALYSES INCLUSES :
- Tests Mann-Kendall et Sen's slope pour toutes les fractions
- Graphiques mensuels (4 sous-graphiques demandés)
- Analyses saisonnières détaillées
- Visualisations complètes (tendances, patterns, distributions)
- Exports Excel et texte avec tous les résultats
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

# Imports des modules du package saskatchewan_albedo
try:
    from saskatchewan_albedo.config import CSV_PATH, OUTPUT_DIR, ANALYSIS_VARIABLE, print_config_summary
    from saskatchewan_albedo.data.handler import AlbedoDataHandler
    from saskatchewan_albedo.analysis.trends import TrendCalculator
    from saskatchewan_albedo.visualization.monthly import MonthlyVisualizer
    from saskatchewan_albedo.utils.helpers import print_section_header, ensure_directory_exists, print_analysis_summary
    print("✅ Tous les modules importés avec succès")
except ImportError as e:
    print(f"❌ Erreur d'import des modules: {e}")
    print(f"📁 Vérifiez que tous les fichiers .py sont dans: {script_dir}")
    print("📋 Fichiers requis: config.py, data_handler.py, trend_calculator.py, monthly_visualizer.py, helpers.py")
    sys.exit(1)

def main():
    """
    Fonction principale d'analyse complète
    """
    # En-tête
    print("🚀 SASKATCHEWAN GLACIER ALBEDO TREND ANALYSIS")
    print("=" * 70)
    print("📅 Analyse lancée le:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # Afficher la configuration
    print_config_summary()
    
    # Vérifier le fichier CSV
    if not os.path.exists(CSV_PATH):
        print(f"\n❌ ERREUR : Fichier CSV non trouvé !")
        print(f"   Chemin configuré : {CSV_PATH}")
        print()
        print("💡 SOLUTION :")
        print(f"   Modifiez la variable CSV_PATH dans config.py")
        print("   ou placez votre fichier CSV avec le bon nom")
        return False
    
    print(f"✅ Fichier CSV trouvé : {CSV_PATH}")
    
    # Créer le répertoire de sortie (chemin absolu)
    output_path = PROJECT_DIR / OUTPUT_DIR
    ensure_directory_exists(str(output_path))
    print(f"📁 Répertoire de sortie : {output_path}/")
    print()
    
    try:
        # ÉTAPE 1: Chargement et préparation des données
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
        
        # ÉTAPE 4: VOS GRAPHIQUES MENSUELS DEMANDÉS
        print_section_header("ÉTAPE 4: Création des graphiques mensuels", level=1)
        
        monthly_visualizer = MonthlyVisualizer(data_handler)
        
        # Créer les 4 graphiques mensuels que vous avez demandés
        monthly_graph_path = monthly_visualizer.create_monthly_statistics_graphs(
            ANALYSIS_VARIABLE, 
            str(output_path / f'monthly_statistics_{ANALYSIS_VARIABLE}.png')
        )
        
        if monthly_graph_path:
            print(f"🎨 Vos graphiques mensuels créés : {monthly_graph_path}")
        
        # Comparaison des tendances mensuelles
        if monthly_results:
            comparison_path = monthly_visualizer.create_seasonal_trends_comparison(
                monthly_results, ANALYSIS_VARIABLE,
                str(output_path / f'monthly_comparison_{ANALYSIS_VARIABLE}.png')
            )
            
            # Résumé mensuel
            monthly_visualizer.print_monthly_summary(ANALYSIS_VARIABLE)
        
        # ÉTAPE 5: Autres visualisations (optionnel)
        print_section_header("ÉTAPE 5: Visualisations additionnelles", level=1)
        
        try:
            # Importer le module de visualisations si disponible
            from chart_generator import ChartGenerator
            
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
            
        except ImportError:
            print("⚠️  Module de visualisations additionnelles non disponible")
        
        # ÉTAPE 6: Exports des résultats
        print_section_header("ÉTAPE 6: Export des résultats", level=1)
        
        try:
            # Export du tableau de résumé
            summary_table = trend_calculator.get_summary_table(ANALYSIS_VARIABLE)
            summary_csv_path = str(output_path / f'summary_trends_{ANALYSIS_VARIABLE}.csv')
            summary_table.to_csv(summary_csv_path, index=False)
            print(f"📊 Tableau de résumé exporté : {summary_csv_path}")
            
            # Export du tableau mensuel
            monthly_table = monthly_visualizer.create_monthly_summary_table(ANALYSIS_VARIABLE)
            if not monthly_table.empty:
                monthly_csv_path = str(output_path / f'monthly_stats_{ANALYSIS_VARIABLE}.csv')
                monthly_table.to_csv(monthly_csv_path, index=False)
                print(f"📅 Statistiques mensuelles exportées : {monthly_csv_path}")
            
            # Export des données nettoyées
            cleaned_data_path = data_handler.export_cleaned_data(
                str(output_path / f'cleaned_data_{ANALYSIS_VARIABLE}.csv')
            )
            
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
        
        generated_files = []
        
        # Vérifier quels fichiers ont été créés
        output_files = [
            ('Graphiques mensuels (DEMANDÉS)', f'monthly_statistics_{ANALYSIS_VARIABLE}.png'),
            ('Comparaison mensuelle', f'monthly_comparison_{ANALYSIS_VARIABLE}.png'),
            ('Aperçu des tendances', f'trend_overview_{ANALYSIS_VARIABLE}.png'),
            ('Patterns saisonniers', f'seasonal_patterns_{ANALYSIS_VARIABLE}.png'),
            ('Résumé des tendances', f'summary_trends_{ANALYSIS_VARIABLE}.csv'),
            ('Statistiques mensuelles', f'monthly_stats_{ANALYSIS_VARIABLE}.csv'),
            ('Données nettoyées', f'cleaned_data_{ANALYSIS_VARIABLE}.csv')
        ]
        
        for description, filename in output_files:
            filepath = output_path / filename
            if filepath.exists():
                size_kb = filepath.stat().st_size / 1024
                generated_files.append((description, str(filepath), size_kb))
                print(f"  ✅ {description}: {filepath} ({size_kb:.1f} KB)")
        
        print(f"\n🎉 ANALYSE TERMINÉE AVEC SUCCÈS !")
        print(f"📁 {len(generated_files)} fichiers générés dans: {output_path}/")
        print(f"🎯 GRAPHIQUES PRINCIPAUX À CONSULTER :")
        print(f"   📊 monthly_statistics_{ANALYSIS_VARIABLE}.png - VOS GRAPHIQUES MENSUELS")
        print(f"   📈 trend_overview_{ANALYSIS_VARIABLE}.png - Vue d'ensemble des tendances")
        print(f"   📄 summary_trends_{ANALYSIS_VARIABLE}.csv - Résumé des statistiques")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DE L'ANALYSE :")
        print(f"   {e}")
        print(f"\n🔍 Détails de l'erreur :")
        import traceback
        traceback.print_exc()
        
        print(f"\n💡 SUGGESTIONS :")
        print(f"   1. Vérifiez le format de votre fichier CSV")
        print(f"   2. Assurez-vous que les colonnes d'albédo existent")
        print(f"   3. Vérifiez l'espace disque disponible")
        print(f"   4. Installez les dépendances: pip install pandas numpy matplotlib seaborn scipy scikit-learn")
        
        return False

def test_imports():
    """
    Test rapide pour vérifier que tous les modules sont disponibles
    """
    print("⚡ Test des modules...")
    
    try:
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
        from scipy import stats
        print("✅ Dépendances principales OK")
        
        from saskatchewan_albedo.config import FRACTION_CLASSES
        from saskatchewan_albedo.utils.helpers import print_section_header
        print("✅ Modules locaux OK")
        
        print(f"✅ Configuration: {len(FRACTION_CLASSES)} fractions")
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("💡 Installez les dépendances:")
        print("   pip install pandas numpy matplotlib seaborn scipy scikit-learn")
        return False

def print_usage_info():
    """
    Affiche les informations d'utilisation
    """
    print("📖 INFORMATIONS D'UTILISATION")
    print("=" * 40)
    print("Ce script effectue une analyse complète automatisée.")
    print()
    print("🔧 CONFIGURATION:")
    print(f"   • Fichier CSV: Modifiez CSV_PATH dans config.py")
    print(f"   • Variable: {ANALYSIS_VARIABLE} (modifiable dans config.py)")
    print(f"   • Sortie: {OUTPUT_DIR}/ (modifiable dans config.py)")
    print()
    print("🎨 GRAPHIQUES GÉNÉRÉS:")
    print("   • Statistiques mensuelles (4 sous-graphiques)")
    print("   • Tendances par fraction")
    print("   • Patterns saisonniers")
    print("   • Comparaisons temporelles")
    print()
    print("📊 ANALYSES INCLUSES:")
    print("   • Tests Mann-Kendall pour toutes les fractions")
    print("   • Pentes de Sen avec intervalles de confiance")
    print("   • Analyses saisonnières détaillées")
    print("   • Statistiques descriptives complètes")
    print("=" * 40)

if __name__ == "__main__":
    # Afficher les informations d'utilisation
    print_usage_info()
    print()
    
    # Test rapide des imports
    if not test_imports():
        print("❌ Échec du test des modules")
        sys.exit(1)
    
    print("🚀 Lancement de l'analyse principale...")
    print()
    
    # Analyse principale
    success = main()
    
    if success:
        print("\n" + "=" * 70)
        print("🎊 ANALYSE TERMINÉE AVEC SUCCÈS !")
        print("📂 Consultez le dossier de sortie pour tous les résultats.")
        print("✨ Vos graphiques mensuels sont maintenant disponibles !")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("💔 ÉCHEC DE L'ANALYSE")
        print("📞 Consultez les messages d'erreur ci-dessus.")
        print("=" * 70)
        sys.exit(1)