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

# Répertoire de sortie pour les résultats - nouvelle structure organisée
OUTPUT_DIR = "results"

# ==========================================
# STRUCTURE DES RÉPERTOIRES DE SORTIE
# ==========================================

# Structure organisée par produit MODIS et type de données
OUTPUT_STRUCTURE = {
    'base_dir': 'results',
    'products': {
        'MCD43A3_albedo': {
            'raw_data': 'results/MCD43A3_albedo/raw_data',
            'processed_data': 'results/MCD43A3_albedo/processed_data', 
            'trend_analysis': 'results/MCD43A3_albedo/trend_analysis',
            'figures': 'results/MCD43A3_albedo/figures',
            'reports': 'results/MCD43A3_albedo/reports'
        },
        'MOD10A1_snow_cover': {
            'raw_data': 'results/MOD10A1_snow_cover/raw_data',
            'processed_data': 'results/MOD10A1_snow_cover/processed_data',
            'analysis': 'results/MOD10A1_snow_cover/analysis',
            'figures': 'results/MOD10A1_snow_cover/figures'
        },
        'MYD10A1_aqua_snow': {
            'raw_data': 'results/MYD10A1_aqua_snow/raw_data',
            'processed_data': 'results/MYD10A1_aqua_snow/processed_data',
            'analysis': 'results/MYD10A1_aqua_snow/analysis',
            'figures': 'results/MYD10A1_aqua_snow/figures'
        },
        'combined_analysis': {
            'multi_product_comparisons': 'results/combined_analysis/multi_product_comparisons',
            'integrated_reports': 'results/combined_analysis/integrated_reports',
            'summary_figures': 'results/combined_analysis/summary_figures'
        },
        'metadata': {
            'processing_logs': 'results/metadata/processing_logs',
            'data_quality_reports': 'results/metadata/data_quality_reports',
            'configuration_snapshots': 'results/metadata/configuration_snapshots'
        }
    }
}

# Chemins spécifiques pour l'analyse d'albédo (MCD43A3)
ALBEDO_PATHS = OUTPUT_STRUCTURE['products']['MCD43A3_albedo']

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
            path = f"results/{product}"
    else:
        # Fallback vers le répertoire de base
        path = OUTPUT_DIR
    
    if create_dir and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    
    return path

def print_config_summary():
    """
    Affiche un résumé de la configuration
    """
    print("⚙️  CONFIGURATION DE L'ANALYSE")
    print("="*50)
    print(f"📊 Fichier CSV: {CSV_PATH}")
    print(f"📁 Répertoire de sortie: {OUTPUT_DIR}")
    print(f"📁 Structure organisée: {len(OUTPUT_STRUCTURE['products'])} produits MODIS")
    print(f"🔍 Variable analysée: {ANALYSIS_VARIABLE}")
    print(f"📊 Fractions: {len(FRACTION_CLASSES)} classes")
    print(f"🔄 Bootstrap: {ANALYSIS_CONFIG['bootstrap_iterations']} itérations")
    print(f"📈 Seuils significativité: {ANALYSIS_CONFIG['significance_levels']}")
    print("="*50)

# ==========================================
# CONFIGURATION GOOGLE EARTH ENGINE
# ==========================================

# Configuration GEE pour récupération de données fraîches
GEE_CONFIG = {
    'collections': {
        'albedo': 'MODIS/061/MCD43A3',  # MODIS/Terra+Aqua BRDF/Albedo
        'snow_cover': 'MODIS/061/MOD10A1',  # Terra Snow Cover Daily
        'aqua_snow': 'MODIS/061/MYD10A1'  # Aqua Snow Cover Daily
    },
    'regions': {
        'saskatchewan': {
            'west': -110.0,
            'east': -101.0,
            'south': 49.0,
            'north': 60.0,
            'description': 'Province entière de Saskatchewan'
        },
        'glacier': {
            'west': -108.0,
            'east': -105.0,
            'south': 51.5,
            'north': 53.0,
            'description': 'Région glaciaire Saskatchewan (défaut)'
        }
    },
    'bands': {
        'albedo_primary': [
            'Albedo_WSA_shortwave',  # Albédo shortwave (principal)
            'Albedo_BSA_shortwave',  # Albédo black-sky shortwave
            'Albedo_WSA_vis',        # Albédo visible
            'Albedo_WSA_nir'         # Albédo proche infrarouge
        ],
        'snow_cover': [
            'NDSI_Snow_Cover',       # Fraction de couverture neigeuse
            'Snow_Albedo_Daily_Tile' # Albédo de la neige
        ]
    },
    'quality_filters': {
        'max_cloud_cover': 20,   # % couverture nuageuse max
        'modis_scale': 500,      # Résolution spatiale (mètres)
        'max_pixels': 1e9        # Pixels max pour les calculs
    },
    'export_settings': {
        'add_synthetic_fractions': True,  # Ajouter fractions synthétiques pour compatibilité
        'output_prefix': 'gee_',          # Préfixe pour fichiers GEE
        'backup_existing': True           # Sauvegarder fichiers existants
    },
    'authentication': {
        'service_account_path': None,     # Chemin vers clé service account (optionnel)
        'fallback_to_user_auth': True,    # Utiliser auth utilisateur si service account échoue
        'require_interactive': False      # Forcer auth interactive
    }
}

# Collections GEE disponibles (pour référence)
GEE_COLLECTIONS_INFO = {
    'MCD43A3': {
        'name': 'MODIS/Terra+Aqua BRDF/Albedo',
        'temporal_resolution': '8 jours',
        'spatial_resolution': '500m',
        'bands_count': 20,
        'description': 'Albédo et BRDF MODIS combiné Terra/Aqua'
    },
    'MOD10A1': {
        'name': 'MODIS/Terra Snow Cover Daily',
        'temporal_resolution': 'Quotidien',
        'spatial_resolution': '500m', 
        'bands_count': 10,
        'description': 'Couverture neigeuse quotidienne Terra'
    },
    'MYD10A1': {
        'name': 'MODIS/Aqua Snow Cover Daily', 
        'temporal_resolution': 'Quotidien',
        'spatial_resolution': '500m',
        'bands_count': 10,
        'description': 'Couverture neigeuse quotidienne Aqua'
    }
}

def get_gee_output_path(data_type='gee_data', create_dir=True):
    """
    Retourne le chemin de sortie pour les données GEE
    
    Args:
        data_type (str): Type de données GEE ('gee_data', 'gee_exports', etc.)
        create_dir (bool): Créer le répertoire s'il n'existe pas
        
    Returns:
        str: Chemin vers le répertoire GEE
    """
    import os
    
    gee_path = f"{OUTPUT_DIR}/gee_data"
    
    if data_type != 'gee_data':
        gee_path = f"{gee_path}/{data_type}"
    
    if create_dir and not os.path.exists(gee_path):
        os.makedirs(gee_path, exist_ok=True)
    
    return gee_path

def print_gee_config_summary():
    """
    Affiche un résumé de la configuration GEE
    """
    print("🛰️  CONFIGURATION GOOGLE EARTH ENGINE")
    print("="*50)
    print(f"📊 Collections disponibles: {len(GEE_CONFIG['collections'])}")
    for name, collection in GEE_CONFIG['collections'].items():
        print(f"   • {name}: {collection}")
    
    print(f"\n🌍 Régions configurées: {len(GEE_CONFIG['regions'])}")
    for name, region in GEE_CONFIG['regions'].items():
        print(f"   • {name}: {region['description']}")
    
    print(f"\n📡 Paramètres qualité:")
    print(f"   • Couverture nuageuse max: {GEE_CONFIG['quality_filters']['max_cloud_cover']}%")
    print(f"   • Résolution: {GEE_CONFIG['quality_filters']['modis_scale']}m")
    
    print(f"\n💾 Export:")
    print(f"   • Préfixe: {GEE_CONFIG['export_settings']['output_prefix']}")
    print(f"   • Fractions synthétiques: {GEE_CONFIG['export_settings']['add_synthetic_fractions']}")
    print("="*50)