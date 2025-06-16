"""
ANALYSE INTERACTIVE - Pour notebooks et environnements interactifs
=================================================================

Ce module fournit des fonctions pour exécuter les analyses dans des
environnements interactifs comme Jupyter ou VS Code.

UTILISATION:
    from interactive_analysis import *
    
    # Voir les options disponibles
    show_options()
    
    # Exécuter une analyse spécifique
    run_analysis('trends')  # ou 'all', 'viz', 'pixel', 'daily'
    
    # Ou utiliser les fonctions directement
    analyze_trends()
    create_visualizations()
    analyze_pixels()
    create_daily_plots()
"""

import sys
from pathlib import Path

# Configuration du path
script_dir = Path(__file__).parent.absolute()
project_dir = script_dir.parent
src_dir = project_dir / 'src'
sys.path.insert(0, str(src_dir))

# Import des modules nécessaires
from main import (
    check_configuration,
    ensure_data_loaded,
    ensure_trends_calculated,
    run_complete_analysis,
    run_trend_analysis,
    run_standard_visualizations,
    run_pixel_qa_analysis,
    run_daily_timeseries,
    print_config_summary,
    analyses_completed
)

def show_options():
    """Affiche les options d'analyse disponibles"""
    print("\n" + "="*60)
    print("🚀 OPTIONS D'ANALYSE DISPONIBLES")
    print("="*60)
    print("\n📋 Analyses disponibles:")
    print("   'all'    - Exécuter toutes les analyses")
    print("   'trends' - Analyses de tendances et statistiques")
    print("   'viz'    - Visualisations standards")
    print("   'pixel'  - Analyse pixels et QA")
    print("   'daily'  - Graphiques de séries temporelles quotidiennes")
    print("\n💡 Utilisation:")
    print("   run_analysis('trends')  # Exécuter une analyse")
    print("   show_status()          # Voir l'état actuel")
    print("="*60)

def show_status():
    """Affiche l'état actuel des analyses"""
    print("\n📊 État actuel des analyses:")
    print(f"   • Données chargées: {'✅' if analyses_completed.get('data_loaded', False) else '❌'}")
    print(f"   • Tendances calculées: {'✅' if analyses_completed.get('trends_calculated', False) else '❌'}")
    print(f"   • Visualisations standards: {'✅' if analyses_completed.get('visualizations_done', False) else '❌'}")
    print(f"   • Analyse pixels/QA: {'✅' if analyses_completed.get('pixel_analysis_done', False) else '❌'}")
    print(f"   • Graphiques quotidiens: {'✅' if analyses_completed.get('daily_plots_done', False) else '❌'}")

def run_analysis(analysis_type):
    """
    Exécute une analyse spécifique
    
    Parameters:
        analysis_type (str): Type d'analyse ('all', 'trends', 'viz', 'pixel', 'daily')
    """
    print("\n" + "="*70)
    print("🚀 SASKATCHEWAN GLACIER ALBEDO ANALYSIS")
    print("="*70)
    
    # Vérifier la configuration
    print_config_summary()
    
    if not check_configuration():
        print("\n❌ Configuration invalide. Veuillez corriger les erreurs ci-dessus.")
        return False
    
    analysis_type = analysis_type.lower()
    
    try:
        if analysis_type == 'all':
            print("\n🔄 Exécution de l'analyse complète...")
            run_complete_analysis()
        elif analysis_type == 'trends':
            print("\n📊 Exécution des analyses de tendances...")
            run_trend_analysis()
        elif analysis_type == 'viz' or analysis_type == 'visualizations':
            print("\n🎨 Exécution des visualisations standards...")
            run_standard_visualizations()
        elif analysis_type == 'pixel' or analysis_type == 'qa':
            print("\n🔍 Exécution de l'analyse pixels/QA...")
            run_pixel_qa_analysis()
        elif analysis_type == 'daily' or analysis_type == 'timeseries':
            print("\n📅 Exécution des graphiques quotidiens...")
            run_daily_timeseries()
        else:
            print(f"\n❌ Type d'analyse invalide: {analysis_type}")
            show_options()
            return False
        
        print("\n✅ Analyse terminée avec succès!")
        show_status()
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()
        return False

# Fonctions raccourcis pour accès direct
def analyze_all():
    """Exécute toutes les analyses"""
    return run_analysis('all')

def analyze_trends():
    """Exécute l'analyse des tendances"""
    return run_analysis('trends')

def create_visualizations():
    """Crée les visualisations standards"""
    return run_analysis('viz')

def analyze_pixels():
    """Exécute l'analyse des pixels et QA"""
    return run_analysis('pixel')

def create_daily_plots():
    """Crée les graphiques quotidiens"""
    return run_analysis('daily')

# Message d'accueil lors de l'import
print("\n✅ Module d'analyse interactive chargé!")
print("💡 Utilisez show_options() pour voir les options disponibles")
print("📊 Utilisez show_status() pour voir l'état actuel")