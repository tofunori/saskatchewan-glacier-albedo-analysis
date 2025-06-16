"""
Gestionnaire de datasets MODIS
=============================

Ce module gère le chargement et la sélection entre les différents
produits MODIS (MCD43A3 vs MOD10A1) ainsi que la préparation
des données pour les analyses comparatives.
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
import warnings

# Import from parent package
from ..config import (
    MCD43A3_CONFIG, MOD10A1_CONFIG, COMPARISON_CONFIG,
    FRACTION_CLASSES, get_dataset_config, get_available_datasets
)
from ..utils.helpers import print_section_header, validate_data
from .loader import SaskatchewanDataLoader

class DatasetManager:
    """
    Gestionnaire principal pour les datasets MODIS
    """
    
    def __init__(self):
        """
        Initialise le gestionnaire de datasets
        """
        self.datasets = {}
        self.current_dataset = None
        self.comparison_data = None
        
    def load_dataset(self, dataset_name, force_reload=False):
        """
        Charge un dataset spécifique
        
        Args:
            dataset_name (str): 'MCD43A3' ou 'MOD10A1'
            force_reload (bool): Forcer le rechargement si déjà en cache
            
        Returns:
            SaskatchewanDataLoader: Instance du chargeur de données
        """
        if not force_reload and dataset_name in self.datasets:
            print(f"✓ Dataset {dataset_name} déjà en cache")
            return self.datasets[dataset_name]
        
        print_section_header(f"Chargement du dataset {dataset_name}", level=2)
        
        # Obtenir la configuration
        config = get_dataset_config(dataset_name)
        
        # Vérifier l'existence des fichiers
        if not os.path.exists(config['csv_path']):
            raise FileNotFoundError(f"Fichier CSV non trouvé: {config['csv_path']}")
        
        # Créer et charger les données
        loader = SaskatchewanDataLoader(config['csv_path'])
        loader.load_data()
        
        # Ajouter les métadonnées du dataset
        loader.dataset_info = {
            'name': dataset_name,
            'config': config,
            'qa_available': os.path.exists(config['qa_csv_path']) if config['qa_csv_path'] else False
        }
        
        # Mettre en cache
        self.datasets[dataset_name] = loader
        self.current_dataset = dataset_name
        
        print(f"✓ Dataset {dataset_name} chargé avec succès")
        loader.print_data_summary()
        
        return loader
    
    def get_dataset(self, dataset_name):
        """
        Récupère un dataset (le charge si nécessaire)
        
        Args:
            dataset_name (str): 'MCD43A3' ou 'MOD10A1'
            
        Returns:
            SaskatchewanDataLoader: Instance du chargeur de données
        """
        if dataset_name not in self.datasets:
            return self.load_dataset(dataset_name)
        return self.datasets[dataset_name]
    
    def load_qa_data(self, dataset_name):
        """
        Charge les données de qualité pour un dataset
        
        Args:
            dataset_name (str): 'MCD43A3' ou 'MOD10A1'
            
        Returns:
            pd.DataFrame: Données de qualité
        """
        config = get_dataset_config(dataset_name)
        
        if not config['qa_csv_path'] or not os.path.exists(config['qa_csv_path']):
            raise FileNotFoundError(f"Fichier QA non trouvé pour {dataset_name}")
        
        print(f"📊 Chargement des données QA pour {dataset_name}...")
        qa_data = pd.read_csv(config['qa_csv_path'])
        
        # Convertir la date
        qa_data['date'] = pd.to_datetime(qa_data['date'])
        
        print(f"✓ Données QA chargées: {len(qa_data)} observations")
        return qa_data
    
    def prepare_comparison_data(self, sync_dates=True):
        """
        Prépare les données pour la comparaison entre MCD43A3 et MOD10A1
        
        Args:
            sync_dates (bool): Synchroniser les dates entre les datasets
            
        Returns:
            dict: Données comparatives avec clés 'mcd43a3', 'mod10a1', 'merged'
        """
        print_section_header("Préparation des données de comparaison", level=2)
        
        # Charger les deux datasets
        mcd43a3 = self.get_dataset('MCD43A3')
        mod10a1 = self.get_dataset('MOD10A1')
        
        if sync_dates:
            # Synchroniser les dates avec une tolérance
            merged_data = self._sync_datasets(mcd43a3.data, mod10a1.data)
        else:
            # Fusion simple sur les dates exactes
            merged_data = self._merge_datasets(mcd43a3.data, mod10a1.data)
        
        self.comparison_data = {
            'mcd43a3': mcd43a3.data,
            'mod10a1': mod10a1.data,
            'merged': merged_data,
            'sync_info': {
                'mcd43a3_total': len(mcd43a3.data),
                'mod10a1_total': len(mod10a1.data),
                'common_dates': len(merged_data),
                'sync_enabled': sync_dates
            }
        }
        
        print(f"✓ Données de comparaison préparées:")
        print(f"  - MCD43A3: {len(mcd43a3.data)} observations")
        print(f"  - MOD10A1: {len(mod10a1.data)} observations")
        print(f"  - Communes: {len(merged_data)} observations")
        
        return self.comparison_data
    
    def _sync_datasets(self, data1, data2, tolerance_days=1):
        """
        Synchronise deux datasets avec une tolérance de dates
        
        Args:
            data1 (pd.DataFrame): Premier dataset
            data2 (pd.DataFrame): Deuxième dataset
            tolerance_days (int): Tolérance en jours
            
        Returns:
            pd.DataFrame: Données synchronisées
        """
        tolerance = pd.Timedelta(days=tolerance_days)
        merged_list = []
        
        # Pour chaque date dans data1, chercher la date la plus proche dans data2
        for _, row1 in data1.iterrows():
            date1 = row1['date']
            
            # Trouver les dates dans la fenêtre de tolérance
            mask = abs(data2['date'] - date1) <= tolerance
            candidates = data2[mask]
            
            if not candidates.empty:
                # Prendre la date la plus proche
                closest_idx = (candidates['date'] - date1).abs().idxmin()
                row2 = data2.loc[closest_idx]
                
                # Vérifier que au moins une fraction a des données valides dans les deux datasets
                has_valid_data = False
                for fraction in FRACTION_CLASSES:
                    col1 = f'{fraction}_mean'
                    col2 = f'{fraction}_mean'
                    
                    if (col1 in row1.index and col2 in row2.index and 
                        pd.notna(row1[col1]) and pd.notna(row2[col2])):
                        has_valid_data = True
                        break
                
                # Ne créer la ligne combinée que si elle a des données valides
                if has_valid_data:
                    merged_row = self._merge_rows(row1, row2, 'mcd43a3', 'mod10a1')
                    merged_list.append(merged_row)
        
        if merged_list:
            return pd.DataFrame(merged_list)
        else:
            return pd.DataFrame()
    
    def _merge_datasets(self, data1, data2):
        """
        Fusion simple des datasets sur les dates exactes
        
        Args:
            data1 (pd.DataFrame): Premier dataset
            data2 (pd.DataFrame): Deuxième dataset
            
        Returns:
            pd.DataFrame: Données fusionnées
        """
        # Renommer les colonnes pour éviter les conflits
        data1_renamed = data1.copy()
        data2_renamed = data2.copy()
        
        # Identifier les colonnes de fractions
        fraction_cols = []
        for fraction in FRACTION_CLASSES:
            for var in ['mean', 'median', 'pixel_count', 'data_quality']:
                col = f'{fraction}_{var}'
                if col in data1.columns:
                    fraction_cols.append(col)
        
        # Renommer les colonnes de fractions
        rename_dict1 = {col: f'mcd43a3_{col}' for col in fraction_cols if col in data1.columns}
        rename_dict2 = {col: f'mod10a1_{col}' for col in fraction_cols if col in data2.columns}
        
        data1_renamed = data1_renamed.rename(columns=rename_dict1)
        data2_renamed = data2_renamed.rename(columns=rename_dict2)
        
        # Fusionner sur la date
        merged = pd.merge(
            data1_renamed,
            data2_renamed,
            on='date',
            how='inner',
            suffixes=('_mcd43a3', '_mod10a1')
        )
        
        # Filtrer pour ne garder que les lignes où les deux datasets ont des données valides
        # pour au moins une fraction
        valid_rows_mask = pd.Series([False] * len(merged))
        
        for fraction in FRACTION_CLASSES:
            mcd_col = f'mcd43a3_{fraction}_mean'
            mod_col = f'mod10a1_{fraction}_mean'
            
            if mcd_col in merged.columns and mod_col in merged.columns:
                # Vérifier que les deux valeurs sont valides (non-NaN)
                fraction_valid = merged[mcd_col].notna() & merged[mod_col].notna()
                valid_rows_mask = valid_rows_mask | fraction_valid
        
        # Ne garder que les lignes avec au moins une fraction valide dans les deux datasets
        filtered_merged = merged[valid_rows_mask].copy()
        
        print(f"📊 Données filtrées: {len(merged)} → {len(filtered_merged)} lignes avec données valides dans les deux produits")
        
        return filtered_merged
    
    def _merge_rows(self, row1, row2, prefix1, prefix2):
        """
        Fusionne deux lignes de données avec des préfixes
        
        Args:
            row1, row2: Lignes de données pandas
            prefix1, prefix2: Préfixes pour les colonnes
            
        Returns:
            dict: Ligne fusionnée
        """
        merged = {}
        
        # Colonnes temporelles communes
        temporal_cols = ['date', 'year', 'month', 'doy', 'decimal_year', 'season']
        for col in temporal_cols:
            if col in row1:
                merged[col] = row1[col]
        
        # Colonnes spécifiques avec préfixes
        for col, value in row1.items():
            if col not in temporal_cols:
                merged[f'{prefix1}_{col}'] = value
        
        for col, value in row2.items():
            if col not in temporal_cols:
                merged[f'{prefix2}_{col}'] = value
        
        return merged
    
    def get_comparison_summary(self):
        """
        Retourne un résumé des données de comparaison
        
        Returns:
            dict: Résumé des comparaisons
        """
        if self.comparison_data is None:
            return {"error": "Données de comparaison non préparées"}
        
        merged = self.comparison_data['merged']
        summary = {
            'total_common_dates': len(merged),
            'date_range': {
                'start': merged['date'].min(),
                'end': merged['date'].max()
            },
            'years_covered': sorted(merged['year'].unique()),
            'correlations': {},
            'differences': {}
        }
        
        # Calculer les corrélations par fraction
        for fraction in FRACTION_CLASSES:
            mcd_col = f'mcd43a3_{fraction}_mean'
            mod_col = f'mod10a1_{fraction}_mean'
            
            if mcd_col in merged.columns and mod_col in merged.columns:
                # Supprimer les NaN pour la corrélation
                valid_data = merged[[mcd_col, mod_col]].dropna()
                
                if len(valid_data) > 10:  # Minimum d'observations pour une corrélation fiable
                    corr = valid_data[mcd_col].corr(valid_data[mod_col])
                    diff_mean = (valid_data[mod_col] - valid_data[mcd_col]).mean()
                    diff_std = (valid_data[mod_col] - valid_data[mcd_col]).std()
                    
                    summary['correlations'][fraction] = {
                        'correlation': corr,
                        'n_observations': len(valid_data)
                    }
                    
                    summary['differences'][fraction] = {
                        'mean_difference': diff_mean,
                        'std_difference': diff_std,
                        'rmse': np.sqrt(((valid_data[mod_col] - valid_data[mcd_col]) ** 2).mean())
                    }
        
        return summary
    
    def print_comparison_summary(self):
        """
        Affiche un résumé des données de comparaison
        """
        summary = self.get_comparison_summary()
        
        if 'error' in summary:
            print(f"❌ {summary['error']}")
            return
        
        print_section_header("Résumé de la comparaison MCD43A3 vs MOD10A1", level=2)
        print(f"📊 Dates communes: {summary['total_common_dates']}")
        print(f"📅 Période: {summary['date_range']['start'].strftime('%Y-%m-%d')} → {summary['date_range']['end'].strftime('%Y-%m-%d')}")
        print(f"🗓️  Années: {len(summary['years_covered'])} années ({min(summary['years_covered'])}-{max(summary['years_covered'])})")
        
        print(f"\n🔗 CORRÉLATIONS PAR FRACTION:")
        for fraction, stats in summary['correlations'].items():
            corr = stats['correlation']
            n_obs = stats['n_observations']
            quality = "🟢 Forte" if corr > 0.8 else "🟡 Modérée" if corr > 0.6 else "🔴 Faible"
            print(f"  {fraction}: r = {corr:.3f} ({quality}, n={n_obs})")
        
        print(f"\n📏 DIFFÉRENCES MOYENNES (MOD10A1 - MCD43A3):")
        for fraction, stats in summary['differences'].items():
            diff = stats['mean_difference']
            rmse = stats['rmse']
            trend = "📈" if diff > 0.01 else "📉" if diff < -0.01 else "➡️"
            print(f"  {fraction}: {diff:+.3f} ± {stats['std_difference']:.3f} (RMSE: {rmse:.3f}) {trend}")
    
    def list_available_datasets(self):
        """
        Affiche la liste des datasets disponibles
        """
        print_section_header("Datasets MODIS disponibles", level=2)
        
        datasets = get_available_datasets()
        for name, info in datasets.items():
            config = info['config']
            csv_status = "✅" if info['csv_exists'] else "❌"
            qa_status = "✅" if info['qa_exists'] else "❌"
            
            print(f"\n📊 {name} - {config['description']}")
            print(f"  Fichier principal: {csv_status}")
            print(f"  Fichier QA: {qa_status}")
            print(f"  Résolution: {config['temporal_resolution']}")
            print(f"  Échelle: {config['scaling_info']}")
    
    def get_dataset_for_analysis(self, dataset_choice):
        """
        Prépare le dataset approprié pour l'analyse
        
        Args:
            dataset_choice (str): 'MCD43A3', 'MOD10A1', ou 'COMPARISON'
            
        Returns:
            Union[SaskatchewanDataLoader, dict]: Dataset ou données de comparaison
        """
        if dataset_choice in ['MCD43A3', 'MOD10A1']:
            return self.get_dataset(dataset_choice)
        elif dataset_choice == 'COMPARISON':
            return self.prepare_comparison_data()
        else:
            raise ValueError(f"Choix de dataset invalide: {dataset_choice}")