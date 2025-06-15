"""
Chargement et préparation des données d'albédo
=============================================

Ce module gère le chargement, le nettoyage et la préparation des données
CSV exportées depuis Google Earth Engine.
"""

import pandas as pd
import numpy as np
import os
from .config import FRACTION_CLASSES, CLASS_LABELS, ANALYSIS_CONFIG
from .utils import print_section_header, validate_data

class SaskatchewanDataLoader:
    """
    Classe pour charger et préparer les données d'albédo du glacier Saskatchewan
    """
    
    def __init__(self, csv_path):
        """
        Initialise le chargeur de données
        
        Args:
            csv_path (str): Chemin vers le fichier CSV
        """
        self.csv_path = csv_path
        self.data = None
        self.raw_data = None
        self.fraction_classes = FRACTION_CLASSES
        self.class_labels = CLASS_LABELS
        
    def load_data(self):
        """
        Charge et prépare les données CSV
        
        Returns:
            self: Pour chaînage des méthodes
            
        Raises:
            FileNotFoundError: Si le fichier CSV n'existe pas
            ValueError: Si les colonnes requises sont manquantes
        """
        print_section_header("Chargement des données", level=2)
        
        # Vérifier l'existence du fichier
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Fichier non trouvé: {self.csv_path}")
        
        # Charger le CSV
        try:
            self.raw_data = pd.read_csv(self.csv_path)
            self.data = self.raw_data.copy()
            print(f"✓ Fichier chargé: {len(self.data)} lignes, {len(self.data.columns)} colonnes")
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement du CSV: {e}")
        
        # Préparer les données
        self._prepare_temporal_data()
        self._filter_quality_data()
        self._add_seasonal_variables()
        self._validate_required_columns()
        
        print(f"✓ Données préparées: {len(self.data)} observations valides")
        print(f"✓ Période: {self.data['date'].min()} à {self.data['date'].max()}")
        
        return self
    
    def _prepare_temporal_data(self):
        """
        Prépare les variables temporelles
        """
        # Convertir la date
        if 'date' in self.data.columns:
            self.data['date'] = pd.to_datetime(self.data['date'])
        else:
            raise ValueError("Colonne 'date' manquante dans les données")
        
        # Ajouter les variables temporelles si elles n'existent pas
        if 'year' not in self.data.columns:
            self.data['year'] = self.data['date'].dt.year
        
        if 'month' not in self.data.columns:
            self.data['month'] = self.data['date'].dt.month
        
        if 'doy' not in self.data.columns:
            self.data['doy'] = self.data['date'].dt.dayofyear
        
        if 'decimal_year' not in self.data.columns:
            self.data['decimal_year'] = self.data['year'] + (self.data['doy'] - 1) / 365.25
    
    def _filter_quality_data(self):
        """
        Filtre les données selon les critères de qualité
        """
        initial_count = len(self.data)
        
        # Filtrer selon le seuil minimum de pixels si disponible
        if 'min_pixels_threshold' in self.data.columns:
            self.data = self.data[self.data['min_pixels_threshold'] == True]
            filtered_count = len(self.data)
            print(f"✓ Filtre qualité appliqué: {filtered_count}/{initial_count} observations gardées")
        
        # Supprimer les lignes avec toutes les valeurs d'albédo manquantes
        albedo_columns = []
        for fraction in self.fraction_classes:
            for var in ['mean', 'median']:
                col = f'{fraction}_{var}'
                if col in self.data.columns:
                    albedo_columns.append(col)
        
        if albedo_columns:
            # Garder les lignes avec au moins une valeur d'albédo valide
            self.data = self.data.dropna(subset=albedo_columns, how='all')
            print(f"✓ Lignes sans données d'albédo supprimées: {len(self.data)} observations restantes")
    
    def _add_seasonal_variables(self):
        """
        Ajoute des variables saisonnières
        """
        # Saison simplifiée (early/mid/late summer)
        self.data['season'] = self.data['month'].map({
            6: 'early_summer',
            7: 'early_summer', 
            8: 'mid_summer',
            9: 'late_summer'
        })
        
        # Label de saison plus détaillé
        self.data['season_label'] = self.data['month'].map({
            6: 'Début été',
            7: 'Début été',
            8: 'Mi-été', 
            9: 'Fin été'
        })
        
        # Mois comme catégorie pour analyses
        self.data['month_cat'] = self.data['month'].astype('category')
    
    def _validate_required_columns(self):
        """
        Valide que les colonnes requises sont présentes
        """
        required_columns = ['date', 'year', 'month', 'doy', 'decimal_year']
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        
        if missing_columns:
            raise ValueError(f"Colonnes requises manquantes: {missing_columns}")
        
        # Vérifier qu'au moins une fraction a des données d'albédo
        has_albedo_data = False
        for fraction in self.fraction_classes:
            for var in ['mean', 'median']:
                col = f'{fraction}_{var}'
                if col in self.data.columns and not self.data[col].isna().all():
                    has_albedo_data = True
                    break
            if has_albedo_data:
                break
        
        if not has_albedo_data:
            raise ValueError("Aucune donnée d'albédo valide trouvée")
    
    def get_data_summary(self):
        """
        Retourne un résumé des données chargées
        
        Returns:
            dict: Résumé des données
        """
        if self.data is None:
            return {"error": "Données non chargées"}
        
        summary = {
            'total_observations': len(self.data),
            'date_range': {
                'start': self.data['date'].min(),
                'end': self.data['date'].max()
            },
            'years_covered': sorted(self.data['year'].unique()),
            'months_covered': sorted(self.data['month'].unique()),
            'fractions_available': []
        }
        
        # Vérifier les fractions disponibles
        for fraction in self.fraction_classes:
            fraction_data = {}
            for var in ['mean', 'median']:
                col = f'{fraction}_{var}'
                if col in self.data.columns:
                    valid_count = self.data[col].notna().sum()
                    fraction_data[var] = {
                        'available': True,
                        'valid_observations': int(valid_count),
                        'missing_percentage': (1 - valid_count/len(self.data)) * 100
                    }
                else:
                    fraction_data[var] = {'available': False}
            
            summary['fractions_available'].append({
                'fraction': fraction,
                'label': self.class_labels[fraction],
                'data': fraction_data
            })
        
        return summary
    
    def print_data_summary(self):
        """
        Affiche un résumé détaillé des données
        """
        summary = self.get_data_summary()
        
        print_section_header("Résumé des données", level=2)
        print(f"📊 Observations totales: {summary['total_observations']}")
        print(f"📅 Période: {summary['date_range']['start'].strftime('%Y-%m-%d')} → {summary['date_range']['end'].strftime('%Y-%m-%d')}")
        print(f"🗓️  Années: {len(summary['years_covered'])} années ({min(summary['years_covered'])}-{max(summary['years_covered'])})")
        print(f"📆 Mois: {summary['months_covered']}")
        
        print("\n📊 Disponibilité des données par fraction:")
        for fraction_info in summary['fractions_available']:
            label = fraction_info['label']
            mean_data = fraction_info['data']['mean']
            median_data = fraction_info['data']['median']
            
            print(f"\n  {label}:")
            if mean_data['available']:
                print(f"    Mean: {mean_data['valid_observations']} obs ({mean_data['missing_percentage']:.1f}% manquant)")
            if median_data['available']:
                print(f"    Median: {median_data['valid_observations']} obs ({median_data['missing_percentage']:.1f}% manquant)")
    
    def get_fraction_data(self, fraction, variable='mean', dropna=True):
        """
        Retourne les données pour une fraction et variable spécifiques
        
        Args:
            fraction (str): Nom de la fraction
            variable (str): Variable à extraire ('mean' ou 'median')
            dropna (bool): Supprimer les valeurs manquantes
            
        Returns:
            pd.DataFrame: Données filtrées avec colonnes 'date', 'decimal_year', 'value'
        """
        if self.data is None:
            raise ValueError("Données non chargées. Appeler load_data() d'abord.")
        
        col_name = f"{fraction}_{variable}"
        
        if col_name not in self.data.columns:
            raise ValueError(f"Colonne {col_name} non trouvée")
        
        # Sélectionner les colonnes pertinentes
        result = self.data[['date', 'decimal_year', col_name]].copy()
        result = result.rename(columns={col_name: 'value'})
        
        if dropna:
            result = result.dropna(subset=['value'])
        
        return result
    
    def export_cleaned_data(self, output_path=None):
        """
        Exporte les données nettoyées vers un nouveau CSV
        
        Args:
            output_path (str, optional): Chemin de sortie. Si None, génère automatiquement.
        """
        if self.data is None:
            raise ValueError("Données non chargées")
        
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(self.csv_path))[0]
            output_path = f"{base_name}_cleaned.csv"
        
        self.data.to_csv(output_path, index=False)
        print(f"✓ Données nettoyées exportées: {output_path}")