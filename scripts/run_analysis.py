#!/usr/bin/env python3
"""
SCRIPT D'ANALYSE DIRECTE - Sans menu interactif
===============================================

Ce script permet d'exécuter directement des analyses spécifiques
sans passer par le menu interactif.

UTILISATION:
    python run_analysis.py [option]
    
OPTIONS:
    1 ou all      - Exécuter toutes les analyses
    2 ou trends   - Analyses de tendances et statistiques
    3 ou viz      - Visualisations standards
    4 ou pixel    - Analyse pixels et QA
    5 ou daily    - Graphiques quotidiens
    
EXEMPLES:
    python run_analysis.py all      # Tout exécuter
    python run_analysis.py trends   # Seulement les tendances
    python run_analysis.py 3        # Seulement les visualisations
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire src au path
script_dir = Path(__file__).parent.absolute()
project_dir = script_dir.parent
src_dir = project_dir / 'src'
sys.path.insert(0, str(src_dir))

# Import des fonctions du script principal
from main import (
    check_configuration, 
    run_complete_analysis,
    run_trend_analysis,
    run_standard_visualizations,
    run_pixel_qa_analysis,
    run_daily_timeseries,
    print_config_summary
)

def main():
    """Fonction principale pour exécution directe"""
    
    print("\n" + "="*70)
    print("🚀 SASKATCHEWAN GLACIER ALBEDO ANALYSIS - MODE DIRECT")
    print("="*70)
    
    # Vérifier la configuration
    print_config_summary()
    
    if not check_configuration():
        print("\n❌ Configuration invalide. Veuillez corriger les erreurs ci-dessus.")
        return 1
    
    # Déterminer quelle analyse exécuter
    if len(sys.argv) > 1:
        option = sys.argv[1].lower()
    else:
        print("\n❌ Aucune option spécifiée!")
        print("Usage: python run_analysis.py [option]")
        print("Options: 1/all, 2/trends, 3/viz, 4/pixel, 5/daily")
        return 1
    
    # Mapping des options
    option_map = {
        '1': 'all', 'all': 'all',
        '2': 'trends', 'trends': 'trends',
        '3': 'viz', 'viz': 'viz', 'visualizations': 'viz',
        '4': 'pixel', 'pixel': 'pixel', 'qa': 'pixel',
        '5': 'daily', 'daily': 'daily', 'timeseries': 'daily'
    }
    
    if option not in option_map:
        print(f"\n❌ Option invalide: {option}")
        print("Options valides: 1/all, 2/trends, 3/viz, 4/pixel, 5/daily")
        return 1
    
    selected = option_map[option]
    
    # Exécuter l'analyse sélectionnée
    try:
        if selected == 'all':
            print("\n🔄 Exécution de l'analyse complète...")
            run_complete_analysis()
        elif selected == 'trends':
            print("\n📊 Exécution des analyses de tendances...")
            run_trend_analysis()
        elif selected == 'viz':
            print("\n🎨 Exécution des visualisations standards...")
            run_standard_visualizations()
        elif selected == 'pixel':
            print("\n🔍 Exécution de l'analyse pixels/QA...")
            run_pixel_qa_analysis()
        elif selected == 'daily':
            print("\n📅 Exécution des graphiques quotidiens...")
            run_daily_timeseries()
        
        print("\n✅ Analyse terminée avec succès!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())