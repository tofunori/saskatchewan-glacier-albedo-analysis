"""
Database connection module for Saskatchewan Glacier Albedo Analysis
================================================================

This module provides database connection and utility functions for
working with PostgreSQL instead of CSV files.
"""

import os
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import Optional, Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    Manages PostgreSQL database connections for the albedo analysis project
    """
    
    def __init__(self, 
                 database: str = "saskatchewan_albedo",
                 user: Optional[str] = None,
                 password: Optional[str] = None,
                 host: str = "localhost",
                 port: int = 5432):
        """
        Initialize database connection
        
        Args:
            database: Database name
            user: Username (defaults to current system user)
            password: Password (defaults to None for peer authentication)
            host: Database host
            port: Database port
        """
        self.database = database
        self.user = user or os.getenv('USER')
        self.password = password
        self.host = host
        self.port = port
        self._engine: Optional[Engine] = None
        
    @property
    def connection_string(self) -> str:
        """Generate SQLAlchemy connection string"""
        if self.password:
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            # Use socket connection for peer authentication
            return f"postgresql:///{self.database}"
    
    @property
    def engine(self) -> Engine:
        """Get or create SQLAlchemy engine"""
        if self._engine is None:
            self._engine = create_engine(self.connection_string)
            logger.info(f"Created database engine for {self.database}")
        return self._engine
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return result.fetchone()[0] == 1
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            pandas.DataFrame: Query results
        """
        try:
            return pd.read_sql(query, self.engine, params=params)
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_statement(self, statement: str, params: Optional[Dict] = None) -> None:
        """
        Execute a SQL statement (INSERT, UPDATE, DELETE, etc.)
        
        Args:
            statement: SQL statement string
            params: Statement parameters
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text(statement), params or {})
                conn.commit()
        except Exception as e:
            logger.error(f"Statement execution failed: {e}")
            raise
    
    def insert_dataframe(self, df: pd.DataFrame, table_name: str, 
                        schema: str = "albedo", if_exists: str = "append") -> None:
        """
        Insert DataFrame into database table
        
        Args:
            df: DataFrame to insert
            table_name: Target table name
            schema: Database schema
            if_exists: What to do if table exists ('fail', 'replace', 'append')
        """
        try:
            df.to_sql(table_name, self.engine, schema=schema, 
                     if_exists=if_exists, index=False, method='multi')
            logger.info(f"Inserted {len(df)} rows into {schema}.{table_name}")
        except Exception as e:
            logger.error(f"Failed to insert data into {schema}.{table_name}: {e}")
            raise
    
    def get_table_info(self, table_name: str, schema: str = "albedo") -> Dict[str, Any]:
        """
        Get information about a table
        
        Args:
            table_name: Table name
            schema: Schema name
            
        Returns:
            dict: Table information
        """
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_schema = %(schema)s 
        AND table_name = %(table)s
        ORDER BY ordinal_position;
        """
        
        columns_df = self.execute_query(query, {'schema': schema, 'table': table_name})
        
        count_query = f"SELECT COUNT(*) as row_count FROM {schema}.{table_name}"
        count_df = self.execute_query(count_query)
        
        return {
            'columns': columns_df.to_dict('records'),
            'row_count': count_df.iloc[0]['row_count'],
            'schema': schema,
            'table': table_name
        }
    
    def close(self):
        """Close database engine"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            logger.info("Database engine closed")

# Global database connection instance
db_connection = DatabaseConnection()

def get_connection() -> DatabaseConnection:
    """Get the global database connection instance"""
    return db_connection

def test_database_setup() -> bool:
    """Test that database is properly set up with required tables"""
    try:
        conn = get_connection()
        
        # Test connection
        if not conn.test_connection():
            logger.error("Database connection failed")
            return False
        
        # Check for required tables
        required_tables = [
            'mcd43a3_measurements',
            'mod10a1_measurements', 
            'mcd43a3_quality',
            'mod10a1_quality'
        ]
        
        for table in required_tables:
            try:
                info = conn.get_table_info(table)
                logger.info(f"Table {table}: {info['row_count']} rows")
            except Exception as e:
                logger.error(f"Table {table} not found or accessible: {e}")
                return False
        
        logger.info("Database setup test passed")
        return True
        
    except Exception as e:
        logger.error(f"Database setup test failed: {e}")
        return False

if __name__ == "__main__":
    # Test the database connection
    print("Testing database setup...")
    success = test_database_setup()
    print(f"Database test: {'PASSED' if success else 'FAILED'}")