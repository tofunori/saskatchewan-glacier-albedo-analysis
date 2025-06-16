"""
Fonctions utilitaires pour l'analyse des tendances d'albédo
==========================================================

Ce module contient toutes les fonctions utilitaires partagées
par les différents modules d'analyse.
"""

import numpy as np
import pandas as pd
from datetime import datetime
import warnings
import os

# Gestion des imports optionnels
try:
    import pymannkendall as mk
    PYMANNKENDALL_AVAILABLE = True
except ImportError:
    PYMANNKENDALL_AVAILABLE = False
    warnings.warn("pymannkendall non disponible. Utilisation de l'implémentation manuelle.")

def check_pymannkendall():
    """
    Vérifie si pymannkendall est disponible
    
    Returns:
        bool: True si pymannkendall est disponible
    """
    return PYMANNKENDALL_AVAILABLE

def manual_mann_kendall(data):
    """
    Implémentation manuelle du test Mann-Kendall si pymannkendall n'est pas disponible
    
    Args:
        data (array-like): Série temporelle à analyser
        
    Returns:
        dict: Résultats du test avec keys: trend, p_value, tau, s, z
    """
    data = np.array(data)
    n = len(data)
    s = 0
    
    for i in range(n-1):
        for j in range(i+1, n):
            s += np.sign(data[j] - data[i])
    
    var_s = n * (n - 1) * (2 * n + 5) / 18
    
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0
    
    # Calcul de la p-value (test bilatéral)
    from scipy.stats import norm
    p_value = 2 * (1 - norm.cdf(abs(z)))
    
    # Calcul du tau de Kendall
    tau = s / (n * (n - 1) / 2)
    
    # Détermination de la tendance
    if p_value < 0.05:
        trend = 'increasing' if s > 0 else 'decreasing'
    else:
        trend = 'no trend'
    
    return {
        'trend': trend,
        'p_value': p_value,
        'tau': tau,
        's': s,
        'z': z
    }

def prewhiten_series(series):
    """
    Pré-blanchiment d'une série temporelle (suppression de la composante AR(1))
    
    Args:
        series (array-like): Série temporelle à pré-blanchir
        
    Returns:
        np.array: Série pré-blanchie
    """
    series = np.array(series)
    
    # Estimation du coefficient AR(1)
    if len(series) < 2:
        return series
    
    rho = np.corrcoef(series[:-1], series[1:])[0, 1]
    
    # Série pré-blanchie
    prewhitened = np.zeros(len(series))
    prewhitened[0] = series[0]
    
    for i in range(1, len(series)):
        prewhitened[i] = series[i] - rho * series[i-1]
    
    return prewhitened[1:]  # Enlever le premier élément

def calculate_autocorrelation(data, lag=1):
    """
    Calcule l'autocorrélation d'une série temporelle
    
    Args:
        data (array-like): Série temporelle
        lag (int): Décalage pour l'autocorrélation
        
    Returns:
        float: Coefficient d'autocorrélation
    """
    data = np.array(data)
    
    if len(data) <= lag:
        return 0.0
    
    return np.corrcoef(data[:-lag], data[lag:])[0, 1]

def validate_data(data, min_obs=10):
    """
    Valide les données pour l'analyse statistique
    
    Args:
        data (array-like): Données à valider
        min_obs (int): Nombre minimum d'observations requises
        
    Returns:
        tuple: (is_valid, cleaned_data, n_removed)
    """
    original_data = np.array(data)
    
    # Supprimer les NaN
    cleaned_data = original_data[~np.isnan(original_data)]
    n_removed = len(original_data) - len(cleaned_data)
    
    # Vérifier le nombre minimum d'observations
    is_valid = len(cleaned_data) >= min_obs
    
    return is_valid, cleaned_data, n_removed

def format_pvalue(p_value, precision=4):
    """
    Formate une p-value pour l'affichage
    
    Args:
        p_value (float): P-value à formater
        precision (int): Nombre de décimales
        
    Returns:
        str: P-value formatée
    """
    if p_value < 0.001:
        return "< 0.001"
    else:
        return f"{p_value:.{precision}f}"

def create_time_index(dates):
    """
    Crée un index temporel décimal pour les analyses de régression
    
    Args:
        dates (pd.Series): Série de dates
        
    Returns:
        np.array: Années décimales
    """
    if isinstance(dates, pd.Series):
        dates = pd.to_datetime(dates)
        years = dates.dt.year
        day_of_year = dates.dt.dayofyear
        # Approximation: diviser par 365.25 pour tenir compte des années bissextiles
        decimal_years = years + (day_of_year - 1) / 365.25
        return decimal_years.values
    else:
        raise ValueError("Dates doit être une pd.Series")

def safe_divide(numerator, denominator, default=0):
    """
    Division sécurisée qui évite la division par zéro
    
    Args:
        numerator: Numérateur
        denominator: Dénominateur
        default: Valeur par défaut si division par zéro
        
    Returns:
        Résultat de la division ou valeur par défaut
    """
    if denominator == 0 or np.isnan(denominator):
        return default
    return numerator / denominator

def print_section_header(title, level=1):
    """
    Affiche un en-tête de section formaté
    
    Args:
        title (str): Titre de la section
        level (int): Niveau d'en-tête (1, 2, ou 3)
    """
    if level == 1:
        print("\n" + "="*80)
        print(f"🔬 {title.upper()}")
        print("="*80)
    elif level == 2:
        print("\n" + "-"*60)
        print(f"📊 {title}")
        print("-"*60)
    else:
        print(f"\n### {title}")

def ensure_directory_exists(file_path):
    """
    S'assure que le répertoire pour un fichier existe
    
    Args:
        file_path (str): Chemin vers le fichier
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

def get_timestamp():
    """
    Retourne un timestamp formaté pour les rapports
    
    Returns:
        str: Timestamp formaté
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def calculate_sen_slope(times, values):
    """
    Calcule la pente de Sen et intervalle de confiance
    
    Args:
        times (array): Temps (années décimales)
        values (array): Valeurs d'albédo
        
    Returns:
        dict: Résultats de la pente de Sen
    """
    try:
        from scipy.stats import theilslopes
        # Calcul avec theilslopes de scipy
        slope, intercept, low_slope, high_slope = theilslopes(values, times, 0.95)
        
        return {
            'slope': slope,
            'slope_per_decade': slope * 10,  # Pente par décennie
            'intercept': intercept,
            'confidence_interval': {
                'low': low_slope,
                'high': high_slope,
                'low_per_decade': low_slope * 10,
                'high_per_decade': high_slope * 10
            },
            'method': 'theilslopes'
        }
    except Exception as e:
        print(f"    ⚠️  Erreur calcul pente Sen: {e}")
        return {
            'slope': np.nan,
            'slope_per_decade': np.nan,
            'intercept': np.nan,
            'confidence_interval': {
                'low': np.nan,
                'high': np.nan,
                'low_per_decade': np.nan,
                'high_per_decade': np.nan
            },
            'method': 'failed'
        }

def perform_mann_kendall_test(values):
    """
    Effectue le test de Mann-Kendall
    
    Args:
        values (array): Valeurs à analyser
        
    Returns:
        dict: Résultats du test Mann-Kendall
    """
    if check_pymannkendall():
        try:
            import pymannkendall as mk
            mk_result = mk.original_test(values)
            return {
                'trend': mk_result.trend,
                'p_value': mk_result.p,
                'tau': mk_result.Tau,
                's': mk_result.s,
                'z': mk_result.z,
                'method': 'pymannkendall'
            }
        except Exception as e:
            print(f"    ⚠️  Erreur pymannkendall: {e}, utilisation manuelle")
            return manual_mann_kendall(values)
    else:
        return manual_mann_kendall(values)

def create_output_filename(base_name, variable, extension='png'):
    """
    Crée un nom de fichier standardisé pour les sorties
    
    Args:
        base_name (str): Nom de base du fichier
        variable (str): Variable analysée
        extension (str): Extension du fichier
        
    Returns:
        str: Nom de fichier complet
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{base_name}_{variable}_{timestamp}.{extension}"

def load_and_validate_csv(csv_path):
    """
    Charge et valide un fichier CSV
    
    Args:
        csv_path (str): Chemin vers le fichier CSV
        
    Returns:
        pd.DataFrame: Données chargées et validées
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        ValueError: Si les colonnes requises sont manquantes
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Fichier non trouvé: {csv_path}")
    
    try:
        data = pd.read_csv(csv_path)
        print(f"✓ Fichier chargé: {len(data)} lignes, {len(data.columns)} colonnes")
        
        # Vérifier les colonnes essentielles
        required_cols = ['date']
        missing_cols = [col for col in required_cols if col not in data.columns]
        
        if missing_cols:
            raise ValueError(f"Colonnes requises manquantes: {missing_cols}")
        
        return data
        
    except Exception as e:
        raise ValueError(f"Erreur lors du chargement du CSV: {e}")

def print_analysis_summary(results):
    """
    Affiche un résumé des résultats d'analyse
    
    Args:
        results (dict): Résultats des analyses
    """
    from ..config import TREND_SYMBOLS, get_significance_marker
    
    print_section_header("RÉSUMÉ DE L'ANALYSE", level=1)
    
    if 'basic_trends' in results:
        basic = results['basic_trends']
        total = len([r for r in basic.values() if not r.get('error', False)])
        significant = len([r for r in basic.values() 
                         if not r.get('error', False) and r['mann_kendall']['p_value'] < 0.05])
        
        print(f"📊 Fractions analysées: {total}")
        print(f"✅ Tendances significatives: {significant}")
        
        if significant > 0:
            print("\n🎯 Fractions avec tendances significatives:")
            for fraction, result in basic.items():
                if not result.get('error', False) and result['mann_kendall']['p_value'] < 0.05:
                    trend = result['mann_kendall']['trend']
                    p_val = result['mann_kendall']['p_value']
                    slope = result['sen_slope']['slope_per_decade']
                    symbol = TREND_SYMBOLS.get(trend, '❓')
                    sig = get_significance_marker(p_val)
                    print(f"  {symbol} {result['label']}: {trend} {sig} ({slope:.6f}/décennie)")
    
    print(f"\n⏰ Analyse terminée à: {get_timestamp()}")
    print("="*80)