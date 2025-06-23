#!/usr/bin/env python3
"""
Saskatchewan Glacier Albedo Database Explorer
===========================================

Interactive tool to explore the PostgreSQL database data.
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_connection
from utils.helpers import print_section_header

class DatabaseExplorer:
    """Interactive database explorer"""
    
    def __init__(self):
        self.conn = get_connection()
        self.tables = {
            '1': ('mcd43a3_measurements', 'MCD43A3 Albedo Measurements'),
            '2': ('mod10a1_measurements', 'MOD10A1 Snow Albedo Measurements'),
            '3': ('mcd43a3_quality', 'MCD43A3 Quality Distribution'),
            '4': ('mod10a1_quality', 'MOD10A1 Quality Distribution')
        }
    
    def show_menu(self):
        """Display main menu"""
        print_section_header("Saskatchewan Glacier Albedo Database Explorer", level=1)
        print("📊 Choose a table to explore:")
        for key, (table, desc) in self.tables.items():
            print(f"  {key}. {desc}")
        print("  5. Custom SQL Query")
        print("  6. Database Summary")
        print("  0. Exit")
        print()
    
    def get_table_overview(self, table_name):
        """Get overview of a table"""
        print_section_header(f"Table: {table_name}", level=2)
        
        # Row count
        count_query = f"SELECT COUNT(*) as count FROM albedo.{table_name}"
        count_df = self.conn.execute_query(count_query)
        row_count = count_df.iloc[0]['count']
        print(f"📊 Total rows: {row_count:,}")
        
        # Date range for measurement tables
        if 'measurements' in table_name:
            date_query = f"""
            SELECT 
                MIN(date) as min_date,
                MAX(date) as max_date,
                COUNT(DISTINCT year) as years,
                COUNT(DISTINCT date) as unique_dates
            FROM albedo.{table_name}
            """
            date_df = self.conn.execute_query(date_query)
            print(f"📅 Date range: {date_df.iloc[0]['min_date']} to {date_df.iloc[0]['max_date']}")
            print(f"🗓️  Years covered: {date_df.iloc[0]['years']}")
            print(f"📆 Unique dates: {date_df.iloc[0]['unique_dates']}")
        
        # Column info
        columns_query = f"""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_schema = 'albedo' AND table_name = '{table_name}'
        ORDER BY ordinal_position
        """
        columns_df = self.conn.execute_query(columns_query)
        print(f"\n📋 Columns ({len(columns_df)}):")
        for _, row in columns_df.head(10).iterrows():
            nullable = "NULL" if row['is_nullable'] == 'YES' else "NOT NULL"
            print(f"  • {row['column_name']} ({row['data_type']}) - {nullable}")
        
        if len(columns_df) > 10:
            print(f"  ... and {len(columns_df) - 10} more columns")
    
    def show_sample_data(self, table_name, limit=5):
        """Show sample data from table"""
        print(f"\n🔍 Sample data (first {limit} rows):")
        
        if 'measurements' in table_name:
            # Show key columns for measurements
            query = f"""
            SELECT 
                date, year, season,
                pure_ice_mean, mostly_ice_mean, mixed_high_mean,
                total_valid_pixels
            FROM albedo.{table_name}
            ORDER BY date
            LIMIT {limit}
            """
        else:
            # Show all columns for quality tables (smaller)
            query = f"SELECT * FROM albedo.{table_name} ORDER BY date LIMIT {limit}"
        
        df = self.conn.execute_query(query)
        print(df.to_string(index=False))
    
    def explore_table(self, table_name):
        """Explore a specific table"""
        self.get_table_overview(table_name)
        self.show_sample_data(table_name)
        
        while True:
            print(f"\n🔧 Table '{table_name}' options:")
            print("  1. Show more sample data")
            print("  2. Filter by year")
            print("  3. Albedo statistics by fraction")
            print("  4. Monthly distribution")
            print("  5. Export to CSV")
            print("  0. Back to main menu")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                limit = input("How many rows? (default 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                self.show_sample_data(table_name, limit)
            elif choice == '2':
                self.filter_by_year(table_name)
            elif choice == '3' and 'measurements' in table_name:
                self.show_albedo_stats(table_name)
            elif choice == '4':
                self.show_monthly_distribution(table_name)
            elif choice == '5':
                self.export_table(table_name)
            else:
                print("❌ Invalid choice")
    
    def filter_by_year(self, table_name):
        """Filter data by year"""
        year = input("Enter year (2010-2024): ").strip()
        if not year.isdigit() or int(year) < 2010 or int(year) > 2024:
            print("❌ Invalid year")
            return
        
        year = int(year)
        query = f"""
        SELECT date, season, 
               pure_ice_mean, pure_ice_pixel_count,
               mostly_ice_mean, mostly_ice_pixel_count,
               mixed_high_mean, mixed_high_pixel_count,
               total_valid_pixels
        FROM albedo.{table_name} 
        WHERE year = {year}
        ORDER BY date
        """
        
        print(f"\n📅 Data for year {year}:")
        df = self.conn.execute_query(query)
        if len(df) > 0:
            print(df.to_string(index=False))
            print(f"\nTotal observations in {year}: {len(df)}")
        else:
            print(f"No data found for year {year}")
    
    def show_albedo_stats(self, table_name):
        """Show albedo statistics by fraction"""
        query = f"""
        SELECT 
            AVG(border_mean) as border_avg,
            AVG(mixed_low_mean) as mixed_low_avg,
            AVG(mixed_high_mean) as mixed_high_avg,
            AVG(mostly_ice_mean) as mostly_ice_avg,
            AVG(pure_ice_mean) as pure_ice_avg,
            COUNT(*) as total_obs
        FROM albedo.{table_name}
        WHERE border_mean IS NOT NULL
        """
        
        print(f"\n📊 Average albedo by fraction:")
        df = self.conn.execute_query(query)
        for col in df.columns:
            if col != 'total_obs':
                fraction = col.replace('_avg', '').replace('_', ' ').title()
                value = df.iloc[0][col]
                if value is not None:
                    print(f"  • {fraction}: {value:.3f}")
        print(f"  • Total observations: {df.iloc[0]['total_obs']:,}")
    
    def show_monthly_distribution(self, table_name):
        """Show data distribution by month"""
        query = f"""
        SELECT 
            EXTRACT(MONTH FROM date) as month,
            COUNT(*) as observations,
            MIN(date) as first_date,
            MAX(date) as last_date
        FROM albedo.{table_name}
        GROUP BY EXTRACT(MONTH FROM date)
        ORDER BY month
        """
        
        print(f"\n📅 Monthly distribution:")
        df = self.conn.execute_query(query)
        month_names = {6: 'June', 7: 'July', 8: 'August', 9: 'September'}
        
        for _, row in df.iterrows():
            month_num = int(row['month'])
            month_name = month_names.get(month_num, f"Month {month_num}")
            print(f"  • {month_name}: {row['observations']:,} observations")
            print(f"    Range: {row['first_date']} to {row['last_date']}")
    
    def export_table(self, table_name):
        """Export table to CSV"""
        filename = f"{table_name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        print("📊 Export options:")
        print("  1. Full table")
        print("  2. Recent data (last 100 rows)")
        print("  3. Specific year")
        
        choice = input("Choose export option: ").strip()
        
        if choice == '1':
            query = f"SELECT * FROM albedo.{table_name} ORDER BY date"
        elif choice == '2':
            query = f"SELECT * FROM albedo.{table_name} ORDER BY date DESC LIMIT 100"
        elif choice == '3':
            year = input("Enter year: ").strip()
            if year.isdigit():
                query = f"SELECT * FROM albedo.{table_name} WHERE year = {year} ORDER BY date"
            else:
                print("❌ Invalid year")
                return
        else:
            print("❌ Invalid choice")
            return
        
        try:
            df = self.conn.execute_query(query)
            df.to_csv(filename, index=False)
            print(f"✅ Exported {len(df)} rows to {filename}")
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    def custom_query(self):
        """Execute custom SQL query"""
        print_section_header("Custom SQL Query", level=2)
        print("💡 Examples:")
        print("  SELECT * FROM albedo.mcd43a3_measurements WHERE year = 2024 LIMIT 10;")
        print("  SELECT AVG(pure_ice_mean) FROM albedo.mcd43a3_measurements WHERE season = 'mid_summer';")
        print()
        
        query = input("Enter your SQL query: ").strip()
        if not query:
            return
        
        try:
            df = self.conn.execute_query(query)
            print(f"\n📊 Query result ({len(df)} rows):")
            if len(df) > 0:
                print(df.to_string(index=False))
            else:
                print("No results returned")
        except Exception as e:
            print(f"❌ Query failed: {e}")
    
    def database_summary(self):
        """Show overall database summary"""
        print_section_header("Database Summary", level=2)
        
        for table_name, description in [
            ('mcd43a3_measurements', 'MCD43A3 Albedo Measurements'),
            ('mod10a1_measurements', 'MOD10A1 Snow Albedo'),
            ('mcd43a3_quality', 'MCD43A3 Quality'),
            ('mod10a1_quality', 'MOD10A1 Quality')
        ]:
            count_query = f"SELECT COUNT(*) as count FROM albedo.{table_name}"
            count_df = self.conn.execute_query(count_query)
            count = count_df.iloc[0]['count']
            print(f"📊 {description}: {count:,} rows")
    
    def run(self):
        """Main explorer loop"""
        while True:
            self.show_menu()
            choice = input("Enter your choice: ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice in self.tables:
                table_name, description = self.tables[choice]
                self.explore_table(table_name)
            elif choice == '5':
                self.custom_query()
            elif choice == '6':
                self.database_summary()
            else:
                print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    explorer = DatabaseExplorer()
    explorer.run()