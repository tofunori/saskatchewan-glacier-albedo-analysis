#!/usr/bin/env python3
"""
Interface de menu interactive pour l'analyse d'albédo du glacier Saskatchewan
========================================================================

Menu interactif bilingue pour toutes les fonctionnalités du projet,
incluant la nouvelle intégration Google Earth Engine.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Setup path
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))

def clear_screen():
    """Efface l'écran"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Affiche l'en-tête principal"""
    print("🏔️  SASKATCHEWAN GLACIER ALBEDO ANALYSIS")
    print("=" * 60)
    print("📅 Session:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("📍 Analyse d'évolution de l'albédo 2010-2024")
    print("=" * 60)

def print_main_menu():
    """Affiche le menu principal"""
    print("\n🎯 MENU PRINCIPAL / MAIN MENU")
    print("-" * 40)
    print("1. 📊 Analyse complète automatisée")
    print("   Complete automated analysis")
    print()
    print("2. 📡 Récupérer données fraîches (Google Earth Engine)")
    print("   Fetch fresh data from GEE")
    print()
    print("3. 📈 Analyse de tendances personnalisée")
    print("   Custom trend analysis")
    print()
    print("4. 🎨 Génération de graphiques")
    print("   Generate visualizations")
    print()
    print("5. 📋 Informations sur les données")
    print("   Data information")
    print()
    print("6. ⚙️  Configuration et tests")
    print("   Configuration and tests")
    print()
    print("0. 🚪 Quitter / Exit")
    print("-" * 40)

def run_complete_analysis():
    """Lance l'analyse complète automatisée"""
    print("\n🚀 LANCEMENT DE L'ANALYSE COMPLÈTE")
    print("=" * 50)
    
    try:
        from main import main
        success = main()
        
        if success:
            print("\n✅ Analyse terminée avec succès!")
            input("\n📱 Appuyez sur Entrée pour continuer...")
        else:
            print("\n❌ Erreur lors de l'analyse")
            input("\n📱 Appuyez sur Entrée pour continuer...")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        input("\n📱 Appuyez sur Entrée pour continuer...")

def gee_data_menu():
    """Menu pour récupération de données GEE"""
    while True:
        clear_screen()
        print_header()
        print("\n🛰️  GOOGLE EARTH ENGINE - DONNÉES FRAÎCHES")
        print("=" * 50)
        print("1. 🔐 Tester la connexion GEE")
        print("   Test GEE connection")
        print()
        print("2. 📊 Récupérer données d'albédo MODIS")
        print("   Fetch MODIS albedo data")
        print()
        print("3. ❄️  Récupérer données de couverture neigeuse")
        print("   Fetch snow cover data")
        print()
        print("4. 🔗 Récupérer données combinées (albédo + neige)")
        print("   Fetch combined dataset")
        print()
        print("5. 📋 Statut des données GEE")
        print("   GEE data status")
        print()
        print("0. ⬅️  Retour au menu principal")
        print("-" * 50)
        
        choice = input("\n🎯 Votre choix (0-5): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            test_gee_connection()
        elif choice == "2":
            fetch_albedo_data()
        elif choice == "3":
            fetch_snow_cover_data()
        elif choice == "4":
            fetch_combined_data()
        elif choice == "5":
            show_gee_status()
        else:
            print("❌ Choix invalide")
            input("📱 Appuyez sur Entrée pour continuer...")

def test_gee_connection():
    """Teste la connexion Google Earth Engine"""
    print("\n🔐 TEST DE CONNEXION GOOGLE EARTH ENGINE")
    print("=" * 50)
    
    try:
        from gee.client import GEEClient
        
        # Check installation first
        install_info = GEEClient.check_installation()
        
        if not install_info['installed']:
            print("❌ Google Earth Engine non installé")
            print(f"💡 Commande d'installation: {install_info['install_command']}")
            input("\n📱 Appuyez sur Entrée pour continuer...")
            return
        
        print(f"✅ Earth Engine installé (version: {install_info.get('version', 'unknown')})")
        print("\n🔄 Tentative d'authentification...")
        
        client = GEEClient()
        if client.authenticate():
            print("✅ Authentification réussie!")
            
            # Test connection
            test_result = client.test_connection()
            
            if test_result['status'] == 'success':
                print("✅ Connexion GEE testée avec succès")
                print(f"📊 Collection de test: {test_result['test_collection']}")
                print(f"📈 Taille de la collection: {test_result['collection_size']}")
            else:
                print(f"❌ Test de connexion échoué: {test_result['message']}")
        else:
            print("❌ Échec de l'authentification")
            print("💡 Essayez 'earthengine authenticate' depuis la ligne de commande")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    input("\n📱 Appuyez sur Entrée pour continuer...")

def fetch_albedo_data():
    """Interface pour récupérer les données d'albédo"""
    print("\n📊 RÉCUPÉRATION DONNÉES ALBÉDO MODIS")
    print("=" * 50)
    
    try:
        # Get date range
        print("📅 Période de données à récupérer:")
        print("1. 🚀 Dernière année (recommandé)")
        print("2. 📈 5 dernières années")
        print("3. 🎯 Période personnalisée")
        
        date_choice = input("\nChoix (1-3): ").strip()
        
        # Set date range based on choice
        end_date = datetime.now()
        
        if date_choice == "1":
            start_date = end_date - timedelta(days=365)
        elif date_choice == "2":
            start_date = end_date - timedelta(days=5*365)
        elif date_choice == "3":
            start_str = input("Date de début (YYYY-MM-DD): ").strip()
            end_str = input("Date de fin (YYYY-MM-DD): ").strip()
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_str, "%Y-%m-%d")
        else:
            print("❌ Choix invalide")
            input("📱 Appuyez sur Entrée pour continuer...")
            return
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        print(f"\n🗓️  Période sélectionnée: {start_str} à {end_str}")
        print("🔄 Récupération en cours...")
        
        from gee.client import GEEClient
        from gee.saskatchewan import SaskatchewanMODISFetcher
        from gee.exporter import DataExporter
        
        # Initialize GEE client
        client = GEEClient()
        if not client.authenticate():
            print("❌ Impossible de s'authentifier avec GEE")
            input("📱 Appuyez sur Entrée pour continuer...")
            return
        
        # Fetch data
        fetcher = SaskatchewanMODISFetcher(client, region='glacier')
        data = fetcher.fetch_albedo_data(start_str, end_str)
        
        if data.empty:
            print("⚠️  Aucune donnée récupérée pour cette période")
        else:
            print(f"✅ {len(data)} observations récupérées")
            
            # Export to CSV
            exporter = DataExporter()
            csv_path = exporter.export_albedo_to_csv(data)
            
            print(f"💾 Données exportées: {csv_path}")
            
            # Show summary
            summary = exporter.get_export_summary(csv_path)
            print(f"📊 Fichier: {summary['file_size_mb']} MB")
            print(f"📅 Période: {summary['date_range']['start']} - {summary['date_range']['end']}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération: {e}")
    
    input("\n📱 Appuyez sur Entrée pour continuer...")

def fetch_snow_cover_data():
    """Interface pour récupérer les données de couverture neigeuse"""
    print("\n❄️  RÉCUPÉRATION DONNÉES COUVERTURE NEIGEUSE")
    print("=" * 50)
    
    try:
        # Use same date selection as albedo
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)  # Last year
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        print(f"🗓️  Période: {start_str} à {end_str}")
        print("🔄 Récupération en cours...")
        
        from gee.client import GEEClient
        from gee.saskatchewan import SaskatchewanMODISFetcher
        from gee.exporter import DataExporter
        
        # Initialize and fetch
        client = GEEClient()
        if not client.authenticate():
            print("❌ Impossible de s'authentifier avec GEE")
            input("📱 Appuyez sur Entrée pour continuer...")
            return
        
        fetcher = SaskatchewanMODISFetcher(client, region='glacier')
        data = fetcher.fetch_snow_cover_data(start_str, end_str)
        
        if data.empty:
            print("⚠️  Aucune donnée de neige récupérée")
        else:
            print(f"✅ {len(data)} observations de neige récupérées")
            
            # Export
            exporter = DataExporter()
            csv_path = exporter.export_snow_cover_to_csv(data)
            print(f"💾 Données exportées: {csv_path}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    input("\n📱 Appuyez sur Entrée pour continuer...")

def fetch_combined_data():
    """Interface pour récupérer les données combinées"""
    print("\n🔗 RÉCUPÉRATION DONNÉES COMBINÉES")
    print("=" * 50)
    print("Cette option récupère à la fois l'albédo et la couverture neigeuse")
    print("et les combine en un seul fichier CSV.")
    
    try:
        # Date selection
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)  # 6 months for combined data
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        print(f"\n🗓️  Période: {start_str} à {end_str}")
        print("🔄 Récupération des données d'albédo...")
        
        from gee.client import GEEClient
        from gee.saskatchewan import SaskatchewanMODISFetcher
        from gee.exporter import DataExporter
        
        client = GEEClient()
        if not client.authenticate():
            print("❌ Impossible de s'authentifier avec GEE")
            input("📱 Appuyez sur Entrée pour continuer...")
            return
        
        fetcher = SaskatchewanMODISFetcher(client, region='glacier')
        
        # Fetch albedo data
        albedo_data = fetcher.fetch_albedo_data(start_str, end_str)
        print(f"✅ Albédo: {len(albedo_data)} observations")
        
        # Fetch snow data
        print("🔄 Récupération des données de neige...")
        snow_data = fetcher.fetch_snow_cover_data(start_str, end_str)
        print(f"✅ Neige: {len(snow_data)} observations")
        
        # Combine and export
        exporter = DataExporter()
        csv_path = exporter.create_combined_dataset(albedo_data, snow_data)
        
        print(f"\n💾 Dataset combiné exporté: {csv_path}")
        
        summary = exporter.get_export_summary(csv_path)
        print(f"📊 Fichier: {summary['file_size_mb']} MB")
        print(f"📈 Records: {summary['total_records']}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    input("\n📱 Appuyez sur Entrée pour continuer...")

def show_gee_status():
    """Affiche le statut des données GEE"""
    print("\n📋 STATUT DONNÉES GOOGLE EARTH ENGINE")
    print("=" * 50)
    
    try:
        from gee.client import GEEClient
        
        # Check installation
        install_info = GEEClient.check_installation()
        print(f"🔧 Installation GEE: {'✅' if install_info['installed'] else '❌'}")
        
        if install_info['installed']:
            print(f"📦 Version: {install_info.get('version', 'unknown')}")
            
            # Check authentication
            client = GEEClient()
            if client.authenticate():
                print("🔐 Authentification: ✅")
                
                # Test region info
                from gee.saskatchewan import SaskatchewanMODISFetcher
                fetcher = SaskatchewanMODISFetcher(client, region='glacier')
                region_info = fetcher.get_region_info()
                
                print(f"\n📍 Région configurée:")
                print(f"   🌍 Zone: Glacier Saskatchewan")
                print(f"   📐 Superficie: {region_info['area_km2']} km²")
                print(f"   📊 Coordonnées: {region_info['coordinates']}")
                
            else:
                print("🔐 Authentification: ❌")
        
        # Check for existing GEE data files
        print(f"\n📁 Fichiers GEE existants:")
        gee_files = list(Path('.').glob('**/gee_*.csv'))
        
        if gee_files:
            for file_path in gee_files[:5]:  # Show up to 5 files
                stat = file_path.stat()
                size_mb = stat.st_size / (1024 * 1024)
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                print(f"   📄 {file_path.name} ({size_mb:.1f} MB, {mod_time.strftime('%Y-%m-%d %H:%M')})")
        else:
            print("   📭 Aucun fichier GEE trouvé")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    input("\n📱 Appuyez sur Entrée pour continuer...")

def custom_analysis_menu():
    """Menu pour analyse personnalisée"""
    print("\n📈 ANALYSE DE TENDANCES PERSONNALISÉE")
    print("=" * 50)
    print("Fonctionnalité à venir...")
    input("\n📱 Appuyez sur Entrée pour continuer...")

def visualization_menu():
    """Menu pour génération de graphiques"""
    print("\n🎨 GÉNÉRATION DE GRAPHIQUES")
    print("=" * 50)
    print("Fonctionnalité à venir...")
    input("\n📱 Appuyez sur Entrée pour continuer...")

def data_info_menu():
    """Menu d'informations sur les données"""
    print("\n📋 INFORMATIONS SUR LES DONNÉES")
    print("=" * 50)
    
    try:
        from config import CSV_PATH, FRACTION_CLASSES
        from data_handler import AlbedoDataHandler
        
        if os.path.exists(CSV_PATH):
            print(f"✅ Fichier CSV principal: {CSV_PATH}")
            
            handler = AlbedoDataHandler(CSV_PATH)
            handler.load_data()
            handler.print_data_summary()
            
        else:
            print(f"❌ Fichier CSV non trouvé: {CSV_PATH}")
        
        print(f"\n📊 Classes de fraction configurées: {len(FRACTION_CLASSES)}")
        for i, fraction in enumerate(FRACTION_CLASSES, 1):
            print(f"   {i}. {fraction}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    input("\n📱 Appuyez sur Entrée pour continuer...")

def config_menu():
    """Menu de configuration et tests"""
    print("\n⚙️  CONFIGURATION ET TESTS")
    print("=" * 50)
    
    try:
        from config import print_config_summary
        print_config_summary()
        
        print("\n🧪 Test des modules...")
        from main import test_imports
        test_imports()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    input("\n📱 Appuyez sur Entrée pour continuer...")

def main_interactive_loop():
    """Boucle principale du menu interactif"""
    while True:
        clear_screen()
        print_header()
        print_main_menu()
        
        choice = input("🎯 Votre choix (0-6): ").strip()
        
        if choice == "0":
            print("\n👋 Au revoir! Goodbye!")
            break
        elif choice == "1":
            run_complete_analysis()
        elif choice == "2":
            gee_data_menu()
        elif choice == "3":
            custom_analysis_menu()
        elif choice == "4":
            visualization_menu()
        elif choice == "5":
            data_info_menu()
        elif choice == "6":
            config_menu()
        else:
            print("❌ Choix invalide / Invalid choice")
            input("📱 Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    try:
        main_interactive_loop()
    except KeyboardInterrupt:
        print("\n\n👋 Interruption utilisateur. Au revoir!")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()