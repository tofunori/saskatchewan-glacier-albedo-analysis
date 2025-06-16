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

# Changer vers le répertoire du projet pour que les chemins relatifs fonctionnent
os.chdir(project_dir)

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
    """Affiche le menu principal organisé par produit MODIS"""
    print("\n" + "="*70)
    print("🚀 MENU D'ANALYSE - SASKATCHEWAN GLACIER ALBEDO")
    print("="*70)
    print()
    print("📊 PRODUITS MODIS:")
    print("1️⃣  MCD43A3 - Albédo général (MODIS Combined)")
    print("2️⃣  MOD10A1 - Albédo de neige (Terra Snow Cover)")
    print()
    print("🔄 COMPARAISON:")
    print("3️⃣  Comparaison MCD43A3 vs MOD10A1")
    print()
    print("4️⃣  Quitter")
    print()
    print("-" * 70)

def get_choice():
    """Obtient le choix de l'utilisateur pour le menu principal"""
    print("\n" + "="*50)
    print("SÉLECTION DU PRODUIT")
    print("="*50)
    print()
    print("Choisissez le produit MODIS à analyser:")
    print("1 = MCD43A3 (Albédo général)")
    print("2 = MOD10A1 (Albédo de neige)")
    print("3 = Comparaison des deux")
    print("4 = Quitter")
    print()
    
    while True:
        try:
            choice = input("➤ Votre choix (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                return int(choice)
            else:
                print(f"❌ '{choice}' n'est pas valide. Tapez un chiffre de 1 à 4.")
        except KeyboardInterrupt:
            print("\n\n👋 Interruption. Au revoir!")
            return 4
        except:
            print("❌ Erreur de saisie. Tapez un chiffre de 1 à 4.")

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

def show_dataset_menu(dataset_name):
    """Affiche le sous-menu pour un dataset spécifique"""
    dataset_info = {
        'MCD43A3': '🌍 MCD43A3 - Albédo général (MODIS Combined)',
        'MOD10A1': '❄️ MOD10A1 - Albédo de neige (Terra Snow Cover)'
    }
    
    print("\n" + "="*60)
    print(f"ANALYSES POUR {dataset_info.get(dataset_name, dataset_name)}")
    print("="*60)
    print()
    print("1️⃣  Analyse complète (toutes les étapes)")
    print("2️⃣  Tendances statistiques seulement")
    print("3️⃣  Visualisations seulement")
    print("4️⃣  Analyse pixels/QA seulement")
    print("5️⃣  Graphiques quotidiens (daily_melt_season)")
    
    # Option spéciale pour MOD10A1 seulement
    if dataset_name == 'MOD10A1':
        print("6️⃣  Comparaison entre fractions MOD10A1 🆕")
        print()
        print("7️⃣  Retour au menu principal")
    else:
        print()
        print("6️⃣  Retour au menu principal")
    
    print()
    print("-" * 60)

def get_dataset_analysis_choice(dataset_name=None):
    """Obtient le choix d'analyse pour un dataset"""
    print("\n" + "="*40)
    print("TYPE D'ANALYSE")
    print("="*40)
    print()
    
    # Déterminer le nombre maximum d'options selon le dataset
    max_choice = 7 if dataset_name == 'MOD10A1' else 6
    max_choice_str = f"1-{max_choice}"
    valid_choices = [str(i) for i in range(1, max_choice + 1)]
    
    while True:
        try:
            choice = input(f"➤ Votre choix ({max_choice_str}): ").strip()
            if choice in valid_choices:
                return int(choice)
            else:
                print(f"❌ '{choice}' n'est pas valide. Tapez un chiffre de {max_choice_str}.")
        except KeyboardInterrupt:
            print("\n\n👋 Interruption.")
            return max_choice  # Retour au menu principal
        except:
            print(f"❌ Erreur de saisie. Tapez un chiffre de {max_choice_str}.")

def show_comparison_menu():
    """Affiche le sous-menu pour la comparaison"""
    print("\n" + "="*60)
    print("🔄 COMPARAISON MCD43A3 vs MOD10A1")
    print("="*60)
    print()
    print("1️⃣  Comparaison complète (corrélations + différences + tendances)")
    print("2️⃣  Corrélations seulement")
    print("3️⃣  Visualisations comparatives seulement")
    print("4️⃣  Graphiques quotidiens par saison de fonte")
    print()
    print("5️⃣  Retour au menu principal")
    print()
    print("-" * 60)

def get_comparison_analysis_choice():
    """Obtient le choix d'analyse pour la comparaison"""
    print("\n" + "="*40)
    print("TYPE DE COMPARAISON")
    print("="*40)
    print()
    
    while True:
        try:
            choice = input("➤ Votre choix (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return int(choice)
            else:
                print(f"❌ '{choice}' n'est pas valide. Tapez un chiffre de 1 à 5.")
        except KeyboardInterrupt:
            print("\n\n👋 Interruption.")
            return 5
        except:
            print("❌ Erreur de saisie. Tapez un chiffre de 1 à 5.")

def _get_fraction_choice():
    """Permet à l'utilisateur de choisir la fraction à analyser"""
    from saskatchewan_albedo.config import FRACTION_CLASSES, CLASS_LABELS
    
    print("\n" + "="*50)
    print("🔍 CHOIX DE LA FRACTION À ANALYSER")
    print("="*50)
    print()
    
    for i, fraction in enumerate(FRACTION_CLASSES, 1):
        print(f"{i}️⃣  {CLASS_LABELS[fraction]}")
    print()
    print("-" * 50)
    
    while True:
        try:
            choice = input(f"➤ Votre choix (1-{len(FRACTION_CLASSES)}): ").strip()
            choice_num = int(choice)
            if 1 <= choice_num <= len(FRACTION_CLASSES):
                selected_fraction = FRACTION_CLASSES[choice_num - 1]
                print(f"✅ Fraction sélectionnée: {CLASS_LABELS[selected_fraction]}")
                return selected_fraction
            else:
                print(f"❌ '{choice}' n'est pas valide. Tapez un chiffre de 1 à {len(FRACTION_CLASSES)}.")
        except KeyboardInterrupt:
            print("\n\n👋 Interruption.")
            return 'pure_ice'  # Valeur par défaut
        except ValueError:
            print(f"❌ Erreur de saisie. Tapez un chiffre de 1 à {len(FRACTION_CLASSES)}.")
        except:
            print(f"❌ Erreur de saisie. Tapez un chiffre de 1 à {len(FRACTION_CLASSES)}.")

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
                # Sous-menu MCD43A3
                _handle_dataset_menu('MCD43A3')
                
            elif choice == 2:
                # Sous-menu MOD10A1
                _handle_dataset_menu('MOD10A1')
                
            elif choice == 3:
                # Sous-menu Comparaison
                _handle_comparison_menu()
                
            elif choice == 4:
                print("\n👋 Au revoir!")
                break
            
        except Exception as e:
            print(f"\n❌ Erreur lors de l'exécution: {e}")
            print("📝 Consultez les logs pour plus de détails.")

def _handle_dataset_menu(dataset_name):
    """Gère le sous-menu pour un dataset spécifique"""
    from saskatchewan_albedo.scripts.analysis_functions import (
        run_dataset_analysis, run_custom_analysis
    )
    
    while True:
        show_dataset_menu(dataset_name)
        choice = get_dataset_analysis_choice(dataset_name)
        
        # Gérer le retour au menu principal selon le dataset
        if (dataset_name == 'MOD10A1' and choice == 7) or (dataset_name != 'MOD10A1' and choice == 6):
            break
            
        try:
            if choice == 1:
                # Analyse complète
                print(f"\n🔍 Analyse complète du dataset {dataset_name}...")
                run_dataset_analysis(dataset_name)
                
            elif choice == 2:
                # Tendances seulement
                print(f"\n📈 Analyse des tendances pour {dataset_name}...")
                run_custom_analysis(dataset_name, 2)
                
            elif choice == 3:
                # Visualisations seulement
                print(f"\n🎨 Génération des visualisations pour {dataset_name}...")
                run_custom_analysis(dataset_name, 3)
                
            elif choice == 4:
                # Pixels/QA seulement
                print(f"\n🔍 Analyse pixels/QA pour {dataset_name}...")
                run_custom_analysis(dataset_name, 4)
                
            elif choice == 5:
                # Graphiques quotidiens
                print(f"\n📅 Graphiques quotidiens pour {dataset_name}...")
                run_custom_analysis(dataset_name, 5)
                
            elif choice == 6 and dataset_name == 'MOD10A1':
                # Comparaison entre fractions MOD10A1 (option spéciale)
                print(f"\n🔍 Comparaison entre fractions MOD10A1...")
                from saskatchewan_albedo.scripts.analysis_functions import run_mod10a1_fraction_comparison
                run_mod10a1_fraction_comparison()
                
        except Exception as e:
            print(f"\n❌ Erreur lors de l'analyse {dataset_name}: {e}")
        
        print("\n" + "="*50)
        try:
            cont = input("➤ Autre analyse pour ce dataset? (o/n): ").strip().lower()
            if cont not in ['o', 'oui', 'y', 'yes']:
                break
        except KeyboardInterrupt:
            break
        except:
            break

def _handle_comparison_menu():
    """Gère le sous-menu pour la comparaison"""
    from saskatchewan_albedo.scripts.analysis_functions import (
        run_comparison_analysis, run_correlation_analysis, run_comparative_visualizations
    )
    
    while True:
        show_comparison_menu()
        choice = get_comparison_analysis_choice()
        
        if choice == 5:  # Retour au menu principal
            break
            
        try:
            if choice == 1:
                # Comparaison complète
                print("\n🔄 Comparaison complète MCD43A3 vs MOD10A1...")
                run_comparison_analysis()
                
            elif choice == 2:
                # Corrélations seulement
                print("\n📊 Analyse de corrélation entre produits...")
                run_correlation_analysis()
                
            elif choice == 3:
                # Visualisations comparatives
                print("\n📈 Génération des visualisations comparatives...")
                run_comparative_visualizations()
                
            elif choice == 4:
                # Graphiques quotidiens par saison de fonte
                print("\n📅 Graphiques quotidiens par saison de fonte...")
                # Demander la fraction à analyser
                fraction_choice = _get_fraction_choice()
                from saskatchewan_albedo.scripts.analysis_functions import run_daily_melt_season_comparison
                run_daily_melt_season_comparison(fraction_choice)
                
        except Exception as e:
            print(f"\n❌ Erreur lors de la comparaison: {e}")
        
        print("\n" + "="*50)
        try:
            cont = input("➤ Autre analyse comparative? (o/n): ").strip().lower()
            if cont not in ['o', 'oui', 'y', 'yes']:
                break
        except KeyboardInterrupt:
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