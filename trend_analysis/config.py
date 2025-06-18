"""
Configuration et constantes pour l'analyse de tendances d'albédo
===============================================================

Ce module contient toutes les configurations, constantes et paramètres
utilisés dans l'analyse des tendances d'albédo du glacier Saskatchewan.
"""

import matplotlib.pyplot as plt
import seaborn as sns

# Configuration des graphiques
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# ==========================================
# STRUCTURE DES RÉPERTOIRES DE SORTIE
# ==========================================

# Répertoire de base pour tous les résultats
OUTPUT_DIR = "../results"

# Structure organisée par produit MODIS et type de données  
OUTPUT_STRUCTURE = {
    'base_dir': '../results',
    'products': {
        'MCD43A3_albedo': {
            'raw_data': '../results/MCD43A3_albedo/raw_data',
            'processed_data': '../results/MCD43A3_albedo/processed_data', 
            'trend_analysis': '../results/MCD43A3_albedo/trend_analysis',
            'figures': '../results/MCD43A3_albedo/figures',
            'reports': '../results/MCD43A3_albedo/reports'
        },
        'MOD10A1_snow_cover': {
            'raw_data': '../results/MOD10A1_snow_cover/raw_data',
            'processed_data': '../results/MOD10A1_snow_cover/processed_data',
            'analysis': '../results/MOD10A1_snow_cover/analysis',
            'figures': '../results/MOD10A1_snow_cover/figures'
        },
        'MYD10A1_aqua_snow': {
            'raw_data': '../results/MYD10A1_aqua_snow/raw_data',  
            'processed_data': '../results/MYD10A1_aqua_snow/processed_data',
            'analysis': '../results/MYD10A1_aqua_snow/analysis',
            'figures': '../results/MYD10A1_aqua_snow/figures'
        },
        'combined_analysis': {
            'multi_product_comparisons': '../results/combined_analysis/multi_product_comparisons',
            'integrated_reports': '../results/combined_analysis/integrated_reports',
            'summary_figures': '../results/combined_analysis/summary_figures'
        },
        'metadata': {
            'processing_logs': '../results/metadata/processing_logs',
            'data_quality_reports': '../results/metadata/data_quality_reports',
            'configuration_snapshots': '../results/metadata/configuration_snapshots'
        }
    }
}

# Chemins spécifiques pour l'analyse d'albédo (MCD43A3)
ALBEDO_PATHS = OUTPUT_STRUCTURE['products']['MCD43A3_albedo']

# Fractions de couverture analysées
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

# Paramètres d'analyse
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

# Messages et symboles
TREND_SYMBOLS = {
    'increasing': '📈',
    'decreasing': '📉', 
    'no trend': '➡️'
}

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

# Configuration des couleurs pour les graphiques
QUALITY_COLORS = ['#2166ac', '#92c5de', '#fddbc7', '#d6604d']

# Styles de graphiques
PLOT_STYLES = {
    'trend_line': {'linewidth': 2, 'alpha': 0.8},
    'scatter': {'alpha': 0.6, 's': 20},
    'error_bars': {'ecolor': 'black', 'capsize': 5},
    'significance_text': {'fontweight': 'bold', 'ha': 'center', 'va': 'bottom'}
}

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

def get_output_path(product='MCD43A3_albedo', data_type='reports', create_dir=True):
    """
    Retourne le chemin de sortie organisé pour un produit et type de données
    
    Args:
        product (str): Produit MODIS ('MCD43A3_albedo', 'MOD10A1_snow_cover', etc.)
        data_type (str): Type de données ('raw_data', 'figures', 'reports', etc.)
        create_dir (bool): Créer le répertoire s'il n'existe pas
        
    Returns:
        str: Chemin vers le répertoire de sortie
    """
    import os
    
    if product in OUTPUT_STRUCTURE['products']:
        if data_type in OUTPUT_STRUCTURE['products'][product]:
            path = OUTPUT_STRUCTURE['products'][product][data_type]
        else:
            # Fallback vers le répertoire du produit
            path = f"../results/{product}"
    else:
        # Fallback vers le répertoire de base
        path = OUTPUT_DIR
    
    if create_dir and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    
    return path