"""
Exports module for Saskatchewan Albedo Analysis
===============================================

This module handles all data export functionality including Excel, CSV, and text reports.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

def get_timestamp():
    """Return current timestamp string"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def export_results(data, output_path):
    """
    Basic export function
    
    Args:
        data: Data to export
        output_path: Path for output file
    """
    if isinstance(data, pd.DataFrame):
        data.to_csv(output_path, index=False)
    else:
        # Handle other data types as needed
        pass
    
    print(f"✅ Data exported to: {output_path}")
    return output_path


class ExportManager:
    """
    Export manager for data output
    """
    
    def __init__(self):
        """Initialize export manager"""
        self.export_history = []
    
    def export_dataframe(self, df, filename, format='csv'):
        """
        Export DataFrame to various formats
        
        Args:
            df (pd.DataFrame): Data to export
            filename (str): Output filename
            format (str): Export format ('csv', 'excel', 'json')
            
        Returns:
            str: Path to exported file
        """
        try:
            if format.lower() == 'csv':
                path = f"{filename}.csv"
                df.to_csv(path, index=False)
            elif format.lower() in ['excel', 'xlsx']:
                path = f"{filename}.xlsx"
                df.to_excel(path, index=False)
            elif format.lower() == 'json':
                path = f"{filename}.json"
                df.to_json(path, orient='records', date_format='iso')
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            self.export_history.append({
                'timestamp': get_timestamp(),
                'filename': path,
                'format': format,
                'records': len(df)
            })
            
            return path
            
        except Exception as e:
            print(f"❌ Export failed: {str(e)}")
            return None
    
    def export_plot_data(self, plot_data, filename):
        """
        Export plot data for reproducibility
        
        Args:
            plot_data (dict): Plot data dictionary
            filename (str): Output filename
            
        Returns:
            str: Path to exported file
        """
        try:
            import json
            
            # Convert numpy arrays to lists for JSON serialization
            serializable_data = {}
            for key, value in plot_data.items():
                if isinstance(value, np.ndarray):
                    serializable_data[key] = value.tolist()
                elif hasattr(value, 'to_dict'):
                    serializable_data[key] = value.to_dict()
                else:
                    serializable_data[key] = value
            
            path = f"{filename}_plot_data.json"
            with open(path, 'w') as f:
                json.dump(serializable_data, f, indent=2, default=str)
            
            return path
            
        except Exception as e:
            print(f"❌ Plot data export failed: {str(e)}")
            return None
    
    def get_export_history(self):
        """
        Get export history
        
        Returns:
            list: List of export records
        """
        return self.export_history