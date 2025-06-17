"""
Streamlit Data Loaders
======================

Cached data loading functions optimized for Streamlit.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.dataset_manager import DatasetManager
from data.handler import AlbedoDataHandler


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_dataset_cached(dataset_name: str, start_year: int = None, end_year: int = None):
    """
    Load dataset with caching for better Streamlit performance.
    
    Parameters:
    -----------
    dataset_name : str
        Name of dataset ('MCD43A3' or 'MOD10A1')
    start_year : int, optional
        Start year for filtering
    end_year : int, optional
        End year for filtering
    
    Returns:
    --------
    AlbedoDataHandler or None
        Loaded dataset or None if failed
    """
    try:
        manager = DatasetManager()
        
        if dataset_name == 'MCD43A3':
            data_handler = manager.load_mcd43a3()
        elif dataset_name == 'MOD10A1':
            data_handler = manager.load_mod10a1()
        else:
            raise ValueError(f"Unknown dataset: {dataset_name}")
        
        if data_handler is None:
            return None
        
        # Apply date filtering if requested
        if start_year is not None and end_year is not None:
            data_handler.data = data_handler.data[
                (data_handler.data['year'] >= start_year) & 
                (data_handler.data['year'] <= end_year)
            ]
        
        return data_handler
        
    except Exception as e:
        st.error(f"Error loading {dataset_name}: {str(e)}")
        return None


@st.cache_data(ttl=3600)
def load_comparison_datasets(start_year: int = None, end_year: int = None):
    """
    Load both datasets for comparison with caching.
    
    Parameters:
    -----------
    start_year : int, optional
        Start year for filtering
    end_year : int, optional
        End year for filtering
    
    Returns:
    --------
    dict
        Dictionary with 'MCD43A3' and 'MOD10A1' keys
    """
    datasets = {}
    
    for dataset_name in ['MCD43A3', 'MOD10A1']:
        datasets[dataset_name] = load_dataset_cached(dataset_name, start_year, end_year)
    
    return datasets


@st.cache_data(ttl=3600)
def get_data_summary(dataset_name: str):
    """
    Get cached summary statistics for a dataset.
    
    Parameters:
    -----------
    dataset_name : str
        Name of dataset
    
    Returns:
    --------
    dict
        Summary statistics
    """
    data_handler = load_dataset_cached(dataset_name)
    
    if data_handler is None:
        return None
    
    data = data_handler.data
    
    summary = {
        'total_records': len(data),
        'date_range': {
            'start': data['date'].min(),
            'end': data['date'].max()
        },
        'years': sorted(data['year'].unique()),
        'available_fractions': [col.replace('_mean', '') for col in data.columns if col.endswith('_mean')],
        'missing_data_percentage': data.isnull().sum().sum() / (data.shape[0] * data.shape[1]) * 100
    }
    
    return summary


@st.cache_data(ttl=3600)
def load_elevation_data_cached(start_year: int = None, end_year: int = None):
    """
    Load elevation analysis data with caching.
    
    Parameters:
    -----------
    start_year : int, optional
        Start year for filtering
    end_year : int, optional
        End year for filtering
    
    Returns:
    --------
    pandas.DataFrame or None
        Elevation data or None if failed
    """
    try:
        from data.loader import ElevationDataLoader
        
        loader = ElevationDataLoader()
        data = loader.load_elevation_data()
        
        if data is None:
            return None
        
        # Apply date filtering if requested
        if start_year is not None and end_year is not None:
            data = data[
                (data['year'] >= start_year) & 
                (data['year'] <= end_year)
            ]
        
        return data
        
    except Exception as e:
        st.error(f"Error loading elevation data: {str(e)}")
        return None


@st.cache_data(ttl=1800)  # Cache for 30 minutes (more dynamic)
def get_fraction_statistics(dataset_name: str, fraction: str, start_year: int = None, end_year: int = None):
    """
    Get cached statistics for a specific fraction.
    
    Parameters:
    -----------
    dataset_name : str
        Name of dataset
    fraction : str
        Fraction class name
    start_year : int, optional
        Start year for filtering
    end_year : int, optional
        End year for filtering
    
    Returns:
    --------
    dict
        Fraction statistics
    """
    data_handler = load_dataset_cached(dataset_name, start_year, end_year)
    
    if data_handler is None:
        return None
    
    col_name = f"{fraction}_mean"
    if col_name not in data_handler.data.columns:
        return None
    
    data = data_handler.data[col_name].dropna()
    
    if len(data) == 0:
        return None
    
    stats = {
        'count': len(data),
        'mean': float(data.mean()),
        'median': float(data.median()),
        'std': float(data.std()),
        'min': float(data.min()),
        'max': float(data.max()),
        'skewness': float(data.skew()),
        'kurtosis': float(data.kurtosis())
    }
    
    return stats


@st.cache_data(ttl=1800)
def calculate_seasonal_patterns(dataset_name: str, fraction: str):
    """
    Calculate seasonal patterns with caching.
    
    Parameters:
    -----------
    dataset_name : str
        Name of dataset
    fraction : str
        Fraction class name
    
    Returns:
    --------
    dict
        Seasonal pattern data
    """
    data_handler = load_dataset_cached(dataset_name)
    
    if data_handler is None:
        return None
    
    col_name = f"{fraction}_mean"
    if col_name not in data_handler.data.columns:
        return None
    
    data = data_handler.data[['date', col_name]].dropna()
    data['month'] = data['date'].dt.month
    
    monthly_stats = data.groupby('month')[col_name].agg(['mean', 'std', 'count']).reset_index()
    
    seasonal_patterns = {
        'monthly_means': monthly_stats['mean'].tolist(),
        'monthly_stds': monthly_stats['std'].tolist(),
        'monthly_counts': monthly_stats['count'].tolist(),
        'peak_month': int(monthly_stats.loc[monthly_stats['mean'].idxmax(), 'month']),
        'low_month': int(monthly_stats.loc[monthly_stats['mean'].idxmin(), 'month']),
        'seasonal_amplitude': float(monthly_stats['mean'].max() - monthly_stats['mean'].min())
    }
    
    return seasonal_patterns


def clear_cache():
    """Clear all cached data."""
    st.cache_data.clear()


def get_cache_info():
    """Get information about cached data."""
    # This would require accessing Streamlit's internal cache
    # For now, return a placeholder
    return {
        'cached_datasets': ['Functionality not yet implemented'],
        'cache_size': 'Unknown',
        'last_updated': 'Unknown'
    }