"""
Dashboard Components for Saskatchewan Glacier Albedo Analysis
==========================================================

Reusable components for the Streamlit dashboard.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Setup path
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))

class DataManager:
    """Data management functionality for the dashboard"""
    
    @staticmethod
    def load_data():
        """Load current dataset"""
        try:
            from config import CSV_PATH
            from data_handler import AlbedoDataHandler
            
            if not os.path.exists(CSV_PATH):
                return None
            
            handler = AlbedoDataHandler(CSV_PATH)
            handler.load_data()
            
            return handler.data
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return None
    
    @staticmethod
    def validate_csv_structure(df):
        """Validate CSV structure for albedo analysis"""
        
        required_columns = ['date', 'year', 'month']
        recommended_columns = ['doy', 'decimal_year', 'quality']
        
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check required columns
        missing_required = [col for col in required_columns if col not in df.columns]
        if missing_required:
            validation_results['errors'].append(f"Missing required columns: {', '.join(missing_required)}")
            validation_results['valid'] = False
        
        # Check recommended columns
        missing_recommended = [col for col in recommended_columns if col not in df.columns]
        if missing_recommended:
            validation_results['warnings'].append(f"Missing recommended columns: {', '.join(missing_recommended)}")
        
        # Check for fraction columns
        fraction_columns = [col for col in df.columns if '_mean' in col or '_median' in col]
        if not fraction_columns:
            validation_results['warnings'].append("No fraction columns found (expected columns like 'border_mean', 'mixed_low_mean', etc.)")
        
        # Check date format
        if 'date' in df.columns:
            try:
                pd.to_datetime(df['date'])
            except:
                validation_results['errors'].append("Date column is not in a valid datetime format")
                validation_results['valid'] = False
        
        # Check data types
        numeric_columns = ['year', 'month', 'doy'] + fraction_columns
        for col in numeric_columns:
            if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
                validation_results['warnings'].append(f"Column '{col}' should be numeric")
        
        return validation_results

class TrendAnalyzer:
    """Trend analysis functionality"""
    
    @staticmethod
    def calculate_basic_statistics(data, column):
        """Calculate basic statistics for a column"""
        
        if column not in data.columns:
            return None
        
        values = data[column].dropna()
        
        if len(values) == 0:
            return None
        
        stats = {
            'count': len(values),
            'mean': values.mean(),
            'median': values.median(),
            'std': values.std(),
            'min': values.min(),
            'max': values.max(),
            'q25': values.quantile(0.25),
            'q75': values.quantile(0.75)
        }
        
        return stats
    
    @staticmethod
    def simple_trend_test(data, column):
        """Simple trend analysis using linear regression"""
        
        if column not in data.columns:
            return None
        
        values = data[column].dropna()
        
        if len(values) < 10:
            return {'error': 'Insufficient data for trend analysis'}
        
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        
        # Simple trend classification
        if abs(slope) < 0.0001:
            trend_direction = 'Stable'
            trend_symbol = '➡️'
        elif slope > 0:
            trend_direction = 'Increasing'
            trend_symbol = '📈'
        else:
            trend_direction = 'Decreasing'
            trend_symbol = '📉'
        
        return {
            'slope': slope,
            'intercept': intercept,
            'direction': trend_direction,
            'symbol': trend_symbol,
            'annual_change': slope * 365 if len(values) > 365 else slope * len(values)
        }

class Visualizer:
    """Visualization functionality"""
    
    @staticmethod
    def create_time_series_plot(data, columns, title="Time Series"):
        """Create time series plot"""
        
        if 'date' not in data.columns:
            return None
        
        fig = go.Figure()
        
        for column in columns:
            if column in data.columns:
                values = data[column].dropna()
                dates = pd.to_datetime(data.loc[values.index, 'date'])
                
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=values,
                    mode='lines+markers',
                    name=column,
                    line=dict(width=2),
                    marker=dict(size=4)
                ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Albedo",
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    @staticmethod
    def create_monthly_boxplot(data, column, title="Monthly Distribution"):
        """Create monthly box plot"""
        
        if column not in data.columns or 'month' not in data.columns:
            return None
        
        month_names = {
            1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
            5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
            9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
        }
        
        # Filter out invalid months and prepare data
        valid_data = data[(data['month'] >= 1) & (data['month'] <= 12)].copy()
        valid_data['month_name'] = valid_data['month'].map(month_names)
        
        fig = px.box(
            valid_data,
            x='month_name',
            y=column,
            title=title,
            category_orders={'month_name': list(month_names.values())}
        )
        
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Albedo",
            template='plotly_white'
        )
        
        return fig
    
    @staticmethod
    def create_correlation_matrix(data, columns):
        """Create correlation matrix heatmap"""
        
        # Select only numeric columns that exist
        valid_columns = [col for col in columns if col in data.columns and pd.api.types.is_numeric_dtype(data[col])]
        
        if len(valid_columns) < 2:
            return None
        
        corr_matrix = data[valid_columns].corr()
        
        fig = px.imshow(
            corr_matrix,
            title="Correlation Matrix",
            color_continuous_scale="RdBu",
            aspect="auto"
        )
        
        fig.update_layout(
            template='plotly_white'
        )
        
        return fig

class GEEIntegration:
    """Google Earth Engine integration components"""
    
    @staticmethod
    def check_gee_status():
        """Check GEE installation and authentication status"""
        
        status = {
            'installed': False,
            'authenticated': False,
            'version': None,
            'error': None
        }
        
        try:
            from gee.client import GEEClient
            
            # Check installation
            install_info = GEEClient.check_installation()
            status['installed'] = install_info['installed']
            status['version'] = install_info.get('version', 'unknown')
            
            if status['installed']:
                # Try to create client (doesn't require full auth)
                client = GEEClient()
                status['client_created'] = True
            
        except Exception as e:
            status['error'] = str(e)
        
        return status
    
    @staticmethod
    def get_region_info():
        """Get configured region information"""
        
        try:
            from config import GEE_CONFIG
            
            regions = GEE_CONFIG.get('regions', {})
            return regions
            
        except Exception:
            return {}

class AnalysisRunner:
    """Analysis execution functionality"""
    
    @staticmethod
    def run_basic_analysis(data, variable='border'):
        """Run basic analysis for a variable"""
        
        try:
            from trend_calculator import TrendCalculator
            from data_handler import AlbedoDataHandler
            from config import CSV_PATH
            
            # Create handler with current data
            handler = AlbedoDataHandler(CSV_PATH)
            handler.data = data
            
            # Run trend calculation
            trend_calc = TrendCalculator(handler)
            results = trend_calc.calculate_basic_trends(variable)
            
            return results
            
        except Exception as e:
            st.error(f"Error running analysis: {str(e)}")
            return None
    
    @staticmethod
    def generate_summary_report(data, analysis_results=None):
        """Generate summary report"""
        
        report = {
            'timestamp': datetime.now(),
            'data_shape': data.shape,
            'date_range': None,
            'quality_summary': None,
            'fraction_columns': []
        }
        
        # Date range
        if 'date' in data.columns:
            dates = pd.to_datetime(data['date'])
            report['date_range'] = {
                'start': dates.min(),
                'end': dates.max(),
                'span_days': (dates.max() - dates.min()).days
            }
        
        # Quality summary
        if 'quality' in data.columns:
            report['quality_summary'] = {
                'total': len(data),
                'good_quality': (data['quality'] <= 1).sum(),
                'quality_percentage': ((data['quality'] <= 1).sum() / len(data)) * 100
            }
        
        # Fraction columns
        report['fraction_columns'] = [col for col in data.columns if '_mean' in col or '_median' in col]
        
        return report

def create_download_link(df, filename, text):
    """Create download link for dataframe"""
    
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def format_number(value, decimals=4):
    """Format number for display"""
    
    if pd.isna(value):
        return "N/A"
    
    if isinstance(value, (int, float)):
        return f"{value:.{decimals}f}"
    
    return str(value)

def show_progress_bar(current, total, text="Progress"):
    """Show progress bar"""
    
    progress = current / total if total > 0 else 0
    st.progress(progress, text=f"{text}: {current}/{total}")

def display_metric_card(title, value, delta=None, help_text=None):
    """Display a metric card"""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.metric(title, value, delta=delta, help=help_text)
    
    return col2  # Return second column for additional content

def create_info_expander(title, content, expanded=False):
    """Create info expander with content"""
    
    with st.expander(title, expanded=expanded):
        if isinstance(content, dict):
            for key, value in content.items():
                st.text(f"{key}: {value}")
        elif isinstance(content, list):
            for item in content:
                st.text(f"• {item}")
        else:
            st.text(content)