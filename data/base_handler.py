"""
Base data handler with modern patterns and error handling.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import pandas as pd
from pathlib import Path
import logging

from utils.exceptions import DataLoadError, ConfigurationError
from config.settings import config

logger = logging.getLogger(__name__)


class BaseDataHandler(ABC):
    """Abstract base class for data handlers."""
    
    def __init__(self, dataset_name: str):
        """Initialize base data handler.
        
        Args:
            dataset_name: Name of the dataset
            
        Raises:
            ConfigurationError: If dataset configuration is invalid
        """
        self.dataset_name = dataset_name
        self.dataset_config = config.get_dataset_config(dataset_name)
        
        if not self.dataset_config:
            raise ConfigurationError(f"No configuration found for dataset: {dataset_name}")
        
        self._data: Optional[pd.DataFrame] = None
        self._raw_data: Optional[pd.DataFrame] = None
        self._metadata: Dict[str, Any] = {}
    
    @property
    def data(self) -> Optional[pd.DataFrame]:
        """Get processed data."""
        return self._data
    
    @property
    def raw_data(self) -> Optional[pd.DataFrame]:
        """Get raw data."""
        return self._raw_data
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get data metadata."""
        return self._metadata
    
    def __len__(self) -> int:
        """Return number of observations."""
        return len(self._data) if self._data is not None else 0
    
    @abstractmethod
    def load_data(self) -> 'BaseDataHandler':
        """Load and process data. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def validate_data(self) -> bool:
        """Validate loaded data. Must be implemented by subclasses."""
        pass
    
    def _check_file_exists(self, file_path: str) -> Path:
        """Check if file exists and return Path object.
        
        Args:
            file_path: Path to file
            
        Returns:
            Path object
            
        Raises:
            DataLoadError: If file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            raise DataLoadError(f"File not found: {file_path}")
        return path
    
    def _load_csv_safely(self, file_path: str, **kwargs) -> pd.DataFrame:
        """Safely load CSV file with error handling.
        
        Args:
            file_path: Path to CSV file
            **kwargs: Additional arguments for pd.read_csv
            
        Returns:
            DataFrame with loaded data
            
        Raises:
            DataLoadError: If CSV loading fails
        """
        try:
            path = self._check_file_exists(file_path)
            logger.info(f"Loading CSV: {path}")
            
            df = pd.read_csv(path, **kwargs)
            logger.info(f"Loaded {len(df)} rows from {path}")
            
            return df
            
        except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
            raise DataLoadError(f"Failed to parse CSV {file_path}: {e}")
        except Exception as e:
            raise DataLoadError(f"Unexpected error loading {file_path}: {e}")
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for the dataset."""
        if self._data is None:
            return {}
        
        numeric_cols = self._data.select_dtypes(include=['number']).columns
        stats = {}
        
        for col in numeric_cols:
            stats[col] = {
                'count': self._data[col].count(),
                'mean': self._data[col].mean(),
                'std': self._data[col].std(),
                'min': self._data[col].min(),
                'max': self._data[col].max(),
                'null_count': self._data[col].isnull().sum()
            }
        
        return stats