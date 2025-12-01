import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
from typing import Optional, Dict, Any, List
import streamlit as st
from config import Config

class DatabaseManager:
    def __init__(self):
        self.config = Config()
        self.engine = None
        self.connection = None
        
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.engine = create_engine(self.config.DATABASE_URL)
            self.connection = self.engine.connect()
            return True
        except Exception as e:
            st.error(f"Database connection failed: {str(e)}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
    
    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """Execute SQL query and return results as DataFrame"""
        try:
            if not self.connection:
                if not self.connect():
                    return None
            
            result = pd.read_sql_query(text(query), self.connection)
            return result
        except Exception as e:
            st.error(f"Query execution failed: {str(e)}")
            return None
    
    def get_table_schema(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get table schema information"""
        try:
            if self.config.DATABASE_TYPE == "sqlite":
                schema_query = f"PRAGMA table_info({table_name})"
            elif self.config.DATABASE_TYPE == "mysql":
                schema_query = f"DESCRIBE {table_name}"
            elif self.config.DATABASE_TYPE == "postgresql":
                schema_query = f"""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                """
            else:
                return None
            
            schema_df = self.execute_query(schema_query)
            return schema_df.to_dict('records') if schema_df is not None else None
        except Exception as e:
            st.error(f"Schema retrieval failed: {str(e)}")
            return None
    
    def get_all_tables(self) -> List[str]:
        """Get list of all tables in the database"""
        try:
            if self.config.DATABASE_TYPE == "sqlite":
                tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
            elif self.config.DATABASE_TYPE == "mysql":
                tables_query = "SHOW TABLES"
            elif self.config.DATABASE_TYPE == "postgresql":
                tables_query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            else:
                return []
            
            tables_df = self.execute_query(tables_query)
            return tables_df.iloc[:, 0].tolist() if tables_df is not None else []
        except Exception as e:
            st.error(f"Table listing failed: {str(e)}")
            return []
    
    def create_sample_data(self):
        """Create sample tables for demonstration"""
        try:
            # Sample sales data
            sales_data = {
                'id': range(1, 101),
                'product': ['Product A', 'Product B', 'Product C'] * 33 + ['Product A'],
                'sales_amount': [100 + i * 10 for i in range(100)],
                'sales_date': pd.date_range('2023-01-01', periods=100, freq='D'),
                'region': ['North', 'South', 'East', 'West'] * 25
            }
            
            sales_df = pd.DataFrame(sales_data)
            sales_df.to_sql('sales', self.engine, if_exists='replace', index=False)
            
            # Sample customer data
            customer_data = {
                'customer_id': range(1, 51),
                'customer_name': [f'Customer {i}' for i in range(1, 51)],
                'age': [25 + (i % 40) for i in range(50)],
                'city': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'] * 10
            }
            
            customer_df = pd.DataFrame(customer_data)
            customer_df.to_sql('customers', self.engine, if_exists='replace', index=False)
            
            st.success("Sample data created successfully!")
            
        except Exception as e:
            st.error(f"Sample data creation failed: {str(e)}")
