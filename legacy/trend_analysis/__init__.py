"""
Saskatchewan Glacier Albedo Trend Analysis Package
=================================================

Ce package contient tous les outils d'analyse statistique pour les données d'albédo 
du glacier Saskatchewan, incluant les tests de Mann-Kendall, pentes de Sen, 
analyses saisonnières, contrôle d'autocorrélation et bootstrap.

Modules:
    config: Configuration et constantes
    data_loader: Chargement et préparation des données
    basic_trends: Tests Mann-Kendall et Sen's slope de base
    advanced_analysis: Analyses avancées (autocorrélation, bootstrap)
    seasonal_analysis: Analyses saisonnières et mensuelles
    spatial_analysis: Cartographie des pentes
    visualizations: Graphiques et visualisations
    exports: Exports Excel et texte
    utils: Fonctions utilitaires

Usage:
    from trend_analysis.main import run_complete_analysis
    run_complete_analysis('your_data.csv')
"""

__version__ = "2.0.0"
__author__ = "Claude Code Analysis"

# Imports principaux pour faciliter l'usage
try:
    from .main import run_complete_analysis, run_quick_analysis, analyze_single_fraction
    from .data_loader import SaskatchewanDataLoader
    from .basic_trends import BasicTrendAnalyzer
    from .advanced_analysis import AdvancedAnalyzer
    from .seasonal_analysis import SeasonalAnalyzer
    from .spatial_analysis import SpatialAnalyzer
    from .visualizations import AlbedoVisualizer
    from .exports import ResultsExporter
    
    __all__ = [
        'run_complete_analysis',
        'run_quick_analysis', 
        'analyze_single_fraction',
        'SaskatchewanDataLoader',
        'BasicTrendAnalyzer', 
        'AdvancedAnalyzer',
        'SeasonalAnalyzer',
        'SpatialAnalyzer',
        'AlbedoVisualizer',
        'ResultsExporter'
    ]
except ImportError as e:
    print(f"⚠️  Erreur d'import dans le package trend_analysis: {e}")
    print("Vérifiez que toutes les dépendances sont installées")
    __all__ = []