import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

from config import Config
from database import DatabaseManager
from sql_generator import SQLGenerator

# Page configuration
config = Config()
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout=config.LAYOUT,
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if 'sql_generator' not in st.session_state:
    st.session_state.sql_generator = SQLGenerator()
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def login():
    if st.session_state.authenticated:
        return True

    st.title("🔐 Analytics AI Tool Login")
    username = st.text_input("Username", autocomplete="username")
    password = st.text_input("Password", type="password", autocomplete="current-password")
    if st.button("Sign in"):
        if username == config.LOGIN_USERNAME and password == config.LOGIN_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid username or password")

    return False

def main():
    if not login():
        return

    # Header
    st.title("📊 Analytics AI Tool")
    st.markdown("Convert natural language to SQL queries and visualize your data instantly!")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Database connection status
        if st.button("🔌 Connect to Database"):
            with st.spinner("Connecting to database..."):
                if st.session_state.db_manager.connect():
                    st.success("✅ Connected to database!")
                else:
                    st.error("❌ Connection failed!")
        
        # Sample data creation
        if st.button("📝 Create Sample Data"):
            with st.spinner("Creating sample data..."):
                st.session_state.db_manager.create_sample_data()
        
        # Database info
        st.subheader("📋 Database Tables")
        tables = st.session_state.db_manager.get_all_tables()
        if tables:
            for table in tables:
                with st.expander(f"📊 {table}"):
                    schema = st.session_state.db_manager.get_table_schema(table)
                    if schema:
                        schema_df = pd.DataFrame(schema)
                        st.dataframe(schema_df, use_container_width=True)
        else:
            st.info("No tables found. Create sample data or connect to your database.")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Natural Language Query")
        
        # Query input
        user_query = st.text_area(
            "Enter your question in plain English:",
            placeholder="e.g., Show me the top 10 products by sales amount",
            height=100
        )
        
        # Example queries
        st.subheader("💡 Example Queries")
        example_queries = [
            "Show me total sales by product",
            "What are the top 5 customers by age?",
            "Show sales trends over time",
            "Which region has the highest sales?",
            "Show average sales amount by month"
        ]
        
        selected_example = st.selectbox("Or select an example:", [""] + example_queries)
        if selected_example:
            user_query = selected_example
            st.rerun()
    
    with col2:
        st.header("⚙️ Query Options")
        
        auto_visualize = st.checkbox("📈 Auto-generate visualizations", value=True)
        show_explanation = st.checkbox("💡 Show SQL explanation", value=True)
        limit_results = st.number_input("🔢 Limit results", min_value=10, max_value=1000, value=100)
    
    # Generate and execute query
    if st.button("🚀 Generate & Execute Query", type="primary"):
        if not user_query:
            st.warning("Please enter a query!")
            return
        
        with st.spinner("Generating SQL query..."):
            # Get schema information
            tables = st.session_state.db_manager.get_all_tables()
            schema_info = {}
            for table in tables:
                schema_info[table] = st.session_state.db_manager.get_table_schema(table)
            
            if not schema_info:
                st.error("No database schema found. Please connect to database and create tables.")
                return
            
            # Generate SQL
            sql_query = st.session_state.sql_generator.generate_sql(user_query, schema_info)
            
            if not sql_query:
                st.error("Failed to generate SQL query.")
                return
            
            # Validate SQL
            if not st.session_state.sql_generator.validate_sql(sql_query):
                st.error("Generated query contains potentially dangerous operations.")
                return
            
            # Add LIMIT if not present
            if "LIMIT" not in sql_query.upper():
                sql_query += f" LIMIT {limit_results}"
        
        # Display generated SQL
        st.subheader("🔍 Generated SQL Query")
        st.code(sql_query, language="sql")
        
        # Show explanation
        if show_explanation:
            with st.spinner("Generating explanation..."):
                explanation = st.session_state.sql_generator.explain_sql(sql_query)
                if explanation:
                    st.info(f"**Query Explanation:** {explanation}")
        
        # Execute query
        with st.spinner("Executing query..."):
            result_df = st.session_state.db_manager.execute_query(sql_query)
            
            if result_df is not None and not result_df.empty:
                # Display results
                st.subheader("📊 Query Results")
                st.dataframe(result_df, use_container_width=True)
                
                # Auto-generate visualizations
                if auto_visualize and len(result_df.columns) >= 2:
                    st.subheader("📈 Visualizations")
                    generate_visualizations(result_df)
                
                # Save to query history
                st.session_state.query_history.append({
                    'timestamp': datetime.now(),
                    'natural_query': user_query,
                    'sql_query': sql_query,
                    'result_count': len(result_df)
                })
                
                # Download option
                csv = result_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            elif result_df is not None:
                st.info("Query executed successfully but returned no results.")
            else:
                st.error("Query execution failed.")
    
    # Query history
    if st.session_state.query_history:
        st.subheader("📝 Query History")
        history_df = pd.DataFrame(st.session_state.query_history)
        st.dataframe(history_df, use_container_width=True)

def generate_visualizations(df):
    """Generate automatic visualizations based on data types"""
    try:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
            # Bar chart
            fig_bar = px.bar(
                df.head(20), 
                x=categorical_cols[0], 
                y=numeric_cols[0],
                title=f"{numeric_cols[0]} by {categorical_cols[0]}"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        if len(numeric_cols) >= 2:
            # Scatter plot
            fig_scatter = px.scatter(
                df, 
                x=numeric_cols[0], 
                y=numeric_cols[1],
                title=f"{numeric_cols[1]} vs {numeric_cols[0]}"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        if len(numeric_cols) >= 1:
            # Histogram
            fig_hist = px.histogram(
                df, 
                x=numeric_cols[0],
                title=f"Distribution of {numeric_cols[0]}"
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        # Time series if date column exists
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        if date_cols and numeric_cols:
            fig_line = px.line(
                df.sort_values(date_cols[0]), 
                x=date_cols[0], 
                y=numeric_cols[0],
                title=f"{numeric_cols[0]} over time"
            )
            st.plotly_chart(fig_line, use_container_width=True)
            
    except Exception as e:
        st.warning(f"Could not generate automatic visualizations: {str(e)}")

if __name__ == "__main__":
    main()
