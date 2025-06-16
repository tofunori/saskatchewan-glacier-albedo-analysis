#!/usr/bin/env python3
"""
Script VS Code pour l'analyse des tendances d'albédo du glacier Saskatchewan
==========================================================================

Ce script est optimisé pour l'exécution interactive dans VS Code.
Il effectue EXACTEMENT les mêmes analyses que run_analysis.py.

Pour utiliser :
1. Configurez le chemin de votre fichier CSV ci-dessous
2. Appuyez sur F5 ou cliquez "Run" dans VS Code
3. Consultez les résultats dans analysis_output/
"""

import os
import sys
from pathlib import Path

# Configuration du projet
print("🚀 SASKATCHEWAN ALBEDO TREND ANALYSIS - VS CODE")
print("="*60)

# Ajouter le répertoire du projet au path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# ==========================================
# CONFIGURATION - MODIFIEZ ICI VOTRE CHEMIN
# ==========================================

# Chemin vers votre fichier CSV (utilisez r"" pour les chemins Windows)
CSV_PATH = r"D:\Downloads\daily_albedo_mann_kendall_ready_2010_2024.csv"

# Répertoire de sortie pour les résultats
OUTPUT_DIR = "analysis_output_vscode"

# Variable à analyser ('mean' ou 'median')
VARIABLE = "mean"

# ==========================================

def main():
    """
    Fonction principale - MÊMES analyses que le script original
    """
    print(f"📊 Fichier CSV : {CSV_PATH}")
    print(f"📁 Sortie : {OUTPUT_DIR}")
    print(f"🔍 Variable : {VARIABLE}")
    print()
    
    # Vérifier que le fichier existe
    if not os.path.exists(CSV_PATH):
        print(f"❌ ERREUR : Fichier CSV non trouvé !")
        print(f"   Chemin recherché : {CSV_PATH}")
        print()
        print("💡 SOLUTION :")
        print("   Modifiez la variable CSV_PATH dans ce script avec le chemin correct")
        print("   Exemple : CSV_PATH = r'C:\\votre\\chemin\\vers\\fichier.csv'")
        return False
    
    print(f"✅ Fichier CSV trouvé : {CSV_PATH}")
    print()
    
    # Test rapide des modules
    print("⚡ Test des modules...")
    try:
        from trend_analysis.config import FRACTION_CLASSES
        from trend_analysis.utils import print_section_header
        
        print_section_header("Modules chargés avec succès", level=2)
        print(f"✅ Fractions configurées : {len(FRACTION_CLASSES)}")
        print(f"✅ Classes : {FRACTION_CLASSES}")
        print()
        
    except Exception as e:
        print(f"❌ ERREUR d'import des modules : {e}")
        print()
        print("💡 SOLUTIONS :")
        print("   1. Assurez-vous d'être dans le bon répertoire")
        print("   2. Vérifiez que le dossier trend_analysis/ existe")
        print("   3. Installez les dépendances : pip install pandas numpy matplotlib seaborn scipy scikit-learn")
        return False
    
    # ANALYSE COMPLÈTE - IDENTIQUE au script original
    print("🔬 Lancement de l'analyse complète...")
    print("   Ceci peut prendre quelques minutes...")
    print()
    
    try:
        # Import de la fonction principale
        from trend_analysis.main import run_complete_analysis
        
        # MÊME analyse que dans run_analysis.py
        results = run_complete_analysis(
            csv_path=CSV_PATH,
            output_dir=OUTPUT_DIR,
            variable=VARIABLE
        )
        
        if results:
            print()
            print("🎉 ANALYSE TERMINÉE AVEC SUCCÈS !")
            print("="*50)
            print(f"📁 Tous les résultats sont dans : {OUTPUT_DIR}/")
            print()
            
            # Afficher les fichiers générés
            if 'files_generated' in results:
                print("📄 Fichiers générés :")
                for file_info in results['files_generated']:
                    print(f"   ✅ {file_info['description']} : {file_info['path']}")
                    if 'size_kb' in file_info:
                        print(f"      Taille : {file_info['size_kb']} KB")
                print()
            
            # Résumé des résultats
            if 'basic_trends' in results:
                basic_results = results['basic_trends']
                significant_count = sum(1 for r in basic_results.values() 
                                      if not r.get('error', False) and r['mann_kendall']['p_value'] < 0.05)
                total_count = sum(1 for r in basic_results.values() if not r.get('error', False))
                
                print("📊 RÉSUMÉ DES TENDANCES :")
                print(f"   • Fractions analysées : {total_count}")
                print(f"   • Tendances significatives : {significant_count}")
                
                if significant_count > 0:
                    print("   • Fractions avec tendances significatives :")
                    for fraction, result in basic_results.items():
                        if not result.get('error', False) and result['mann_kendall']['p_value'] < 0.05:
                            trend = result['mann_kendall']['trend']
                            p_val = result['mann_kendall']['p_value']
                            slope = result['sen_slope']['slope_per_decade']
                            print(f"     - {result['label']} : {trend} (p={p_val:.4f}, {slope:.6f}/décennie)")
                print()
            
            print("🎯 GRAPHIQUES PRINCIPAUX À CONSULTER :")
            print("   📊 monthly_statistics_mean.png - VOS GRAPHIQUES MENSUELS")
            print("   📈 trend_overview_mean.png - Vue d'ensemble des tendances")
            print("   🎨 dashboard_summary_mean.png - Dashboard complet")
            print("   📄 Rapport texte complet avec toutes les statistiques")
            print()
            print("✨ Analyse complète terminée ! Consultez les fichiers générés.")
            return True
            
        else:
            print("❌ ÉCHEC de l'analyse complète")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR lors de l'analyse : {e}")
        print()
        print("💡 SOLUTIONS POSSIBLES :")
        print("   1. Vérifiez le format de votre fichier CSV")
        print("   2. Assurez-vous que toutes les dépendances sont installées")
        print("   3. Vérifiez l'espace disque disponible")
        
        import traceback
        print("\n🔍 Détails de l'erreur :")
        traceback.print_exc()
        return False

def show_configuration():
    """
    Affiche la configuration actuelle
    """
    print("⚙️  CONFIGURATION ACTUELLE :")
    print("-" * 30)
    print(f"Fichier CSV : {CSV_PATH}")
    print(f"Répertoire de sortie : {OUTPUT_DIR}")
    print(f"Variable analysée : {VARIABLE}")
    print(f"Répertoire de travail : {Path.cwd()}")
    print()

if __name__ == "__main__":
    # Afficher la configuration
    show_configuration()
    
    # Lancer l'analyse principale
    success = main()
    
    if success:
        print("🎊 SUCCÈS ! Votre analyse est terminée.")
        print("📂 Ouvrez le dossier de sortie pour voir tous les résultats.")
    else:
        print("💔 ÉCHEC de l'analyse.")
        print("📞 Consultez les messages d'erreur ci-dessus pour le dépannage.")
    
    print("\n" + "="*60)
    print("Script terminé. Vous pouvez fermer cette fenêtre.")