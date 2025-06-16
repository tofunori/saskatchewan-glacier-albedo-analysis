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

# Chemin vers votre fichier CSV (MODIFIEZ ICI)
CSV_PATH = r"D:\Downloads\daily_albedo_mann_kendall_ready_2010_2024.csv"

# Répertoire de sortie pour les résultats
OUTPUT_DIR = "analysis_results"

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

def print_config_summary():
    """
    Affiche un résumé de la configuration
    """
    print("⚙️  CONFIGURATION DE L'ANALYSE")
    print("="*50)
    print(f"📊 Fichier CSV: {CSV_PATH}")
    print(f"📁 Répertoire de sortie: {OUTPUT_DIR}")
    print(f"🔍 Variable analysée: {ANALYSIS_VARIABLE}")
    print(f"📊 Fractions: {len(FRACTION_CLASSES)} classes")
    print(f"🔄 Bootstrap: {ANALYSIS_CONFIG['bootstrap_iterations']} itérations")
    print(f"📈 Seuils significativité: {ANALYSIS_CONFIG['significance_levels']}")
    print("="*50)