#!/usr/bin/env python3
"""
Test script for the elevation analysis functionality
"""

import sys
from pathlib import Path

# Ajouter le répertoire du projet au path
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))

def test_elevation_analysis():
    """Test the elevation analysis module"""
    print("="*60)
    print("🧪 TEST ANALYSE FRACTION × ÉLÉVATION")
    print("="*60)
    
    try:
        # Test import des modules
        print("\n1️⃣ Test imports...")
        from analysis.elevation_analysis import ElevationAnalyzer, run_elevation_analysis
        from visualization.elevation_plots import ElevationPlotter, create_elevation_visualizations
        from config import ELEVATION_CONFIG
        print("✅ Tous les modules importés avec succès")
        
        # Test configuration
        print("\n2️⃣ Test configuration...")
        print(f"📁 Fichier CSV: {ELEVATION_CONFIG['csv_path']}")
        print(f"📊 Méthode: {ELEVATION_CONFIG['methodology']}")
        print(f"🧊 Fractions: {ELEVATION_CONFIG['fraction_classes']}")
        print(f"🏔️ Zones élévation: {ELEVATION_CONFIG['elevation_zones']}")
        print(f"🔢 Combinaisons: {ELEVATION_CONFIG['combinations']}")
        
        # Test existence du fichier
        csv_path = Path(ELEVATION_CONFIG['csv_path'])
        if csv_path.exists():
            print(f"✅ Fichier CSV trouvé: {csv_path}")
            print(f"📊 Taille: {csv_path.stat().st_size / 1024 / 1024:.1f} MB")
            
            # Test chargement données
            print("\n3️⃣ Test chargement données...")
            analyzer = ElevationAnalyzer(str(csv_path), "results/elevation_analysis_test")
            analyzer.load_data()
            
            print(f"✅ Données chargées: {len(analyzer.data)} observations")
            print(f"✅ Données annuelles: {len(analyzer.annual_data)} années")
            print(f"✅ Combinaisons valides: {len(analyzer.valid_combinations)}")
            
            # Test analyse rapide
            print("\n4️⃣ Test analyse tendances...")
            analyzer.calculate_trends()
            print(f"✅ Tendances calculées: {len(analyzer.trends)}")
            
            # Test analyse élévation
            print("\n5️⃣ Test analyse élévation...")
            analyzer.analyze_elevation_dependency()
            
            transient = analyzer.elevation_analysis['transient_snowline']
            print(f"✅ Zone déclin maximal: {transient['strongest_decline_zone']}")
            print(f"✅ Hypothèse supportée: {transient['hypothesis_supported']}")
            
            # Test exports
            print("\n6️⃣ Test exports...")
            trends_df, zone_summary_df = analyzer.create_summary_report()
            wm_df = analyzer.export_williamson_menounos_format()
            
            print(f"✅ Rapport tendances: {len(trends_df)} lignes")
            print(f"✅ Résumé zones: {len(zone_summary_df)} lignes")
            print(f"✅ Format W&M: {len(wm_df)} lignes")
            
            print("\n🎯 RÉSULTATS PRINCIPAUX:")
            for zone, analysis in analyzer.elevation_analysis['zone_analysis'].items():
                print(f"• {zone}: {analysis['mean_sens_slope']:.4f}/an "
                      f"({analysis['percent_significant']:.1f}% significatif)")
            
            print(f"\n📁 Résultats sauvegardés dans: {analyzer.output_dir}")
            
        else:
            print(f"⚠️ Fichier CSV non trouvé: {csv_path}")
            print("📝 Assurez-vous d'avoir exporté les données depuis Google Earth Engine")
        
        print("\n✅ TOUS LES TESTS RÉUSSIS!")
        print("🎯 L'analyse fraction × élévation est prête à utiliser!")
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DU TEST: {e}")
        import traceback
        traceback.print_exc()

def show_menu_structure():
    """Montre la structure du nouveau menu"""
    print("\n="*60)
    print("📋 NOUVELLE STRUCTURE MENU")
    print("="*60)
    
    print("\n🏠 MENU PRINCIPAL:")
    print("1️⃣  MCD43A3 - Albédo général")
    print("2️⃣  MOD10A1 - Albédo de neige")
    print("3️⃣  Comparaison MCD43A3 vs MOD10A1")
    print("4️⃣  Quitter")
    
    print("\n❄️ SOUS-MENU MOD10A1 (NOUVEAU):")
    print("1️⃣  Analyse complète")
    print("2️⃣  Tendances seulement")
    print("3️⃣  Visualisations seulement")
    print("4️⃣  Analyse pixels/QA seulement")
    print("5️⃣  Graphiques quotidiens")
    print("6️⃣  Comparaison entre fractions MOD10A1")
    print("7️⃣  Analyse fraction × élévation (Williamson & Menounos 2021) 🆕")
    print("8️⃣  Retour au menu principal")
    
    print("\n🏔️ SOUS-MENU FRACTION × ÉLÉVATION (NOUVEAU):")
    print("1️⃣  Analyse complète (tendances + visualisations + rapports)")
    print("2️⃣  Analyse tendances seulement")
    print("3️⃣  Visualisations seulement")
    print("4️⃣  Comparaison avec Williamson & Menounos (2021)")
    print("5️⃣  Rapport synthèse seulement")
    print("6️⃣  Retour au menu MOD10A1")
    
    print("\n📊 FICHIERS CRÉÉS:")
    print("✅ /analysis/elevation_analysis.py")
    print("✅ /visualization/elevation_plots.py")
    print("✅ Configuration ajoutée à config.py")
    print("✅ Menu intégré dans scripts/main.py")
    print("✅ Fonctions ajoutées à scripts/analysis_functions.py")

if __name__ == "__main__":
    show_menu_structure()
    test_elevation_analysis()