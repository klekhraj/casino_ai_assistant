import urllib.request
import urllib.parse
import json
from typing import Optional, Dict, Any, List
import streamlit as st
from config import Config
import os

class SQLGenerator:
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.API_KEY
        
    def generate_sql_prompt(self, user_query: str, schema_info: Dict[str, Any]) -> str:
        """Generate the prompt for OpenAI to convert natural language to SQL"""
        
        # Format schema information
        schema_text = ""
        for table_name, columns in schema_info.items():
            schema_text += f"\nTable: {table_name}\n"
            for col in columns:
                if isinstance(col, dict):
                    # SQLite format
                    if 'name' in col:
                        schema_text += f"  - {col['name']} ({col.get('type', 'TEXT')})\n"
                    # MySQL/PostgreSQL format
                    elif 'column_name' in col:
                        schema_text += f"  - {col['column_name']} ({col.get('data_type', 'TEXT')})\n"
                else:
                    schema_text += f"  - {col}\n"
        
        prompt = f"""
You are an expert SQL query generator. Convert the following natural language request into a valid SQL query.

Database Schema:
{schema_text}

User Request: {user_query}

Instructions:
1. Generate ONLY the SQL query, no explanations
2. Use proper SQL syntax
3. Include appropriate WHERE clauses, JOINs, GROUP BY, ORDER BY as needed
4. For aggregations, use appropriate functions (COUNT, SUM, AVG, etc.)
5. Use LIMIT if the request implies limiting results
6. Ensure the query is safe and doesn't include any destructive operations
7. Use table and column names exactly as shown in the schema

SQL Query:
"""
        return prompt
    
    def generate_sql(self, user_query: str, schema_info: Dict[str, Any]) -> Optional[str]:
        """Generate SQL query from natural language using OpenAI via urllib"""
        try:
            if not self.api_key:
                st.error("OpenAI API key not configured. Please set OPENAI_API_KEY in your environment.")
                return None
            
            prompt = self.generate_sql_prompt(user_query, schema_info)
            
            headers = {
                "Authorization": f"Bearer {self.api_key.strip()}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.config.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are an expert SQL query generator. Generate only valid SQL queries without any explanations or markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": self.config.MAX_TOKENS,
                "temperature": self.config.TEMPERATURE
            }
            
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(data).encode(),
                headers=headers
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                sql_query = result["choices"][0]["message"]["content"].strip()
            
            # Clean up the response (remove any markdown formatting)
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            
            return sql_query
            
        except Exception as e:
            st.error(f"SQL generation failed: {str(e)}")
            return None
    
    def validate_sql(self, sql_query: str) -> bool:
        """Basic SQL validation to prevent destructive operations"""
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE']
        
        sql_upper = sql_query.upper()
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                st.warning(f"Query contains potentially dangerous keyword: {keyword}")
                return False
        
        return True
    
    def explain_sql(self, sql_query: str) -> Optional[str]:
        """Generate explanation for the SQL query using OpenAI via urllib"""
        try:
            if not self.api_key:
                st.error("OpenAI API key not configured. Please set OPENAI_API_KEY in your environment.")
                return None

            prompt = f"""
Explain this SQL query in simple terms:

{sql_query}

Provide a clear, concise explanation of what this query does.
"""
            
            headers = {
                "Authorization": f"Bearer {self.api_key.strip()}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.config.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are an SQL expert. Explain SQL queries in simple, clear terms."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 300,
                "temperature": 0.3
            }
            
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(data).encode(),
                headers=headers
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                return result["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            st.error(f"SQL explanation failed: {str(e)}")
            return None
