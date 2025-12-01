import streamlit as st
from openai import OpenAI
from datetime import datetime
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Royal Analytics AI - Casino Intelligence Suite",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Header Styles */
    .header-container {
        background: rgba(255, 255, 255, 0.98) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 25px !important;
        padding: 2.5rem 2rem !important;
        margin-bottom: 2rem !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main-title {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-align: center !important;
        margin: 0 !important;
        line-height: 1.2 !important;
    }
    
    .subtitle {
        font-size: 1.3rem !important;
        color: #555 !important;
        text-align: center !important;
        font-weight: 400 !important;
        margin: 0.5rem 0 0 0 !important;
    }
    
    /* Card Styles */
    .card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .input-card {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Example Cards */
    .example-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
    }
    
    .example-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 25px rgba(240, 147, 251, 0.5);
    }
    
    /* SQL Output */
    .sql-output {
        background: #1e1e1e;
        color: #d4d4d4;
        padding: 1.5rem;
        border-radius: 12px;
        font-family: 'Monaco', 'Consolas', monospace;
        font-size: 0.9rem;
        line-height: 1.6;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    /* Success/Error Messages */
    .success-message {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    /* Loading Animation */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .loading-spinner {
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'selected_query' not in st.session_state:
    st.session_state.selected_query = ""

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
    # Header with Royal Lounge Casino branding
    st.markdown("""
    <div class="header-container">
        <div style="text-align: center; padding: 1.5rem 0;">
            <div style="display: flex; align-items: center; justify-content: center; gap: 2rem; margin-bottom: 1rem; flex-wrap: wrap;">
                <div style="width: 100px; height: 100px; display: flex; align-items: center; justify-content: center;">
                    <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxkZWZzPgo8bGluZWFyR3JhZGllbnQgaWQ9ImJsdWVHcmFkaWVudCIgeDE9IjAlIiB5MT0iMCUiIHgyPSIxMDAlIiB5Mj0iMTAwJSI+CjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiMxZTNhOGEiLz4KPHN0b3Agb2Zmc2V0PSI1MCUiIHN0b3AtY29sb3I9IiMxZTQwYWYiLz4KPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjM2I4MmY2Ii8+CjwvbGluZWFyR3JhZGllbnQ+CjxsaW5lYXJHcmFkaWVudCBpZD0iZ29sZEdyYWRpZW50IiB4MT0iMCUiIHkxPSIwJSIgeDI9IjEwMCUiIHkyPSIxMDAlIj4KPHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iI2ZiYmYyNCIvPgo8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiNmNTllMGIiLz4KPC9saW5lYXJHcmFkaWVudD4KPC9kZWZzPgo8IS0tIE1haW4gU2hpZWxkIC0tPgo8cGF0aCBkPSJNNTAgNUwyMCAyMEwyMCA2MEw1MCA5NUw4MCA2MEw4MCAyMEw1MCA1WiIgZmlsbD0idXJsKCNibHVlR3JhZGllbnQpIiBzdHJva2U9IiNmYmJmMjQiIHN0cm9rZS13aWR0aD0iMiIvPgo8IS0tIENyb3duIC0tPgo8dGV4dCB4PSI1MCIgeT0iMjUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgZmlsbD0iI2ZiYmYyNCIgdGV4dC1hbmNob3I9Im1pZGRsZSI+8J+RkTwvdGV4dD4KPCEtLSBST1lBTCAtLT4KPHJlY3QgeD0iMjAiIHk9IjMwIiB3aWR0aD0iNjAiIGhlaWdodD0iMTIiIHJ4PSI2IiBmaWxsPSJ1cmwoI2dvbGRHcmFkaWVudCkiLz4KPHRleHQgeD0iNTAiIHk9IjM5IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iOCIgZm9udC13ZWlnaHQ9ImJvbGQiIGZpbGw9IiMxZTQwYWYiIHRleHQtYW5jaG9yPSJtaWRkbGUiPlJPWUFMPC90ZXh0Pgo8IS0tIExPVU5HRSAtLT4KPHJlY3QgeD0iMTUiIHk9IjQ1IiB3aWR0aD0iNzAiIGhlaWdodD0iMTIiIHJ4PSI2IiBmaWxsPSJ1cmwoI2dvbGRHcmFkaWVudCkiLz4KPHRleHQgeD0iNTAiIHk9IjU0IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iOCIgZm9udC13ZWlnaHQ9ImJvbGQiIGZpbGw9IiMxZTQwYWYiIHRleHQtYW5jaG9yPSJtaWRkbGUiPkxPVU5HRTwvdGV4dD4KPCEtLSBDQVNJTk8gLS0+Cjx0ZXh0IHg9IjUwIiB5PSI3MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjgiIGZvbnQtd2VpZ2h0PSJib2xkIiBmaWxsPSIjZmJiZjI0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5DQVNJT088L3RleHQ+CjwhLS0gRGVjb3JhdGl2ZSBEb3RzIC0tPgo8Y2lyY2xlIGN4PSIyNSIgY3k9IjI1IiByPSIyIiBmaWxsPSIjZmJiZjI0Ii8+CjxjaXJjbGUgY3g9Ijc1IiBjeT0iMjUiIHI9IjIiIGZpbGw9IiNmYmJmMjQiLz4KPGNpcmNsZSBjeD0iMjUiIGN5PSI3NSIgcj0iMiIgZmlsbD0iI2ZiYmYyNCIvPgo8Y2lyY2xlIGN4PSI3NSIgY3k9Ijc1IiByPSIyIiBmaWxsPSIjZmJiZjI0Ii8+Cjwvc3ZnPg==" 
                         alt="Royal Lounge Casino Logo" 
                         style="width: 80px; height: 80px; filter: drop-shadow(0 4px 15px rgba(74, 26, 92, 0.4));">
                </div>
                <div style="height: 60px; width: 3px; background: linear-gradient(135deg, #D4AF37 0%, #FFD700 100%); border-radius: 2px; box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);"></div>
                <div style="text-align: left;">
                    <h1 style="font-size: 2.8rem; font-weight: 800; margin: 0; background: linear-gradient(135deg, #4A1A5C 0%, #2D1B69 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); line-height: 1;">
                        Royal Analytics AI
                    </h1>
                    <p style="font-size: 1rem; color: #D4AF37; margin: 0; font-weight: 700; text-transform: uppercase; letter-spacing: 2px;">
                        Casino Intelligence Suite
                    </p>
                </div>
            </div>
            <p style="font-size: 1.1rem; color: #4A5568; margin: 0 0 1.5rem 0; font-weight: 500; max-width: 650px; margin-left: auto; margin-right: auto;">
                Transform natural language into powerful BigQuery SQL queries for premium casino analytics
            </p>
            <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
                <span style="background: linear-gradient(135deg, #D4AF37 0%, #FFD700 100%); color: #2D1B69; padding: 0.4rem 1.2rem; border-radius: 25px; font-size: 0.9rem; font-weight: 700; box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4);">
                    ⚡ Powered by OpenAI
                </span>
                <span style="background: linear-gradient(135deg, #4A1A5C 0%, #2D1B69 100%); color: #D4AF37; padding: 0.4rem 1.2rem; border-radius: 25px; font-size: 0.9rem; font-weight: 700; box-shadow: 0 4px 15px rgba(74, 26, 92, 0.4);">
                    📊 BigQuery Optimized
                </span>
                <span style="background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%); color: white; padding: 0.4rem 1.2rem; border-radius: 25px; font-size: 0.9rem; font-weight: 700; box-shadow: 0 4px 15px rgba(139, 69, 19, 0.4);">
                    👑 Royal Lounge Data
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content in columns
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        # Query Input Section
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown("### 💬 Ask Your Analytics Question")
        
        # Show selected query if available
        if st.session_state.selected_query:
            st.info(f"📝 Selected Query: {st.session_state.selected_query}")
            user_query = st.session_state.selected_query
            # Add option to clear or edit
            col_clear, col_edit = st.columns(2)
            with col_clear:
                if st.button("❌ Clear Selection"):
                    st.session_state.selected_query = ""
                    st.rerun()
            with col_edit:
                if st.button("✏️ Edit Query"):
                    st.session_state.selected_query = ""
                    st.rerun()
        else:
            user_query = st.text_area(
                "",
                placeholder="Ask anything about your GSN Casino data...\n\nExample: 'Show me DAU trends for the last 30 days' or 'Compare revenue between high and low payers'",
                height=120,
                key="query_input"
            )
        
        # Generate button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            generate_clicked = st.button("🚀 Generate SQL Query", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Process query
        if generate_clicked and user_query.strip():
            with st.spinner("🤖 Generating your SQL query..."):
                time.sleep(1)  # Add slight delay for better UX
                sql_query = generate_sql_query(user_query)
                
                if sql_query:
                    st.markdown("### ✨ Generated SQL Query")
                    st.code(sql_query, language="sql")
                    
                    # Action buttons
                    col_action1, col_action2 = st.columns(2)
                    with col_action1:
                        st.download_button(
                            "📥 Download SQL",
                            sql_query,
                            file_name=f"gsn_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
                            mime="text/plain"
                        )
                    
                    with col_action2:
                        if st.button("📋 Copy to Clipboard"):
                            st.success("✅ SQL copied to clipboard!")
                    
                    # Save to history
                    st.session_state.query_history.insert(0, {
                        'timestamp': datetime.now(),
                        'question': user_query,
                        'sql': sql_query
                    })
                    
                    # Keep only last 10 queries
                    if len(st.session_state.query_history) > 10:
                        st.session_state.query_history = st.session_state.query_history[:10]
        
        elif generate_clicked and not user_query.strip():
            st.warning("⚠️ Please enter your analytics question first!")
    
    with col2:
        # Quick Examples Section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 💡 Quick Examples")
        
        examples = [
            "Get VIP player activity last 7 days",
            "Show revenue by player tier",
            "Top 10 high-rollers by total bets",
            "Daily jackpot trends (30 days)",
            "Premium member engagement",
            "Average bet size by game type",
            "VIP vs regular player comparison",
            "Mobile vs desktop revenue",
            "Player retention by loyalty tier",
            "Weekly tournament participation"
        ]
        
        for example in examples:
            if st.button(f"📊 {example}", key=f"ex_{example}", use_container_width=True):
                st.session_state.selected_query = example
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # API Configuration
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Configuration")
        
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Your OpenAI API key for generating SQL queries"
        )
        
        if api_key_input:
            st.success("✅ API Key configured")
        else:
            st.warning("⚠️ API Key required")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    
    # Query History Section
    if st.session_state.query_history:
        st.markdown("---")
        st.markdown("### 📚 Recent Queries")
        
        for i, item in enumerate(st.session_state.query_history[:5]):
            with st.expander(f"🕐 {item['timestamp'].strftime('%H:%M:%S')} - {item['question'][:50]}..."):
                st.markdown(f"**Question:** {item['question']}")
                st.code(item['sql'], language="sql")
                
                col_hist1, col_hist2 = st.columns(2)
                with col_hist1:
                    st.download_button(
                        "📥 Download",
                        item['sql'],
                        file_name=f"query_{i+1}.sql",
                        key=f"download_{i}"
                    )
                with col_hist2:
                    if st.button("🔄 Use Again", key=f"reuse_{i}"):
                        st.session_state.selected_query = item['question']
                        st.rerun()

if __name__ == "__main__":
    main()
