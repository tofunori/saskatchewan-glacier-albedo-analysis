#!/usr/bin/env python3
"""
SCRIPT PRINCIPAL - Analyse des tendances d'albédo du glacier Saskatchewan
========================================================================

Script interactif simple avec menu pour choisir les analyses à effectuer.

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
5 = Graphiques quotidiens seulement (NOUVEAU: inclut albédo quotidien!)
6 = Quitter
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire src au path
script_dir = Path(__file__).parent.absolute()
project_dir = script_dir.parent
src_dir = project_dir / 'src'
sys.path.insert(0, str(src_dir))

print(f"📂 Répertoire de travail actuel: {Path.cwd()}")
print(f"📁 Répertoire du projet: {project_dir}")

# Import de la configuration et des fonctions d'analyse
try:
    from saskatchewan_albedo.config import print_config_summary
    from saskatchewan_albedo.scripts.analysis_functions import (check_config, run_complete_analysis, run_trends_only, 
                                                               run_visualizations_only, run_pixels_only, run_daily_only)
    print("✅ Modules importés avec succès")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
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
    print("5️⃣  Graphiques quotidiens (pixels/QA + albédo)")
    print("6️⃣  Quitter")
    print()
    print("-" * 60)

def get_choice():
    """Obtient le choix de l'utilisateur"""
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