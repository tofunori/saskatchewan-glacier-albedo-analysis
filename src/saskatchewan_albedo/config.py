"""
Configuration pour l'analyse des tendances d'albédo du glacier Saskatchewan
=========================================================================

Ce fichier contient toutes les configurations et constantes utilisées
dans l'analyse autonome des tendances d'albédo.
"""

import matplotlib.pyplot as plt
import seaborn as sns

# Configuration des graphiques
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# ==========================================
# CONFIGURATION PRINCIPALE
# ==========================================

# Choix du dataset par défaut ('MCD43A3', 'MOD10A1', ou 'COMPARISON')
DEFAULT_DATASET = "MCD43A3"

# Configuration pour MCD43A3 (Albédo général)
MCD43A3_CONFIG = {
    'csv_path': r"D:\UQTR\Maitrîse\Code\saskatchewan-glacier-albedo-analysis\data\csv\daily_albedo_mann_kendall_ready_2010_2024.csv",
    'qa_csv_path': r"D:\UQTR\Maitrîse\Code\saskatchewan-glacier-albedo-analysis\data\csv\global_quality_distribution_daily_2010_2024.csv",
    'name': 'MCD43A3',
    'description': 'Albédo général (MODIS Combined)',
    'quality_levels': ['quality_0_best', 'quality_1_good', 'quality_2_moderate', 'quality_3_poor'],
    'temporal_resolution': '16-day composite',
    'scaling_info': 'Scale factor: 0.001'
}

# Configuration pour MOD10A1 (Albédo de neige)
MOD10A1_CONFIG = {
    'csv_path': r"D:\UQTR\Maitrîse\Code\saskatchewan-glacier-albedo-analysis\data\csv\daily_snow_albedo_mann_kendall_mod10a1_2010_2024.csv",
    'qa_csv_path': r"D:\UQTR\Maitrîse\Code\saskatchewan-glacier-albedo-analysis\data\csv\snow_quality_distribution_daily_mod10a1_2010_2024.csv",
    'name': 'MOD10A1',
    'description': 'Albédo de neige (Terra Snow Cover)',
    'quality_levels': ['quality_0_best', 'quality_1_good', 'quality_2_ok', 'quality_other_night_ocean'],
    'temporal_resolution': 'Daily',
    'scaling_info': 'Percentage (1-100) to decimal (÷100)'
}

# Configuration pour les comparaisons
COMPARISON_CONFIG = {
    'output_suffix': '_comparison',
    'correlation_threshold': 0.7,
    'significance_level': 0.05,
    'difference_threshold': 0.1,  # Seuil pour les différences significatives d'albédo
    'sync_tolerance_days': 1,     # Tolérance pour synchroniser les dates
}

# Variables de compatibilité (pour maintenir le code existant)
CSV_PATH = MCD43A3_CONFIG['csv_path']  # Par défaut
QA_CSV_PATH = MCD43A3_CONFIG['qa_csv_path']  # Par défaut

# Répertoire de sortie pour les résultats
OUTPUT_DIR = "results"

# Variable à analyser ('mean' ou 'median')
ANALYSIS_VARIABLE = "mean"

# ==========================================
# FRACTIONS DE COUVERTURE GLACIAIRE
# ==========================================

# Classes de fractions analysées
FRACTION_CLASSES = ['border', 'mixed_low', 'mixed_high', 'mostly_ice', 'pure_ice']

# Labels complets pour les fractions
CLASS_LABELS = {
    'border': '0-25% (Bordure)',
    'mixed_low': '25-50% (Mixte bas)',
    'mixed_high': '50-75% (Mixte haut)',
    'mostly_ice': '75-90% (Majoritaire)',
    'pure_ice': '90-100% (Pur)'
}

# Couleurs pour les visualisations
FRACTION_COLORS = {
    'border': 'red',
    'mixed_low': 'orange', 
    'mixed_high': 'gold',
    'mostly_ice': 'lightblue',
    'pure_ice': 'blue'
}

# ==========================================
# PARAMÈTRES D'ANALYSE STATISTIQUE
# ==========================================

# Configuration des analyses
ANALYSIS_CONFIG = {
    'bootstrap_iterations': 1000,
    'min_observations': 10,
    'significance_levels': [0.001, 0.01, 0.05],
    'autocorr_thresholds': {
        'weak': 0.1,
        'moderate': 0.3,
        'strong': 0.5
    },
    'quality_threshold': 10  # Minimum pixels pour analyse fiable
}

# Configuration des exports
EXPORT_CONFIG = {
    'excel_max_rows': 1000,  # Limite pour éviter fichiers trop gros
    'image_dpi': 300,
    'figure_format': 'png'
}

# ==========================================
# SYMBOLES ET MARQUEURS
# ==========================================

# Symboles pour les tendances
TREND_SYMBOLS = {
    'increasing': '📈',
    'decreasing': '📉', 
    'no trend': '➡️'
}

# Marqueurs de significativité
SIGNIFICANCE_MARKERS = {
    0.001: '***',
    0.01: '**',
    0.05: '*',
    1.0: 'ns'
}

# Noms des mois
MONTH_NAMES = {
    6: 'Juin',
    7: 'Juillet', 
    8: 'Août',
    9: 'Septembre'
}

# ==========================================
# STYLES DE GRAPHIQUES
# ==========================================

# Configuration des couleurs pour les graphiques
QUALITY_COLORS = ['#2166ac', '#92c5de', '#fddbc7', '#d6604d']

# Styles de graphiques
PLOT_STYLES = {
    'trend_line': {'linewidth': 2, 'alpha': 0.8},
    'scatter': {'alpha': 0.6, 's': 20},
    'error_bars': {'ecolor': 'black', 'capsize': 5},
    'significance_text': {'fontweight': 'bold', 'ha': 'center', 'va': 'bottom'}
}

# ==========================================
# CONFIGURATION POUR L'ANALYSE DES PIXELS
# ==========================================

# Seuils de qualité des données
QA_THRESHOLDS = {
    'high_quality': 80,      # Seuil pour haute qualité (%)
    'medium_quality': 60,    # Seuil pour qualité moyenne (%)
    'low_quality': 0         # En dessous = faible qualité
}

# Configuration des visualisations de pixels
PIXEL_PLOT_CONFIG = {
    'heatmap_colormap': 'RdYlGn',
    'qa_colormap': 'RdYlGn',
    'pixel_count_colors': ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00'],
    'availability_colormap': 'viridis'
}

# Styles spécifiques pour les graphiques de pixels
PIXEL_PLOT_STYLES = {
    'heatmap': {'annot': True, 'fmt': '.1f', 'cbar_kws': {'shrink': 0.8}},
    'timeseries': {'linewidth': 1.5, 'alpha': 0.7},
    'bar_charts': {'alpha': 0.8, 'edgecolor': 'black', 'linewidth': 0.5}
}

# ==========================================
# FONCTIONS UTILITAIRES DE CONFIGURATION
# ==========================================

def get_significance_marker(p_value):
    """
    Retourne le marqueur de significativité selon la p-value
    
    Args:
        p_value (float): P-value du test statistique
        
    Returns:
        str: Marqueur de significativité (***/**/**/ns)
    """
    for threshold, marker in SIGNIFICANCE_MARKERS.items():
        if p_value < threshold:
            return marker
    return SIGNIFICANCE_MARKERS[1.0]

def get_autocorr_status(autocorr_value):
    """
    Retourne le statut d'autocorrélation avec emoji
    
    Args:
        autocorr_value (float): Valeur d'autocorrélation lag-1
        
    Returns:
        str: Statut avec emoji (🔴 Forte, 🟡 Modérée, 🟢 Faible)
    """
    abs_autocorr = abs(autocorr_value)
    
    if abs_autocorr > ANALYSIS_CONFIG['autocorr_thresholds']['strong']:
        return "🔴 Très forte"
    elif abs_autocorr > ANALYSIS_CONFIG['autocorr_thresholds']['moderate']:
        return "🔴 Forte" 
    elif abs_autocorr > ANALYSIS_CONFIG['autocorr_thresholds']['weak']:
        return "🟡 Modérée"
    else:
        return "🟢 Faible"

def get_dataset_config(dataset_name):
    """
    Retourne la configuration pour un dataset spécifique
    
    Args:
        dataset_name (str): 'MCD43A3' ou 'MOD10A1'
        
    Returns:
        dict: Configuration du dataset
    """
    if dataset_name == 'MCD43A3':
        return MCD43A3_CONFIG
    elif dataset_name == 'MOD10A1':
        return MOD10A1_CONFIG
    else:
        raise ValueError(f"Dataset inconnu: {dataset_name}. Utilisez 'MCD43A3' ou 'MOD10A1'")

def get_available_datasets():
    """
    Retourne la liste des datasets disponibles avec leurs informations
    
    Returns:
        dict: Informations sur les datasets disponibles
    """
    import os
    
    datasets = {}
    for name, config in [('MCD43A3', MCD43A3_CONFIG), ('MOD10A1', MOD10A1_CONFIG)]:
        datasets[name] = {
            'config': config,
            'csv_exists': os.path.exists(config['csv_path']),
            'qa_exists': os.path.exists(config['qa_csv_path']) if config['qa_csv_path'] else False
        }
    
    return datasets

def print_config_summary(dataset_name=None):
    """
    Affiche un résumé de la configuration
    
    Args:
        dataset_name (str, optional): Dataset spécifique à afficher
    """
    if dataset_name:
        config = get_dataset_config(dataset_name)
        print(f"⚙️  CONFIGURATION - {config['name']}")
        print("="*50)
        print(f"📊 Dataset: {config['description']}")
        print(f"📊 Fichier CSV: {config['csv_path']}")
        print(f"📊 Fichier QA: {config['qa_csv_path']}")
        print(f"⏱️  Résolution temporelle: {config['temporal_resolution']}")
        print(f"📏 Échelle: {config['scaling_info']}")
        print(f"🔍 Variable analysée: {ANALYSIS_VARIABLE}")
        print(f"📊 Fractions: {len(FRACTION_CLASSES)} classes")
        print("="*50)
    else:
        print("⚙️  CONFIGURATION GÉNÉRALE")
        print("="*50)
        print(f"📊 Dataset par défaut: {DEFAULT_DATASET}")
        print(f"📁 Répertoire de sortie: {OUTPUT_DIR}")
        print(f"🔍 Variable analysée: {ANALYSIS_VARIABLE}")
        print(f"📊 Fractions: {len(FRACTION_CLASSES)} classes")
        print(f"🔄 Bootstrap: {ANALYSIS_CONFIG['bootstrap_iterations']} itérations")
        print(f"📈 Seuils significativité: {ANALYSIS_CONFIG['significance_levels']}")
        
        # Afficher la disponibilité des datasets
        print(f"\n📊 DATASETS DISPONIBLES:")
        datasets = get_available_datasets()
        for name, info in datasets.items():
            status = "✅" if info['csv_exists'] else "❌"
            qa_status = "✅" if info['qa_exists'] else "❌"
            print(f"  {status} {name}: {info['config']['description']}")
            print(f"    QA: {qa_status}")
        print("="*50)

def print_comparison_info():
    """
    Affiche les informations sur les capacités de comparaison
    """
    print("🔄 CONFIGURATION COMPARAISON")
    print("="*50)
    print(f"🎯 Seuil de corrélation: {COMPARISON_CONFIG['correlation_threshold']}")
    print(f"📊 Niveau de significativité: {COMPARISON_CONFIG['significance_level']}")
    print(f"📏 Seuil différence albédo: {COMPARISON_CONFIG['difference_threshold']}")
    print(f"⏱️  Tolérance synchronisation: {COMPARISON_CONFIG['sync_tolerance_days']} jour(s)")
    print("="*50)