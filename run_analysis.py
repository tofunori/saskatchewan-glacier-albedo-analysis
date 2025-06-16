#!/usr/bin/env python3
"""
Script simple pour exécuter l'analyse des tendances d'albédo
===========================================================

Ce script évite les problèmes d'imports relatifs en utilisant
le package trend_analysis comme un module normal.
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour importer le package
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def main():
    """
    Fonction principale pour exécuter l'analyse
    """
    print("🚀 SASKATCHEWAN ALBEDO TREND ANALYSIS")
    print("="*50)
    
    # MODIFIEZ ICI LE CHEMIN VERS VOTRE FICHIER CSV
    # Option 1: Chemin direct (recommandé)
    direct_csv_path = r"D:\Downloads\daily_albedo_mann_kendall_ready_2010_2024.csv"
    
    # Option 2: Liste de chemins possibles (si vous avez plusieurs fichiers)
    csv_files = [
        direct_csv_path,  # Votre fichier principal
        "daily_albedo_mann_kendall_ready_2010_2024.csv",  # Dans le répertoire courant
        "daily_albedo_by_fraction_optimized.csv",  # Ancien nom
        "data.csv",  # Nom générique
    ]
    
    csv_path = None
    
    # Essayer d'abord le chemin direct
    if os.path.exists(direct_csv_path):
        csv_path = direct_csv_path
        print(f"✅ Fichier trouvé avec le chemin direct: {csv_path}")
    else:
        # Sinon, chercher dans la liste
        for filename in csv_files:
            if os.path.exists(filename):
                csv_path = filename
                print(f"✅ Fichier trouvé: {csv_path}")
                break
    
    if csv_path is None:
        print("❌ Aucun fichier CSV trouvé!")
        print("Chemins recherchés:")
        for f in csv_files:
            print(f"  - {f}")
        print(f"\n💡 SOLUTION RAPIDE:")
        print(f"Modifiez la ligne 'direct_csv_path' dans ce script avec le chemin complet:")
        print(f'direct_csv_path = r"VOTRE_CHEMIN_COMPLET.csv"')
        print(f"\nOu placez votre fichier dans le répertoire courant avec un des noms ci-dessus")
        return False
    
    print(f"✅ Fichier CSV trouvé: {csv_path}")
    
    # Option 1: Analyse complète (recommandée)
    print("\n🔬 Option 1: Analyse complète")
    try:
        from trend_analysis.main import run_complete_analysis
        
        results = run_complete_analysis(
            csv_path=csv_path,
            output_dir='analysis_output',
            variable='mean'
        )
        
        if results:
            print("✅ Analyse complète réussie!")
            return True
        else:
            print("❌ Échec de l'analyse complète")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse complète: {e}")
        print("\nEssai avec l'analyse étape par étape...")
        
        # Option 2: Analyse étape par étape
        return run_step_by_step_analysis(csv_path)

def run_step_by_step_analysis(csv_path):
    """
    Analyse étape par étape en cas de problème avec l'analyse complète
    """
    print("\n🧩 Option 2: Analyse étape par étape")
    
    try:
        # Import des modules individuels
        from trend_analysis.data_loader import SaskatchewanDataLoader
        from trend_analysis.basic_trends import BasicTrendAnalyzer
        from trend_analysis.seasonal_analysis import SeasonalAnalyzer
        
        print("📊 Chargement des données...")
        data_loader = SaskatchewanDataLoader(csv_path)
        data_loader.load_data()
        data_loader.print_data_summary()
        
        print("\n📈 Analyses de tendances de base...")
        basic_analyzer = BasicTrendAnalyzer(data_loader)
        basic_results = basic_analyzer.calculate_trends('mean')
        basic_analyzer.print_summary('mean')
        
        print("\n📅 Analyses saisonnières...")
        seasonal_analyzer = SeasonalAnalyzer(data_loader)
        monthly_results = seasonal_analyzer.analyze_monthly_trends('mean')
        
        # Créer les graphiques de statistiques mensuelles
        print("\n🎨 Création des graphiques mensuels...")
        monthly_graph = seasonal_analyzer.create_monthly_statistics_graphs('mean')
        if monthly_graph:
            print(f"✅ Graphiques mensuels créés: {monthly_graph}")
        
        print("\n✅ Analyse étape par étape réussie!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse étape par étape: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_quick_test():
    """
    Test rapide pour vérifier que les modules fonctionnent
    """
    print("\n⚡ Test rapide des modules...")
    
    try:
        # Tester les imports
        from trend_analysis.config import FRACTION_CLASSES
        from trend_analysis.utils import print_section_header
        
        print_section_header("Test des imports", level=2)
        print(f"✅ Fractions configurées: {len(FRACTION_CLASSES)}")
        print(f"✅ Classes: {FRACTION_CLASSES}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main_with_args():
    """
    Version qui accepte les arguments de ligne de commande
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyse des tendances d\'albédo du glacier Saskatchewan')
    parser.add_argument('csv_path', nargs='?', help='Chemin vers le fichier CSV (optionnel)')
    parser.add_argument('--output', '-o', default='analysis_output', help='Répertoire de sortie')
    parser.add_argument('--variable', '-v', default='mean', choices=['mean', 'median'], 
                       help='Variable à analyser')
    
    args = parser.parse_args()
    
    # Si un chemin est fourni en argument, l'utiliser
    if args.csv_path:
        if os.path.exists(args.csv_path):
            print(f"✅ Utilisation du fichier spécifié: {args.csv_path}")
            return run_analysis_with_path(args.csv_path, args.output, args.variable)
        else:
            print(f"❌ Fichier non trouvé: {args.csv_path}")
            return False
    else:
        # Sinon, utiliser la fonction main() normale
        return main()

def run_analysis_with_path(csv_path, output_dir='analysis_output', variable='mean'):
    """
    Lance l'analyse avec un chemin spécifique
    """
    print("🚀 SASKATCHEWAN ALBEDO TREND ANALYSIS")
    print("="*50)
    print(f"📊 Fichier: {csv_path}")
    print(f"📁 Sortie: {output_dir}")
    print(f"🔍 Variable: {variable}")
    
    try:
        from trend_analysis.main import run_complete_analysis
        
        results = run_complete_analysis(
            csv_path=csv_path,
            output_dir=output_dir,
            variable=variable
        )
        
        if results:
            print("✅ Analyse complète réussie!")
            return True
        else:
            print("❌ Échec de l'analyse complète")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("📋 MODES D'UTILISATION:")
    print("1. Avec chemin en argument: python run_analysis.py 'D:\\Downloads\\votre_fichier.csv'")
    print("2. Modification du script: Changez direct_csv_path dans le script")
    print("3. Fichier dans le répertoire courant")
    print()
    
    # Test rapide d'abord
    if not run_quick_test():
        print("❌ Échec du test rapide - problème avec les modules")
        sys.exit(1)
    
    # Analyse principale avec gestion des arguments
    success = main_with_args()
    
    if success:
        print("\n🎉 Analyse terminée avec succès!")
        print("📁 Consultez les fichiers générés dans le répertoire de sortie")
    else:
        print("\n❌ Échec de l'analyse")
        print("💡 SOLUTIONS:")
        print("  1. Vérifiez le chemin de votre fichier CSV")
        print("  2. Essayez: python run_analysis.py 'D:\\Downloads\\daily_albedo_mann_kendall_ready_2010_2024.csv'")
        print("  3. Ou modifiez direct_csv_path dans ce script")
        print("  4. Installez les dépendances: pip install pandas numpy matplotlib seaborn scipy scikit-learn")
        
        sys.exit(1)