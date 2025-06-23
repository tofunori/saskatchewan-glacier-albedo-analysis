#!/usr/bin/env python3
"""
Quick Database Viewer - Simple queries for Saskatchewan Glacier Albedo Database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_connection

def quick_stats():
    """Show quick database statistics"""
    conn = get_connection()
    
    print("🗄️ Saskatchewan Glacier Albedo Database - Quick Stats")
    print("=" * 60)
    
    # Table counts
    tables = [
        ('mcd43a3_measurements', 'MCD43A3 Albedo Data'),
        ('mod10a1_measurements', 'MOD10A1 Snow Albedo'),
        ('mcd43a3_quality', 'MCD43A3 Quality'),
        ('mod10a1_quality', 'MOD10A1 Quality')
    ]
    
    for table, desc in tables:
        query = f"SELECT COUNT(*) as count FROM albedo.{table}"
        result = conn.execute_query(query)
        count = result.iloc[0]['count']
        print(f"📊 {desc}: {count:,} rows")
    
    # Date ranges
    print("\n📅 Data Coverage:")
    for table in ['mcd43a3_measurements', 'mod10a1_measurements']:
        query = f"""
        SELECT 
            MIN(date) as start_date,
            MAX(date) as end_date,
            COUNT(DISTINCT year) as years
        FROM albedo.{table}
        """
        result = conn.execute_query(query)
        row = result.iloc[0]
        dataset = table.split('_')[0].upper()
        print(f"  {dataset}: {row['start_date']} to {row['end_date']} ({row['years']} years)")
    
    # Recent albedo values
    print("\n❄️ Recent Albedo Values (Pure Ice):")
    query = """
    SELECT date, pure_ice_mean, season
    FROM albedo.mcd43a3_measurements 
    WHERE pure_ice_mean IS NOT NULL
    ORDER BY date DESC 
    LIMIT 5
    """
    result = conn.execute_query(query)
    for _, row in result.iterrows():
        print(f"  {row['date']}: {row['pure_ice_mean']:.3f} ({row['season']})")

if __name__ == "__main__":
    quick_stats()