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
    
    # Chemin vers vos données (modifiez selon votre fichier)
    csv_files = [
        "daily_albedo_by_fraction_optimized.csv",
        "data.csv",
        # Ajoutez d'autres noms possibles ici
    ]
    
    csv_path = None
    for filename in csv_files:
        if os.path.exists(filename):
            csv_path = filename
            break
    
    if csv_path is None:
        print("❌ Aucun fichier CSV trouvé!")
        print("Fichiers recherchés:")
        for f in csv_files:
            print(f"  - {f}")
        print("\nVeuillez:")
        print("1. Placer votre fichier CSV dans le répertoire courant")
        print("2. Ou modifier la liste csv_files dans ce script")
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

if __name__ == "__main__":
    # Test rapide d'abord
    if not run_quick_test():
        print("❌ Échec du test rapide - problème avec les modules")
        sys.exit(1)
    
    # Analyse principale
    success = main()
    
    if success:
        print("\n🎉 Analyse terminée avec succès!")
        print("📁 Consultez les fichiers générés dans le répertoire courant")
    else:
        print("\n❌ Échec de l'analyse")
        print("💡 Suggestions:")
        print("  - Vérifiez que toutes les dépendances sont installées:")
        print("    pip install pandas numpy matplotlib seaborn scipy scikit-learn")
        print("  - Vérifiez le format de votre fichier CSV")
        print("  - Consultez les messages d'erreur ci-dessus")
        
        sys.exit(1)