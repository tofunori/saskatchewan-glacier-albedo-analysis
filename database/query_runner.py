#!/usr/bin/env python3
"""
Simple Query Runner for Saskatchewan Glacier Albedo Database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_connection

def run_query(sql):
    """Run a SQL query and display results"""
    conn = get_connection()
    try:
        result = conn.execute_query(sql)
        print(f"📊 Query Results ({len(result)} rows):")
        print("=" * 60)
        print(result.to_string(index=False))
        return result
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Query provided as command line argument
        query = " ".join(sys.argv[1:])
        run_query(query)
    else:
        # Interactive mode
        print("🗄️ Saskatchewan Glacier Albedo Database - Query Runner")
        print("Enter SQL queries (type 'exit' to quit):")
        print("Examples:")
        print("  SELECT COUNT(*) FROM albedo.mcd43a3_measurements;")
        print("  SELECT * FROM albedo.mcd43a3_measurements WHERE year = 2024 LIMIT 5;")
        print()
        
        while True:
            try:
                query = input("SQL> ").strip()
                if query.lower() in ['exit', 'quit', 'q']:
                    break
                if query:
                    run_query(query)
                    print()
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break