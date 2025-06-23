"""
CSV to PostgreSQL Import Script
==============================

This script imports the existing CSV files into PostgreSQL database tables.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_connection
from utils.helpers import print_section_header

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_csv_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean CSV data for database import
    
    Args:
        df: Raw DataFrame from CSV
        
    Returns:
        pd.DataFrame: Cleaned DataFrame
    """
    # Remove problematic columns
    df_clean = df.copy()
    
    # Remove system:index and .geo columns if they exist (they're not useful for analysis)
    columns_to_drop = ['system:index', '.geo']
    for col in columns_to_drop:
        if col in df_clean.columns:
            df_clean = df_clean.drop(columns=[col])
    
    # Rename system:time_start to system_time_start
    if 'system:time_start' in df_clean.columns:
        df_clean = df_clean.rename(columns={'system:time_start': 'system_time_start'})
    
    # Convert date to proper format
    if 'date' in df_clean.columns:
        df_clean['date'] = pd.to_datetime(df_clean['date'])
    
    # Replace empty strings and 'null' with None
    df_clean = df_clean.replace(['', 'null', 'NULL'], None)
    
    # Convert numeric columns
    numeric_cols = [col for col in df_clean.columns if any(x in col.lower() for x in 
                   ['mean', 'median', 'quality', 'pixel', 'decimal', 'doy', 'year', 'threshold'])]
    
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Handle boolean columns
    if 'min_pixels_threshold' in df_clean.columns:
        df_clean['min_pixels_threshold'] = df_clean['min_pixels_threshold'].astype('Int64')
    
    return df_clean

def import_csv_file(csv_path: str, table_name: str, schema: str = "albedo") -> bool:
    """
    Import a single CSV file into PostgreSQL
    
    Args:
        csv_path: Path to CSV file
        table_name: Target table name
        schema: Database schema
        
    Returns:
        bool: Success status
    """
    try:
        print_section_header(f"Importing {Path(csv_path).name}", level=2)
        
        # Read CSV
        logger.info(f"Reading CSV: {csv_path}")
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} rows from CSV")
        
        # Clean data
        df_clean = clean_csv_data(df)
        logger.info(f"Cleaned data: {len(df_clean)} rows ready for import")
        
        # Import to database
        conn = get_connection()
        # First clear the table (since we can't drop due to views)
        if table_name in ['mcd43a3_measurements', 'mod10a1_measurements']:
            clear_query = f"DELETE FROM {schema}.{table_name}"
            conn.execute_statement(clear_query)
            logger.info(f"Cleared existing data from {schema}.{table_name}")
        
        conn.insert_dataframe(df_clean, table_name, schema=schema, if_exists='append')
        
        # Verify import
        info = conn.get_table_info(table_name, schema)
        logger.info(f"Import successful: {info['row_count']} rows in {schema}.{table_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to import {csv_path}: {e}")
        return False

def import_all_csv_files():
    """Import all CSV files to PostgreSQL"""
    print_section_header("CSV to PostgreSQL Import", level=1)
    
    # Define file mappings
    csv_files = [
        {
            'path': 'data/csv/MCD43A3_albedo_daily_stats_2010_2024.csv',
            'table': 'mcd43a3_measurements',
            'description': 'MCD43A3 Albedo Measurements'
        },
        {
            'path': 'data/csv/MOD10A1_snow_daily_stats_2010_2024.csv',
            'table': 'mod10a1_measurements',
            'description': 'MOD10A1 Snow Albedo Measurements'
        },
        {
            'path': 'data/csv/MCD43A3_quality_distribution_daily_2010_2024.csv',
            'table': 'mcd43a3_quality',
            'description': 'MCD43A3 Quality Distribution'
        },
        {
            'path': 'data/csv/MOD10A1_quality_daily_2010_2024.csv',
            'table': 'mod10a1_quality',
            'description': 'MOD10A1 Quality Distribution'
        }
    ]
    
    success_count = 0
    total_count = len(csv_files)
    
    for file_info in csv_files:
        csv_path = file_info['path']
        table_name = file_info['table']
        description = file_info['description']
        
        print(f"\n📁 Processing: {description}")
        
        if Path(csv_path).exists():
            success = import_csv_file(csv_path, table_name)
            if success:
                success_count += 1
                print(f"✅ {description} imported successfully")
            else:
                print(f"❌ {description} import failed")
        else:
            print(f"⚠️  File not found: {csv_path}")
    
    print_section_header("Import Summary", level=2)
    print(f"📊 Successfully imported: {success_count}/{total_count} files")
    
    if success_count == total_count:
        print("🎉 All CSV files imported successfully!")
        return True
    else:
        print("⚠️  Some imports failed. Check logs for details.")
        return False

def verify_import():
    """Verify that data was imported correctly"""
    print_section_header("Import Verification", level=2)
    
    conn = get_connection()
    tables = ['mcd43a3_measurements', 'mod10a1_measurements', 'mcd43a3_quality', 'mod10a1_quality']
    
    for table in tables:
        try:
            info = conn.get_table_info(table)
            print(f"📊 {table}: {info['row_count']:,} rows")
            
            # Show date range for measurements tables
            if 'measurements' in table:
                query = f"SELECT MIN(date) as min_date, MAX(date) as max_date FROM albedo.{table}"
                date_info = conn.execute_query(query)
                min_date = date_info.iloc[0]['min_date']
                max_date = date_info.iloc[0]['max_date']
                print(f"   📅 Date range: {min_date} to {max_date}")
                
        except Exception as e:
            print(f"❌ Error checking {table}: {e}")

if __name__ == "__main__":
    # Run the import
    print("🚀 Starting CSV to PostgreSQL import...")
    
    # Test database connection first
    conn = get_connection()
    if not conn.test_connection():
        print("❌ Database connection failed. Please check your PostgreSQL setup.")
        exit(1)
    
    # Import all files
    success = import_all_csv_files()
    
    if success:
        print("\n🔍 Verifying import...")
        verify_import()
        print("\n✅ Import completed successfully!")
    else:
        print("\n❌ Import completed with errors.")
        exit(1)