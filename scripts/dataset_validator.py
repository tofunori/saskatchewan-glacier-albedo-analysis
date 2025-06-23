"""
Dataset validation and availability checking.
"""

import os
from typing import List, Dict, Tuple
import logging

from config.settings import config
from utils.exceptions import DataLoadError, DatabaseConnectionError

logger = logging.getLogger(__name__)


class DatasetValidator:
    """Handles dataset validation and availability checking."""
    
    def __init__(self):
        """Initialize validator with current configuration."""
        self.config = config
        self.available_datasets: List[str] = []
    
    def check_all_datasets(self) -> bool:
        """Check availability of all configured datasets.
        
        Returns:
            bool: True if at least one dataset is available
        """
        try:
            if self.config.data_mode.lower() == "database":
                return self._check_database_datasets()
            else:
                return self._check_csv_datasets()
        except Exception as e:
            logger.error(f"Error checking datasets: {e}")
            print(f"❌ Error checking datasets: {e}")
            return False
    
    def _check_database_datasets(self) -> bool:
        """Check datasets in database mode.
        
        Returns:
            bool: True if database connection works and datasets exist
        """
        print("🔍 Database mode enabled - checking connectivity...")
        
        try:
            from data.unified_loader import get_albedo_handler
        except ImportError as e:
            raise DatabaseConnectionError(f"Cannot import database handler: {e}")
        
        self.available_datasets = []
        
        for dataset_name in ['MCD43A3', 'MOD10A1']:
            try:
                dataset_config = self.config.get_dataset_config(dataset_name)
                if not dataset_config:
                    continue
                
                handler = get_albedo_handler(dataset_name)
                test_data = handler.load_data()
                
                if len(test_data) > 0:
                    self.available_datasets.append(dataset_name)
                    print(f"✅ Dataset {dataset_name} available in database ({len(test_data)} rows)")
                else:
                    print(f"❌ Dataset {dataset_name} empty in database")
                    
            except Exception as e:
                logger.warning(f"Dataset {dataset_name} inaccessible: {e}")
                print(f"❌ Dataset {dataset_name} inaccessible in database: {e}")
        
        return len(self.available_datasets) > 0
    
    def _check_csv_datasets(self) -> bool:
        """Check datasets in CSV mode.
        
        Returns:
            bool: True if at least one CSV file exists
        """
        print("🔍 CSV mode enabled - checking files...")
        
        self.available_datasets = []
        
        for dataset_name, dataset_config in self.config.get_all_datasets().items():
            if os.path.exists(dataset_config.csv_path):
                self.available_datasets.append(dataset_name)
                print(f"✅ Dataset {dataset_name} found: {dataset_config.csv_path}")
            else:
                print(f"❌ Dataset {dataset_name} missing: {dataset_config.csv_path}")
        
        return len(self.available_datasets) > 0
    
    def get_available_datasets(self) -> List[str]:
        """Get list of available datasets.
        
        Returns:
            List of available dataset names
        """
        return self.available_datasets.copy()
    
    def is_dataset_available(self, dataset_name: str) -> bool:
        """Check if specific dataset is available.
        
        Args:
            dataset_name: Name of dataset to check
            
        Returns:
            bool: True if dataset is available
        """
        return dataset_name in self.available_datasets


def check_datasets_availability() -> bool:
    """Legacy function for backward compatibility.
    
    Returns:
        bool: True if at least one dataset is available
    """
    validator = DatasetValidator()
    return validator.check_all_datasets()


def check_config() -> bool:
    """Check if configuration is valid.
    
    Returns:
        bool: True if configuration loads successfully
    """
    try:
        # Test that we can access core configuration
        _ = config.default_dataset
        _ = config.get_all_datasets()
        print("✅ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False