"""
Example implementation of conversational memory for your Royal Analytics AI
This shows how to add session-based conversation history
"""

import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize conversation history in session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

def generate_conversational_sql(user_query: str, api_key: str = None) -> str:
    """Generate SQL with conversation context"""
    try:
        client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        
        # Build conversation context from history
        context = ""
        if st.session_state.conversation_history:
            context = "\nCONVERSATION HISTORY:\n"
            for i, item in enumerate(st.session_state.conversation_history[-3:]):  # Last 3 exchanges
                context += f"Q{i+1}: {item['question']}\n"
                context += f"SQL{i+1}: {item['sql']}\n\n"
            context += "CURRENT QUESTION (consider the above context):\n"
        
        prompt = f"""
You are a GSN Casino BigQuery SQL expert. Generate optimized SQL queries for GSN Casino data.

RULES:
- Always reference: dwh-prod-gsn-casino.gsn_agg.user_days
- Always filter by event_day_pst to limit scanned data
- Use clear BigQuery syntax
- If the user refers to "previous query" or "that", use the conversation history
- For follow-up questions like "average of it" or "median", modify the previous SQL

TABLE SCHEMA (dwh-prod-gsn-casino.gsn_agg.user_days):
- event_day_pst: Date
- user_id: Unique user id
- bookings: User's revenue
- transactions: Number of transactions
- payer_type: Type of payer
- slot_spins: Number of spins in a day
- platform: ios, android, amazon (mobile), others (web/webstore)
- engagement_7d: Days active in last 7 days

{context}
{user_query}

SQL Query:
"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a GSN Casino BigQuery SQL expert. Generate contextual SQL queries based on conversation history."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        sql_query = response.choices[0].message.content.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        # Save to conversation history
        st.session_state.conversation_history.append({
            'question': user_query,
            'sql': sql_query
        })
        
        # Keep only last 10 conversations to manage token usage
        if len(st.session_state.conversation_history) > 10:
            st.session_state.conversation_history = st.session_state.conversation_history[-10:]
        
        return sql_query
        
    except Exception as e:
        st.error(f"SQL generation failed: {str(e)}")
        return None

def show_conversation_examples():
    """Show example of conversational flow"""
    st.markdown("### 💬 Conversational Examples")
    
    examples = [
        {
            "q": "Q1: I want DAU of last 7 days?",
            "sql": "SELECT event_day_pst, COUNT(DISTINCT user_id) as DAU FROM `dwh-prod-gsn-casino.gsn_agg.user_days` WHERE event_day_pst >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) GROUP BY event_day_pst ORDER BY event_day_pst"
        },
        {
            "q": "Q2: Can you also give average of it?",
            "sql": "SELECT AVG(daily_users) as avg_dau FROM (SELECT event_day_pst, COUNT(DISTINCT user_id) as daily_users FROM `dwh-prod-gsn-casino.gsn_agg.user_days` WHERE event_day_pst >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) GROUP BY event_day_pst)"
        },
        {
            "q": "Q3: Is it higher than the median?",
            "sql": "WITH daily_stats AS (SELECT event_day_pst, COUNT(DISTINCT user_id) as daily_users FROM `dwh-prod-gsn-casino.gsn_agg.user_days` WHERE event_day_pst >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) GROUP BY event_day_pst) SELECT AVG(daily_users) as avg_dau, PERCENTILE_CONT(daily_users, 0.5) OVER() as median_dau FROM daily_stats"
        }
    ]
    
    for example in examples:
        st.markdown(f"**{example['q']}**")
        st.code(example['sql'], language="sql")
        st.markdown("---")

if __name__ == "__main__":
    st.title("🎰 Conversational SQL Generator")
    show_conversation_examples()
