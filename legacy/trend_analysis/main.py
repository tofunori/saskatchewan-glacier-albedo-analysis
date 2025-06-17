"""
Point d'entrée principal pour l'analyse complète des tendances d'albédo
=====================================================================

Ce module orchestre toutes les analyses et génère les rapports finaux
pour l'étude des tendances d'albédo du glacier Saskatchewan.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Gérer les imports relatifs et absolus
try:
    # Import relatif (quand utilisé comme module)
    from .data_loader import SaskatchewanDataLoader
    from .basic_trends import BasicTrendAnalyzer
    from .seasonal_analysis import SeasonalAnalyzer
    from .visualizations import AlbedoVisualizer
    from .utils import print_section_header, ensure_directory_exists
except ImportError:
    # Import absolu (quand exécuté directement)
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    from data_loader import SaskatchewanDataLoader
    from basic_trends import BasicTrendAnalyzer
    from seasonal_analysis import SeasonalAnalyzer
    from visualizations import AlbedoVisualizer
    from utils import print_section_header, ensure_directory_exists

def run_complete_analysis(csv_path, output_dir='analysis_output', variable='mean'):
    """
    Exécute l'analyse complète des tendances d'albédo
    
    Args:
        csv_path (str): Chemin vers le fichier CSV des données
        output_dir (str): Répertoire de sortie pour les résultats
        variable (str): Variable à analyser ('mean' ou 'median')
        
    Returns:
        dict: Résultats complets de l'analyse
    """
    print_section_header("ANALYSE COMPLÈTE DES TENDANCES D'ALBÉDO", level=1)
    print(f"📊 Fichier d'entrée: {csv_path}")
    print(f"📁 Répertoire de sortie: {output_dir}")
    print(f"🔍 Variable analysée: {variable}")
    
    # Créer le répertoire de sortie
    ensure_directory_exists(os.path.join(output_dir, 'temp'))
    
    # ÉTAPE 1: Chargement des données
    print_section_header("ÉTAPE 1: Chargement et préparation des données", level=1)
    
    try:
        data_loader = SaskatchewanDataLoader(csv_path)
        data_loader.load_data()
        data_loader.print_data_summary()
    except Exception as e:
        print(f"❌ Erreur lors du chargement des données: {e}")
        return None
    
    # ÉTAPE 2: Analyses de tendances de base
    print_section_header("ÉTAPE 2: Analyses de tendances de base", level=1)
    
    try:
        basic_analyzer = BasicTrendAnalyzer(data_loader)
        basic_results = basic_analyzer.calculate_trends(variable)
        basic_analyzer.print_summary(variable)
        
        # Sauvegarder le tableau de résumé de base
        summary_table = basic_analyzer.get_summary_table(variable)
        summary_path = os.path.join(output_dir, f'basic_trends_summary_{variable}.csv')
        summary_table.to_csv(summary_path, index=False)
        print(f"✓ Tableau de résumé sauvegardé: {summary_path}")
        
    except Exception as e:
        print(f"❌ Erreur lors des analyses de base: {e}")
        return None
    
    # ÉTAPE 3: Analyses saisonnières et mensuelles
    print_section_header("ÉTAPE 3: Analyses saisonnières et mensuelles", level=1)
    
    try:
        seasonal_analyzer = SeasonalAnalyzer(data_loader)
        monthly_results = seasonal_analyzer.analyze_monthly_trends(variable)
        seasonal_analyzer.print_seasonal_summary(variable)
        
        # Créer les graphiques de statistiques mensuelles demandés
        monthly_graph_path = seasonal_analyzer.create_monthly_statistics_graphs(
            variable, os.path.join(output_dir, f'monthly_statistics_{variable}.png')
        )
        
        # Graphique de comparaison saisonnière
        seasonal_graph_path = seasonal_analyzer.create_seasonal_comparison_graph(
            variable, os.path.join(output_dir, f'seasonal_comparison_{variable}.png')
        )
        
        # Sauvegarder le tableau mensuel
        monthly_table = seasonal_analyzer.get_monthly_summary_table(variable)
        monthly_path = os.path.join(output_dir, f'monthly_trends_summary_{variable}.csv')
        monthly_table.to_csv(monthly_path, index=False)
        print(f"✓ Tableau mensuel sauvegardé: {monthly_path}")
        
    except Exception as e:
        print(f"❌ Erreur lors des analyses saisonnières: {e}")
        monthly_results = {}
    
    # ÉTAPE 4: Visualisations principales
    print_section_header("ÉTAPE 4: Création des visualisations", level=1)
    
    try:
        visualizer = AlbedoVisualizer(data_loader)
        
        # Graphique d'aperçu des tendances
        overview_path = visualizer.create_trend_overview_graph(
            basic_results, variable, os.path.join(output_dir, f'trend_overview_{variable}.png')
        )
        
        # Matrice de corrélation
        correlation_path = visualizer.create_correlation_matrix_graph(
            variable, os.path.join(output_dir, f'correlation_matrix_{variable}.png')
        )
        
        # Patterns saisonniers
        patterns_path = visualizer.create_seasonal_patterns_graph(
            variable, os.path.join(output_dir, f'seasonal_patterns_{variable}.png')
        )
        
        # Dashboard de résumé
        dashboard_path = visualizer.create_summary_dashboard(
            basic_results, variable, os.path.join(output_dir, f'dashboard_summary_{variable}.png')
        )
        
        # Séries temporelles détaillées pour chaque fraction
        timeseries_paths = []
        for fraction in data_loader.fraction_classes:
            try:
                ts_path = visualizer.create_time_series_graph(
                    fraction, variable, 
                    os.path.join(output_dir, f'timeseries_{fraction}_{variable}.png')
                )
                if ts_path:
                    timeseries_paths.append(ts_path)
            except Exception as e:
                print(f"⚠️  Impossible de créer la série temporelle pour {fraction}: {e}")
        
    except Exception as e:
        print(f"❌ Erreur lors des visualisations: {e}")
        overview_path = None
    
    # ÉTAPE 5: Compilation des résultats
    print_section_header("ÉTAPE 5: Compilation des résultats finaux", level=1)
    
    results = {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'csv_path': csv_path,
            'output_dir': output_dir,
            'variable': variable,
            'data_summary': data_loader.get_data_summary()
        },
        'basic_trends': basic_results,
        'monthly_trends': monthly_results,
        'files_generated': []
    }
    
    # Lister tous les fichiers générés
    generated_files = [
        ('Résumé tendances de base', summary_path if 'summary_path' in locals() else None),
        ('Résumé tendances mensuelles', monthly_path if 'monthly_path' in locals() else None),
        ('Graphiques statistiques mensuelles', monthly_graph_path if 'monthly_graph_path' in locals() else None),
        ('Comparaison saisonnière', seasonal_graph_path if 'seasonal_graph_path' in locals() else None),
        ('Aperçu des tendances', overview_path if 'overview_path' in locals() else None),
        ('Matrice de corrélation', correlation_path if 'correlation_path' in locals() else None),
        ('Patterns saisonniers', patterns_path if 'patterns_path' in locals() else None),
        ('Dashboard résumé', dashboard_path if 'dashboard_path' in locals() else None)
    ]
    
    # Ajouter les séries temporelles
    if 'timeseries_paths' in locals():
        for i, ts_path in enumerate(timeseries_paths):
            generated_files.append((f'Série temporelle {i+1}', ts_path))
    
    # Filtrer les fichiers existants et afficher
    print("📁 Fichiers générés:")
    for description, file_path in generated_files:
        if file_path and os.path.exists(file_path):
            print(f"  ✓ {description}: {file_path}")
            results['files_generated'].append({
                'description': description,
                'path': file_path,
                'size_kb': round(os.path.getsize(file_path) / 1024, 1)
            })
        elif file_path:
            print(f"  ❌ {description}: {file_path} (introuvable)")
    
    # Résumé final
    print_section_header("ANALYSE TERMINÉE", level=1)
    print(f"✅ Analyse complète terminée avec succès")
    print(f"📊 Variable analysée: {variable}")
    print(f"📁 {len(results['files_generated'])} fichiers générés dans: {output_dir}")
    print(f"⏱️  Durée totale: {datetime.now().strftime('%H:%M:%S')}")
    
    # Afficher un résumé des tendances significatives
    significant_trends = []
    for fraction, result in basic_results.items():
        if not result.get('error', False):
            mk = result['mann_kendall']
            if mk['p_value'] < 0.05:
                significant_trends.append(f"  📊 {result['label']}: {mk['trend']} (p={mk['p_value']:.4f})")
    
    if significant_trends:
        print(f"\n🎯 Tendances significatives détectées:")
        for trend in significant_trends:
            print(trend)
    else:
        print(f"\n➡️  Aucune tendance significative détectée au seuil p < 0.05")
    
    return results

def run_quick_analysis(csv_path, variable='mean'):
    """
    Exécute une analyse rapide sans sauvegarder les graphiques
    
    Args:
        csv_path (str): Chemin vers le fichier CSV
        variable (str): Variable à analyser
        
    Returns:
        dict: Résultats de base
    """
    print_section_header("ANALYSE RAPIDE DES TENDANCES D'ALBÉDO", level=1)
    
    # Chargement des données
    data_loader = SaskatchewanDataLoader(csv_path)
    data_loader.load_data()
    
    # Analyses de base seulement
    basic_analyzer = BasicTrendAnalyzer(data_loader)
    basic_results = basic_analyzer.calculate_trends(variable)
    basic_analyzer.print_summary(variable)
    
    return {
        'basic_trends': basic_results,
        'summary_table': basic_analyzer.get_summary_table(variable)
    }

def analyze_single_fraction(csv_path, fraction, variable='mean', save_graphs=False):
    """
    Analyse une seule fraction en détail
    
    Args:
        csv_path (str): Chemin vers le fichier CSV
        fraction (str): Fraction à analyser
        variable (str): Variable à analyser
        save_graphs (bool): Sauvegarder les graphiques
        
    Returns:
        dict: Résultats pour cette fraction
    """
    print_section_header(f"ANALYSE DÉTAILLÉE - {fraction.upper()}", level=1)
    
    # Chargement des données
    data_loader = SaskatchewanDataLoader(csv_path)
    data_loader.load_data()
    
    # Analyse de base
    basic_analyzer = BasicTrendAnalyzer(data_loader)
    basic_results = basic_analyzer.calculate_trends(variable)
    
    if fraction not in basic_results:
        print(f"❌ Fraction {fraction} non trouvée dans les résultats")
        return None
    
    result = basic_results[fraction]
    
    # Affichage détaillé
    print(f"\n📊 Résultats pour {result['label']}:")
    print(f"  • Observations: {result['n_obs']}")
    print(f"  • Tendance: {result['mann_kendall']['trend']}")
    print(f"  • P-value: {result['mann_kendall']['p_value']:.6f}")
    print(f"  • Pente Sen: {result['sen_slope']['slope_per_decade']:.6f}/décennie")
    
    # Graphiques optionnels
    if save_graphs:
        visualizer = AlbedoVisualizer(data_loader)
        ts_path = visualizer.create_time_series_graph(fraction, variable)
        print(f"✓ Série temporelle sauvegardée: {ts_path}")
    
    return result

if __name__ == "__main__":
    # Exemple d'utilisation
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <csv_path> [output_dir] [variable]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'analysis_output'
    variable = sys.argv[3] if len(sys.argv) > 3 else 'mean'
    
    results = run_complete_analysis(csv_path, output_dir, variable)
    
    if results:
        print(f"\n✅ Analyse terminée. Résultats dans: {output_dir}")
    else:
        print(f"\n❌ Échec de l'analyse")
        sys.exit(1)