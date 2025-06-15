"""
Fonctions utilitaires pour l'analyse de tendances d'albédo
=========================================================

Ce module contient les fonctions utilitaires partagées par différents
modules d'analyse.
"""

import numpy as np
import pandas as pd
from datetime import datetime
import warnings

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
    import os
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