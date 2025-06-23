"""
Database-based Data Handler for Saskatchewan Glacier Albedo Analysis
===================================================================

This module provides a PostgreSQL-based data handler that replaces the CSV-based
AlbedoDataHandler while maintaining the same API for backward compatibility.
"""

import pandas as pd
import numpy as np
import sys
import os
from typing import Optional, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_connection
from config import FRACTION_CLASSES, CLASS_LABELS, ANALYSIS_CONFIG
from utils.helpers import print_section_header

class AlbedoDataHandler:
    """
    Database-based data handler for Saskatchewan Glacier albedo analysis
    
    This class provides the same interface as the original CSV-based handler
    but loads data from PostgreSQL instead of CSV files.
    """
    
    def __init__(self, dataset_type: str = "MCD43A3"):
        """
        Initialize the database-based data handler
        
        Args:
            dataset_type (str): Type of dataset ("MCD43A3" or "MOD10A1")
        """
        self.dataset_type = dataset_type.upper()
        self.data = None
        self.raw_data = None
        self.fraction_classes = FRACTION_CLASSES
        self.class_labels = CLASS_LABELS
        self.db_connection = get_connection()
        
        # Map dataset types to table names
        self.table_mapping = {
            "MCD43A3": "mcd43a3_measurements",
            "MOD10A1": "mod10a1_measurements"
        }
        
        if self.dataset_type not in self.table_mapping:
            raise ValueError(f"Unsupported dataset type: {dataset_type}. Use 'MCD43A3' or 'MOD10A1'")
        
        self.table_name = self.table_mapping[self.dataset_type]
        
    def __len__(self):
        """
        Returns the number of observations in the loaded data
        
        Returns:
            int: Number of observations, or 0 if no data is loaded
        """
        if self.data is not None:
            return len(self.data)
        return 0
        
    def load_data(self):
        """
        Load and prepare data from PostgreSQL database
        
        Returns:
            self: For method chaining
            
        Raises:
            ValueError: If required columns are missing or no data found
        """
        print_section_header(f"Loading {self.dataset_type} data from database", level=2)
        
        try:
            # Load data from database
            query = f"""
            SELECT 
                date,
                year,
                decimal_year,
                doy,
                season,
                min_pixels_threshold,
                border_mean,
                border_median,
                mixed_low_mean,
                mixed_low_median,
                mixed_high_mean,
                mixed_high_median,
                mostly_ice_mean,
                mostly_ice_median,
                pure_ice_mean,
                pure_ice_median,
                total_valid_pixels
            FROM albedo.{self.table_name}
            ORDER BY date
            """
            
            self.raw_data = self.db_connection.execute_query(query)
            
            if len(self.raw_data) == 0:
                raise ValueError(f"No data found in {self.table_name}")
            
            self.data = self.raw_data.copy()
            
            # Prepare the data
            self._prepare_temporal_data()
            self._filter_quality_data()
            self._add_seasonal_variables()
            self._validate_required_columns()
            
            print(f"✓ Data loaded: {len(self.data)} observations")
            print(f"✓ Period: {self.data['date'].min()} to {self.data['date'].max()}")
            
            return self
            
        except Exception as e:
            raise ValueError(f"Failed to load data from database: {e}")
    
    def _prepare_temporal_data(self):
        """
        Prepare temporal variables (already in database, but ensure consistency)
        """
        # Convert date if it's not already datetime
        if not pd.api.types.is_datetime64_any_dtype(self.data['date']):
            self.data['date'] = pd.to_datetime(self.data['date'])
        
        # Add month column if not present
        if 'month' not in self.data.columns:
            self.data['month'] = self.data['date'].dt.month
    
    def _filter_quality_data(self):
        """
        Filter data according to quality criteria
        """
        initial_count = len(self.data)
        
        # Filter by minimum pixels threshold if available
        if 'min_pixels_threshold' in self.data.columns:
            # Convert threshold to boolean if it's numeric
            if self.data['min_pixels_threshold'].dtype in [int, float]:
                self.data = self.data[self.data['min_pixels_threshold'] >= 1]
            else:
                self.data = self.data[self.data['min_pixels_threshold'] == True]
            
            filtered_count = len(self.data)
            print(f"✓ Quality filter applied: {filtered_count}/{initial_count} observations kept")
        
        # Remove rows with all albedo values missing
        albedo_columns = []
        for fraction in self.fraction_classes:
            for var in ['mean', 'median']:
                col = f'{fraction}_{var}'
                if col in self.data.columns:
                    albedo_columns.append(col)
        
        if albedo_columns:
            # Keep rows with at least one valid albedo value
            self.data = self.data.dropna(subset=albedo_columns, how='all')
            print(f"✓ Rows without albedo data removed: {len(self.data)} observations remaining")
    
    def _add_seasonal_variables(self):
        """
        Add seasonal variables
        """
        # Simplified season (early/mid/late summer)
        self.data['season'] = self.data['month'].map({
            6: 'early_summer',
            7: 'early_summer', 
            8: 'mid_summer',
            9: 'late_summer'
        })
        
        # Detailed season labels
        self.data['season_label'] = self.data['month'].map({
            6: 'Early Summer',
            7: 'Early Summer',
            8: 'Mid Summer', 
            9: 'Late Summer'
        })
        
        # Month as category for analysis
        self.data['month_cat'] = self.data['month'].astype('category')
    
    def _validate_required_columns(self):
        """
        Validate that required columns are present
        """
        required_columns = ['date', 'year', 'month', 'doy', 'decimal_year']
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        
        if missing_columns:
            raise ValueError(f"Required columns missing: {missing_columns}")
        
        # Check that at least one fraction has albedo data
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
            raise ValueError("No valid albedo data found")
    
    def get_data_summary(self):
        """
        Return summary of loaded data
        
        Returns:
            dict: Data summary
        """
        if self.data is None:
            return {"error": "Data not loaded"}
        
        summary = {
            'dataset_type': self.dataset_type,
            'total_observations': len(self.data),
            'date_range': {
                'start': self.data['date'].min(),
                'end': self.data['date'].max()
            },
            'years_covered': sorted(self.data['year'].unique()),
            'months_covered': sorted(self.data['month'].unique()),
            'fractions_available': []
        }
        
        # Check available fractions
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
        Print detailed data summary
        """
        summary = self.get_data_summary()
        
        print_section_header(f"{summary['dataset_type']} Data Summary", level=2)
        print(f"📊 Total observations: {summary['total_observations']}")
        print(f"📅 Period: {summary['date_range']['start'].strftime('%Y-%m-%d')} → {summary['date_range']['end'].strftime('%Y-%m-%d')}")
        print(f"🗓️  Years: {len(summary['years_covered'])} years ({min(summary['years_covered'])}-{max(summary['years_covered'])})")
        print(f"📆 Months: {summary['months_covered']}")
        
        print("\n📊 Data availability by fraction:")
        for fraction_info in summary['fractions_available']:
            label = fraction_info['label']
            mean_data = fraction_info['data']['mean']
            median_data = fraction_info['data']['median']
            
            print(f"\n  {label}:")
            if mean_data['available']:
                print(f"    Mean: {mean_data['valid_observations']} obs ({mean_data['missing_percentage']:.1f}% missing)")
            if median_data['available']:
                print(f"    Median: {median_data['valid_observations']} obs ({median_data['missing_percentage']:.1f}% missing)")
    
    def get_fraction_data(self, fraction, variable='mean', dropna=True):
        """
        Return data for a specific fraction and variable
        
        Args:
            fraction (str): Fraction name
            variable (str): Variable to extract ('mean' or 'median')
            dropna (bool): Remove missing values
            
        Returns:
            pd.DataFrame: Filtered data with columns 'date', 'decimal_year', 'value'
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        col_name = f"{fraction}_{variable}"
        
        if col_name not in self.data.columns:
            raise ValueError(f"Column {col_name} not found")
        
        # Select relevant columns
        result = self.data[['date', 'decimal_year', col_name]].copy()
        result = result.rename(columns={col_name: 'value'})
        
        if dropna:
            result = result.dropna(subset=['value'])
        
        return result
    
    def get_monthly_data(self, fraction, variable='mean', month=None):
        """
        Return data for a specific month
        
        Args:
            fraction (str): Fraction name
            variable (str): Variable to extract
            month (int, optional): Specific month (6-9)
            
        Returns:
            pd.DataFrame: Filtered data for the month
        """
        data = self.get_fraction_data(fraction, variable, dropna=True)
        
        if month is not None:
            # Add month column if needed
            data['month'] = data['date'].dt.month
            data = data[data['month'] == month]
        
        return data
    
    def get_available_fractions(self, variable='mean'):
        """
        Return list of fractions with available data
        
        Args:
            variable (str): Variable to check
            
        Returns:
            list: List of fractions with available data
        """
        available = []
        
        for fraction in self.fraction_classes:
            col_name = f"{fraction}_{variable}"
            if col_name in self.data.columns and not self.data[col_name].isna().all():
                available.append(fraction)
        
        return available
    
    def export_cleaned_data(self, output_path=None):
        """
        Export cleaned data to CSV (for compatibility)
        
        Args:
            output_path (str, optional): Output path. If None, generates automatically.
        """
        if self.data is None:
            raise ValueError("Data not loaded")
        
        if output_path is None:
            output_path = f"{self.dataset_type.lower()}_cleaned_data.csv"
        
        self.data.to_csv(output_path, index=False)
        print(f"✓ Cleaned data exported: {output_path}")
        
        return output_path

if __name__ == "__main__":
    # Test the database handler
    print("Testing database-based AlbedoDataHandler...")
    
    # Test MCD43A3
    print("\n=== Testing MCD43A3 ===")
    handler_mcd = AlbedoDataHandler("MCD43A3")
    handler_mcd.load_data()
    handler_mcd.print_data_summary()
    
    # Test MOD10A1
    print("\n=== Testing MOD10A1 ===")
    handler_mod = AlbedoDataHandler("MOD10A1")
    handler_mod.load_data()
    handler_mod.print_data_summary()
    
    print("\n✅ Database handler tests completed!")