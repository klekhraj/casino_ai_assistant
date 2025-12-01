import streamlit as st
from openai import OpenAI
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="GSN Casino SQL Generator",
    page_icon="🎰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

def generate_sql_query(user_query: str, custom_prompt: str = None, api_key: str = None) -> str:
    """Generate SQL query from natural language using OpenAI"""
    try:
        # Initialize OpenAI client
        if api_key:
            client = OpenAI(api_key=api_key)
        else:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        if not (api_key or os.getenv("OPENAI_API_KEY")):
            st.error("OpenAI API key not provided!")
            return None
        
        # Use custom prompt or GSN Casino specific prompt
        if custom_prompt:
            prompt = custom_prompt.replace("{user_query}", user_query)
        else:
            prompt = f"""
You are a GSN Casino BigQuery SQL expert. Generate optimized SQL queries for GSN Casino data stored in Google BigQuery.

RULES:
- Always reference: dwh-prod-gsn-casino.gsn_agg.user_days
- Always filter by event_day_pst to limit scanned data
- Add LIMIT 100 only at final display step, not during intermediate aggregations
- Use clear BigQuery syntax
- Provide ONLY the SQL query, no explanations or commentary

TABLE SCHEMA (dwh-prod-gsn-casino.gsn_agg.user_days):
- event_day_pst: Date
- user_id: Unique user id
- bookings: User's revenue
- transactions: Number of transactions
- payer_type: Type of payer (payer_type, DolphinLapse, WhaleLapse, BassLapse, Whale, Bass, MinnowLapse, Dolphin, Blue, Minnow, OrcaLapse, BlueLapse, NULL for Non-Payer)
- slot_spins: Number of spins in a day
- slot_coins_used: Tokens/coins used in a day
- slot_coins_gained: Tokens/coins gained in a day
- platform: ios, android, amazon (mobile), others (web/webstore)
- engagement_7d: Days active in last 7 days (7 = regular users)

PAYER GROUPS:
- High Payer: Blue, BlueLapse, Orca, OrcaLapse, Whale, WhaleLapse
- Low Payer: Bass, BassLapse, Dolphin, DolphinLapse, Minnow, MinnowLapse
- Non-Payer: NULL

User Request: {user_query}

SQL Query:
"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a GSN Casino BigQuery SQL expert. Generate only optimized BigQuery SQL queries for GSN Casino data without any explanations or markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        sql_query = response.choices[0].message.content.strip()
        
        # Clean up the response (remove any markdown formatting)
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        return sql_query
        
    except Exception as e:
        st.error(f"SQL generation failed: {str(e)}")
        return None

def main():
    # Header
    st.title("🎰 GSN Casino SQL Generator")
    st.markdown("Convert natural language to optimized BigQuery SQL for GSN Casino analytics!")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key:",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Enter your OpenAI API key"
        )
        
        st.markdown("---")
        
        # Custom prompt section
        st.subheader("🎯 Custom Prompt (Optional)")
        use_custom_prompt = st.checkbox("Use custom prompt")
        
        custom_prompt = ""
        if use_custom_prompt:
            custom_prompt = st.text_area(
                "Custom Prompt:",
                height=200,
                placeholder="Enter your custom prompt here. Use {user_query} as placeholder for the user's natural language query.",
                help="Create a custom prompt for SQL generation. Use {user_query} where you want the user's question to be inserted."
            )
        
        st.markdown("---")
        
        # Query history
        if st.session_state.query_history:
            st.subheader("📝 Recent Queries")
            for i, item in enumerate(reversed(st.session_state.query_history[-5:])):
                with st.expander(f"Query {len(st.session_state.query_history) - i}"):
                    st.write(f"**Input:** {item['input']}")
                    st.code(item['sql'], language="sql")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Natural Language Input")
        
        # Query input
        user_query = st.text_area(
            "Enter your GSN Casino analytics question:",
            placeholder="e.g., Get DAU for last 7 days or Show revenue by payer type",
            height=120
        )
        
        # Example queries
        st.subheader("💡 GSN Casino Example Queries")
        example_queries = [
            "Get DAU (daily active users) in last 7 days",
            "Get average DAU in last 7 days",
            "Get non-payer DAU in last 7 days",
            "Show total revenue by payer type in last 30 days",
            "Get top 10 users by slot spins in last 7 days",
            "Show daily revenue trends for last 30 days",
            "Get regular users (engagement_7d = 7) count by platform",
            "Calculate average coins used per spin by payer group",
            "Show high payer vs low payer revenue comparison",
            "Get mobile platform DAU vs web platform DAU"
        ]
        
        selected_example = st.selectbox("Or select an example:", [""] + example_queries)
        if selected_example:
            user_query = selected_example
    
    with col2:
        st.header("🔧 Options")
        
        show_prompt = st.checkbox("📋 Show generated prompt", value=False)
        copy_to_clipboard = st.checkbox("📋 Enable copy to clipboard", value=True)
    
    # Generate query button
    if st.button("🚀 Generate SQL Query", type="primary", use_container_width=True):
        if not user_query.strip():
            st.warning("Please enter a query!")
            return
        
        if not api_key:
            st.error("Please provide your OpenAI API key in the sidebar!")
            return
        
        with st.spinner("Generating SQL query..."):
            # Show the prompt if requested
            if show_prompt:
                if use_custom_prompt and custom_prompt:
                    display_prompt = custom_prompt.replace("{user_query}", user_query)
                else:
                    display_prompt = f"Convert this to SQL: {user_query}"
                
                st.subheader("📋 Generated Prompt")
                st.text_area("Prompt sent to OpenAI:", display_prompt, height=100)
            
            # Generate SQL
            sql_query = generate_sql_query(
                user_query, 
                custom_prompt if use_custom_prompt else None,
                api_key
            )
            
            if sql_query:
                # Display generated SQL
                st.subheader("✨ Generated SQL Query")
                st.code(sql_query, language="sql")
                
                # Copy to clipboard option
                if copy_to_clipboard:
                    st.text_input(
                        "Copy this SQL query:",
                        value=sql_query,
                        help="Select all and copy (Ctrl+A, Ctrl+C)"
                    )
                
                # Save to history
                st.session_state.query_history.append({
                    'timestamp': datetime.now(),
                    'input': user_query,
                    'sql': sql_query
                })
                
                # Download option
                st.download_button(
                    label="📥 Download SQL Query",
                    data=sql_query,
                    file_name=f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
                    mime="text/plain"
                )
                
                st.success("✅ SQL query generated successfully!")
    
    # Display query history
    if st.session_state.query_history:
        st.markdown("---")
        st.subheader("📚 Query History")
        
        # Show recent queries in main area
        for i, item in enumerate(reversed(st.session_state.query_history)):
            with st.expander(f"Query {len(st.session_state.query_history) - i} - {item['timestamp'].strftime('%H:%M:%S')}"):
                col_a, col_b = st.columns([1, 2])
                with col_a:
                    st.write("**Natural Language:**")
                    st.write(item['input'])
                with col_b:
                    st.write("**Generated SQL:**")
                    st.code(item['sql'], language="sql")
        
        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.query_history = []
            st.rerun()

if __name__ == "__main__":
    main()
