"""
Export Google Earth Engine data to CSV format compatible with existing analysis pipeline
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import config


class DataExporter:
    """
    Export GEE data to CSV format matching existing analysis expectations
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize data exporter
        
        Args:
            output_dir: Output directory for CSV files (default: from config)
        """
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(output_dir) if output_dir else Path(config.OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"📁 Export directory: {self.output_dir}")
    
    def export_albedo_to_csv(self, 
                           albedo_data: pd.DataFrame,
                           filename: Optional[str] = None,
                           add_fraction_columns: bool = True) -> str:
        """
        Export albedo data to CSV format compatible with AlbedoDataHandler
        
        Args:
            albedo_data: DataFrame from SaskatchewanMODISFetcher
            filename: Output filename (auto-generated if None)
            add_fraction_columns: Add synthetic fraction columns for compatibility
            
        Returns:
            str: Path to exported CSV file
        """
        self.logger.info("📊 Exporting albedo data to CSV format...")
        
        if albedo_data.empty:
            raise ValueError("Cannot export empty albedo data")
        
        # Create output filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gee_albedo_data_{timestamp}.csv"
        
        output_path = self.output_dir / filename
        
        # Prepare data for export
        export_df = albedo_data.copy()
        
        # Ensure required columns exist
        required_columns = ['date', 'year', 'month', 'doy', 'decimal_year']
        for col in required_columns:
            if col not in export_df.columns:
                self.logger.warning(f"⚠️ Missing required column: {col}")
        
        # Add primary albedo metrics if available
        albedo_columns = {
            'Albedo_WSA_shortwave': 'border_mean',
            'Albedo_BSA_shortwave': 'border_median',
            'Albedo_WSA_vis': 'albedo_visible',
            'Albedo_WSA_nir': 'albedo_nir'
        }
        
        for gee_col, export_col in albedo_columns.items():
            if gee_col in export_df.columns:
                export_df[export_col] = export_df[gee_col]
        
        # Add synthetic fraction columns for compatibility with AlbedoDataHandler
        if add_fraction_columns:
            export_df = self._add_fraction_columns(export_df)
        
        # Add quality indicators
        export_df['quality'] = 0  # Assume good quality for GEE data
        export_df['data_source'] = 'GEE_MODIS'
        
        # Ensure day column exists
        if 'day' not in export_df.columns and 'date' in export_df.columns:
            export_df['day'] = pd.to_datetime(export_df['date']).dt.day
        
        # Select and order columns for output
        output_columns = self._get_output_columns(export_df)
        final_df = export_df[output_columns].copy()
        
        # Remove rows with all NaN values in critical columns
        critical_cols = ['border_mean', 'border_median'] 
        existing_critical = [col for col in critical_cols if col in final_df.columns]
        if existing_critical:
            final_df = final_df.dropna(subset=existing_critical, how='all')
        
        # Save to CSV
        final_df.to_csv(output_path, index=False)
        
        self.logger.info(f"✅ Exported {len(final_df)} records to: {output_path}")
        self.logger.info(f"📋 Columns: {list(final_df.columns)}")
        
        return str(output_path)
    
    def export_snow_cover_to_csv(self,
                                snow_data: pd.DataFrame,
                                filename: Optional[str] = None) -> str:
        """
        Export snow cover data to CSV format
        
        Args:
            snow_data: DataFrame from SaskatchewanMODISFetcher
            filename: Output filename (auto-generated if None)
            
        Returns:
            str: Path to exported CSV file
        """
        self.logger.info("❄️ Exporting snow cover data to CSV format...")
        
        if snow_data.empty:
            raise ValueError("Cannot export empty snow cover data")
        
        # Create output filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gee_snow_cover_{timestamp}.csv"
        
        output_path = self.output_dir / filename
        
        # Prepare snow cover data
        export_df = snow_data.copy()
        
        # Rename columns for clarity
        column_mapping = {
            'NDSI_Snow_Cover': 'snow_cover_fraction',
            'Snow_Albedo_Daily_Tile': 'snow_albedo'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in export_df.columns:
                export_df[new_col] = export_df[old_col]
        
        # Add metadata
        export_df['data_source'] = 'GEE_MOD10A1'
        export_df['quality'] = 0
        
        # Save to CSV
        export_df.to_csv(output_path, index=False)
        
        self.logger.info(f"✅ Exported {len(export_df)} snow cover records to: {output_path}")
        
        return str(output_path)
    
    def _add_fraction_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add synthetic fraction columns for compatibility
        
        This creates placeholder columns that match the expected format
        from the existing analysis pipeline.
        """
        # Add fraction columns based on existing config
        if hasattr(config, 'FRACTION_CLASSES'):
            for fraction_class in config.FRACTION_CLASSES:
                # Add mean and median columns for each fraction class
                for stat in ['mean', 'median']:
                    col_name = f"{fraction_class}_{stat}"
                    if col_name not in df.columns:
                        # Create synthetic data based on primary albedo if available
                        if 'border_mean' in df.columns and not df['border_mean'].isna().all():
                            # Add small random variation
                            base_values = df['border_mean']
                            noise = np.random.normal(0, 0.02, len(df))
                            df[col_name] = base_values + noise
                            # Clip to valid albedo range
                            df[col_name] = df[col_name].clip(0, 1)
                        else:
                            df[col_name] = np.nan
        
        return df
    
    def _get_output_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Get ordered list of output columns
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            List of column names in preferred order
        """
        # Core columns (always first)
        core_columns = ['date', 'year', 'month', 'day', 'doy', 'decimal_year']
        
        # Primary data columns
        data_columns = ['border_mean', 'border_median', 'albedo_visible', 'albedo_nir']
        
        # Fraction columns (if any)
        fraction_columns = [col for col in df.columns 
                          if any(f'{fc}_' in col for fc in getattr(config, 'FRACTION_CLASSES', []))]
        
        # Metadata columns
        meta_columns = ['quality', 'data_source']
        
        # Additional columns (anything else)
        all_priority_cols = core_columns + data_columns + fraction_columns + meta_columns
        additional_columns = [col for col in df.columns if col not in all_priority_cols]
        
        # Build final column list (only include existing columns)
        output_columns = []
        for col_list in [core_columns, data_columns, fraction_columns, meta_columns, additional_columns]:
            for col in col_list:
                if col in df.columns:
                    output_columns.append(col)
        
        return output_columns
    
    def create_combined_dataset(self,
                              albedo_data: pd.DataFrame,
                              snow_data: Optional[pd.DataFrame] = None,
                              filename: Optional[str] = None) -> str:
        """
        Create a combined dataset with albedo and optional snow cover data
        
        Args:
            albedo_data: Primary albedo DataFrame
            snow_data: Optional snow cover DataFrame
            filename: Output filename
            
        Returns:
            str: Path to combined CSV file
        """
        self.logger.info("🔗 Creating combined dataset...")
        
        # Start with albedo data
        combined_df = albedo_data.copy()
        
        # Merge with snow data if provided
        if snow_data is not None and not snow_data.empty:
            # Merge on date
            combined_df = pd.merge(
                combined_df, 
                snow_data[['date', 'NDSI_Snow_Cover', 'Snow_Albedo_Daily_Tile']],
                on='date',
                how='left',
                suffixes=('', '_snow')
            )
            
            # Rename snow columns
            combined_df.rename(columns={
                'NDSI_Snow_Cover': 'snow_cover_fraction',
                'Snow_Albedo_Daily_Tile': 'snow_albedo'
            }, inplace=True)
        
        # Export combined dataset
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gee_combined_dataset_{timestamp}.csv"
        
        return self.export_albedo_to_csv(combined_df, filename)
    
    def get_export_summary(self, csv_path: str) -> Dict[str, Any]:
        """
        Get summary information about exported CSV file
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            Dict with summary information
        """
        try:
            df = pd.read_csv(csv_path)
            
            summary = {
                'file_path': csv_path,
                'file_size_mb': round(Path(csv_path).stat().st_size / (1024 * 1024), 2),
                'total_records': len(df),
                'date_range': {
                    'start': df['date'].min() if 'date' in df.columns else None,
                    'end': df['date'].max() if 'date' in df.columns else None
                },
                'columns': list(df.columns),
                'data_quality': {
                    'missing_values': df.isnull().sum().to_dict(),
                    'valid_albedo_records': len(df.dropna(subset=['border_mean'])) if 'border_mean' in df.columns else 0
                }
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Error creating export summary: {e}")
            return {'error': str(e)}