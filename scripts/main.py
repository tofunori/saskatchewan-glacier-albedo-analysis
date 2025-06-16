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
    """Affiche le menu d'options avec choix de datasets"""
    print("\n" + "="*70)
    print("🚀 MENU D'ANALYSE - SASKATCHEWAN GLACIER ALBEDO")
    print("="*70)
    print()
    print("📊 ANALYSES PAR DATASET:")
    print("1️⃣  Analyse MCD43A3 (Albédo général MODIS)")
    print("2️⃣  Analyse MOD10A1 (Albédo de neige Terra)")
    print()
    print("🔄 ANALYSES COMPARATIVES:")
    print("3️⃣  Comparaison MCD43A3 vs MOD10A1")
    print("4️⃣  Analyse de corrélation entre produits")
    print()
    print("🛠️  OUTILS AVANCÉS:")
    print("5️⃣  Analyse personnalisée (choix dataset)")
    print("6️⃣  Visualisations comparatives")
    print("7️⃣  Export des résultats")
    print()
    print("8️⃣  Quitter")
    print()
    print("-" * 70)

def get_choice():
    """Obtient le choix de l'utilisateur avec validation étendue"""
    print("\n" + "="*70)
    print("SÉLECTION DE L'ANALYSE")
    print("="*70)
    print()
    print("Tapez le numéro de votre choix puis appuyez sur Entrée:")
    print("1 = MCD43A3 (Albédo général)")
    print("2 = MOD10A1 (Albédo neige)")
    print("3 = Comparaison complète")
    print("4 = Corrélations")
    print("5 = Analyse personnalisée")
    print("6 = Visualisations")
    print("7 = Exports")
    print("8 = Quitter")
    print()
    
    while True:
        try:
            choice = input("➤ Votre choix (1-8): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                return int(choice)
            else:
                print(f"❌ '{choice}' n'est pas valide. Tapez un chiffre de 1 à 8.")
        except KeyboardInterrupt:
            print("\n\n👋 Interruption. Au revoir!")
            return 8
        except:
            print("❌ Erreur de saisie. Tapez un chiffre de 1 à 8.")

def get_dataset_choice():
    """Permet à l'utilisateur de choisir un dataset spécifique"""
    print("\n" + "="*50)
    print("CHOIX DU DATASET")
    print("="*50)
    print()
    print("1️⃣  MCD43A3 - Albédo général (MODIS Combined)")
    print("2️⃣  MOD10A1 - Albédo de neige (Terra Snow Cover)")
    print()
    
    while True:
        try:
            choice = input("➤ Choisissez le dataset (1-2): ").strip()
            if choice == '1':
                return 'MCD43A3'
            elif choice == '2':
                return 'MOD10A1'
            else:
                print(f"❌ '{choice}' n'est pas valide. Tapez 1 ou 2.")
        except KeyboardInterrupt:
            print("\n\n👋 Interruption.")
            return None
        except:
            print("❌ Erreur de saisie. Tapez 1 ou 2.")

def get_analysis_type():
    """Permet à l'utilisateur de choisir le type d'analyse"""
    print("\n" + "="*50)
    print("TYPE D'ANALYSE")
    print("="*50)
    print()
    print("1️⃣  Analyse complète")
    print("2️⃣  Tendances seulement")
    print("3️⃣  Visualisations seulement")
    print("4️⃣  Pixels/QA seulement")
    print("5️⃣  Graphiques quotidiens")
    print()
    
    while True:
        try:
            choice = input("➤ Type d'analyse (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return int(choice)
            else:
                print(f"❌ '{choice}' n'est pas valide. Tapez un chiffre de 1 à 5.")
        except KeyboardInterrupt:
            print("\n\n👋 Interruption.")
            return None
        except:
            print("❌ Erreur de saisie. Tapez un chiffre de 1 à 5.")

def main():
    """Fonction principale avec support multi-datasets"""
    print("\n" + "="*70)
    print("🚀 SASKATCHEWAN GLACIER ALBEDO TREND ANALYSIS")
    print("="*70)
    print("📅 Session lancée le:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Afficher la configuration générale et vérifier les datasets
    print_config_summary()
    
    # Importer les nouvelles fonctions
    try:
        from saskatchewan_albedo.scripts.analysis_functions import (
            run_dataset_analysis, run_comparison_analysis, run_correlation_analysis,
            run_custom_analysis, run_comparative_visualizations, run_export_all,
            check_datasets_availability
        )
    except ImportError as e:
        print(f"❌ Erreur d'import des nouvelles fonctions: {e}")
        print("📝 Utilisation du mode de compatibilité...")
        from saskatchewan_albedo.scripts.analysis_functions import (
            run_complete_analysis, run_trends_only, run_visualizations_only,
            run_pixels_only, run_daily_only
        )
        # Mode de compatibilité avec l'ancien menu
        _run_legacy_mode()
        return
    
    # Vérifier la disponibilité des datasets
    if not check_datasets_availability():
        print("\n❌ Aucun dataset valide trouvé.")
        return
    
    while True:
        show_menu()
        choice = get_choice()
        
        try:
            if choice == 1:
                # Analyse MCD43A3
                print("\n🔍 Analyse du dataset MCD43A3 (Albédo général)...")
                run_dataset_analysis('MCD43A3')
                
            elif choice == 2:
                # Analyse MOD10A1
                print("\n❄️ Analyse du dataset MOD10A1 (Albédo de neige)...")
                run_dataset_analysis('MOD10A1')
                
            elif choice == 3:
                # Comparaison complète
                print("\n🔄 Comparaison complète MCD43A3 vs MOD10A1...")
                run_comparison_analysis()
                
            elif choice == 4:
                # Analyse de corrélation
                print("\n📊 Analyse de corrélation entre produits...")
                run_correlation_analysis()
                
            elif choice == 5:
                # Analyse personnalisée
                print("\n⚙️ Analyse personnalisée...")
                dataset = get_dataset_choice()
                if dataset:
                    analysis_type = get_analysis_type()
                    if analysis_type:
                        run_custom_analysis(dataset, analysis_type)
                
            elif choice == 6:
                # Visualisations comparatives
                print("\n📈 Génération des visualisations comparatives...")
                run_comparative_visualizations()
                
            elif choice == 7:
                # Export des résultats
                print("\n💾 Export de tous les résultats...")
                run_export_all()
                
            elif choice == 8:
                print("\n👋 Au revoir!")
                break
            
        except Exception as e:
            print(f"\n❌ Erreur lors de l'exécution: {e}")
            print("📝 Consultez les logs pour plus de détails.")
        
        print("\n" + "="*60)
        try:
            cont = input("➤ Continuer avec une autre analyse? (o/n): ").strip().lower()
            if cont not in ['o', 'oui', 'y', 'yes']:
                print("\n👋 Au revoir!")
                break
        except KeyboardInterrupt:
            print("\n\n👋 Interruption. Au revoir!")
            break
        except:
            break

def _run_legacy_mode():
    """Mode de compatibilité avec l'ancien menu"""
    print("\n⚠️ Mode de compatibilité activé - Menu simplifié")
    
    from saskatchewan_albedo.scripts.analysis_functions import (
        run_complete_analysis, run_trends_only, run_visualizations_only,
        run_pixels_only, run_daily_only
    )
    
    while True:
        print("\n" + "="*60)
        print("🚀 MENU SIMPLIFIÉ")
        print("="*60)
        print("1️⃣  Analyse complète")
        print("2️⃣  Tendances seulement")
        print("3️⃣  Visualisations")
        print("4️⃣  Pixels/QA")
        print("5️⃣  Graphiques quotidiens")
        print("6️⃣  Quitter")
        
        try:
            choice = input("\n➤ Votre choix (1-6): ").strip()
            
            if choice == '1':
                run_complete_analysis()
            elif choice == '2':
                run_trends_only()
            elif choice == '3':
                run_visualizations_only()
            elif choice == '4':
                run_pixels_only()
            elif choice == '5':
                run_daily_only()
            elif choice == '6':
                break
            else:
                print("❌ Choix invalide")
                
        except KeyboardInterrupt:
            print("\n👋 Au revoir!")
            break

if __name__ == "__main__":
    main()