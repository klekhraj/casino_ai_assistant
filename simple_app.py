import streamlit as st
from openai import OpenAI
from datetime import datetime
import os
import json
import ast
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from database import DatabaseManager

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Casino Analytics AI Assistant",
    page_icon="🎰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    /* Global layout */
    .stApp {
        background: radial-gradient(circle at top left, #162447 0, #05081a 45%, #02030c 100%);
        color: #f8fafc;
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .block-container {
        padding-top: 0.9rem;
        padding-bottom: 2.4rem;
        max-width: 1120px;
    }

    /* Hero */
    .gsn-hero-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 900;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        background: linear-gradient(120deg, #e5f6ff 0%, #7dd3fc 30%, #60a5fa 60%, #a855f7 100%);
        -webkit-background-clip: text;
        color: transparent;
        text-shadow:
            0 0 2px rgba(255,255,255,0.8),
            0 2px 6px rgba(15,23,42,0.8);
        margin-bottom: 0.45rem;
    }

    .gsn-hero-subtitle {
        text-align: center;
        font-size: 1.05rem;
        color: #cbd5f5;
        opacity: 0.98;
        margin-bottom: 0.2rem;
    }

    /* Glass cards */
    .gsn-card {
        background: linear-gradient(135deg, rgba(30, 64, 175, 0.18), rgba(76, 29, 149, 0.28));
        border-radius: 18px;
        padding: 1.3rem 1.55rem;
        border: 1px solid rgba(148, 163, 184, 0.55);
        box-shadow:
            0 18px 45px rgba(10, 15, 35, 0.9),
            0 0 32px rgba(59, 130, 246, 0.45);
        backdrop-filter: blur(18px);
    }

    .gsn-card h2, .gsn-card h3 {
        color: #e5e7f9 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    /* Smaller heading style for right-side panels */
    .right-panel-heading {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }

    /* Tight label helper to keep text close to the control below */
    .tight-label {
        font-size: 0.9rem;
        font-weight: 600;
        color: #e5e7eb;
        margin-bottom: 0.05rem;
    }

    /* Wider label spacing when needed (e.g., above FAQ dropdown) */
    .wide-gap-label {
        font-size: 0.9rem;
        font-weight: 600;
        color: #e5e7eb;
        margin-bottom: 0.3rem;
    }

    /* Pull text area up to tighten first label gap; leave selectbox lower */
    .stTextArea {
        margin-top: -0.7rem !important;   /* tighter gap for first big input box */
    }
    .stSelectbox {
        margin-top: 0.1rem !important;    /* larger gap for dropdown */
    }

    /* Primary CTA: rectangular with soft rounded edges to match other buttons */
    button[kind="primary"] {
        font-weight: 600 !important;
        border-radius: 10px !important;
        border: 1px solid rgba(148, 163, 184, 0.7) !important;
        text-transform: none;
        letter-spacing: 0.03em;
        box-shadow: none !important;
    }
    button[kind="primary"]:hover {
        filter: brightness(1.05);
        transform: translateY(-0.5px);
    }

    /* Inputs */
    textarea, .stSelectbox, .stTextInput, .stNumberInput, .stMultiSelect {
        background-color: rgba(15, 23, 42, 0.96) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(148, 163, 184, 0.7) !important;
        color: #e5e7eb !important;
    }
    textarea:focus, .stTextInput:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.7) !important;
    }

    /* Tables */
    .stDataFrame, .stTable {
        background-color: rgba(15, 23, 42, 0.98) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(75, 85, 99, 0.7) !important;
    }

    hr {
        border-color: rgba(55, 65, 81, 0.7);
    }

    /* Make download, copy, and primary buttons share the same style */
    .stDownloadButton button, #copy-table-btn, button[kind="primary"] {
        border-radius: 10px !important;
        background: linear-gradient(90deg, #38bdf8, #4ade80) !important;
        color: #0b1020 !important;
        border: 1px solid rgba(148, 163, 184, 0.7) !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        padding: 0.45rem 0.9rem !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.35rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if 'last_result_df' not in st.session_state:
    st.session_state.last_result_df = None
if 'last_user_query' not in st.session_state:
    st.session_state.last_user_query = ""
if 'user_query_input' not in st.session_state:
    st.session_state.user_query_input = ""

# Optional: column definitions for known tables (used in debug view)
COLUMN_DEFINITIONS = {
    "event_day_pst": "Event date in Pacific time.",
    "user_id": "Unique user identifier.",
    "bookings": "User revenue (bookings) for the day.",
    "transactions": "Number of transactions for the day.",
    "payer_type": "Payer segmentation label (e.g., Blue, Dolphin, Minnow).",
    "Payer_type": "Payer segmentation label (e.g., Blue, Dolphin, Minnow).",
    "slot_spins": "Number of slot spins in the day.",
    "slot_coins_used": "Total coins/tokens wagered in slot spins.",
    "slot_coins_gained": "Total coins/tokens won from slot spins.",
    "platform": "User platform (ios, android, amazon, others).",
    "engagement_7d": "Days active in the last 7 days (7 = regular user).",
    "total_revenue": "Aggregated revenue metric (e.g., SUM(bookings) over the selected period).",
}

def generate_sql_query(user_query: str, custom_prompt: str = None) -> str:
    """Generate SQL query from natural language using OpenAI.

    The OpenAI API key is read from the OPENAI_API_KEY environment variable only
    and is never exposed in the UI.
    """
    try:
        # Initialize OpenAI client from environment variable only
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("OpenAI API key not configured. Please set OPENAI_API_KEY in your environment.")
            return None

        client = OpenAI(api_key=api_key)
        
        # Use custom prompt or GSN Casino specific prompt
        if custom_prompt:
            prompt = custom_prompt.replace("{user_query}", user_query)
        else:
            prompt = f"""
You are a GSN Casino SQL expert. Generate optimized SQL queries for GSN Casino data stored in a local SQLite database.

RULES:
- Always reference the table: user_days
- Always filter by event_day_pst to limit scanned data when a time range is implied
- Add LIMIT 100 only at the final display step, not during intermediate aggregations
- Use clear, standard SQL that is compatible with SQLite (no BigQuery-specific functions like DATE_SUB or INTERVAL)
- Always treat NULL payer_type as the string 'Non-Payer' by using COALESCE(payer_type, 'Non-Payer') in SELECT and GROUP BY when segmenting by payer type for **active payer** status.
- Interpreting payer status:
  * Active payer vs active non-payer (last 12 weeks) is determined by payer_type (NULL => not an active payer).
  * **Lifetime non-payers** are users with bookings_lifetime = 0 (they have never paid).
  * **Lifetime payers** are users with bookings_lifetime > 0 (they have paid at least once).
  * Whenever the user asks about "lifetime" payer or non-payer metrics, you MUST use bookings_lifetime (0 vs > 0) instead of payer_type filters.
- Provide ONLY the SQL query, no explanations or commentary

TABLE SCHEMA (user_days):
- event_day_pst: Snapshot date.
- user_id: Unique user id.
- bookings: User's revenue for that day.
- transactions: Number of transactions.
- bookings_lifetime: Lifetime revenue (LTV) or lifetime value of a user up to event_day_pst.
- balance_coins_begin: Tokens/coins balance when the user logged in.
- balance_coins_end: Tokens/coins balance at the end of the day.
- install_first_date_pst: Date of install. Can be used to calculate tenure. Users older than 365 days are called older players.
- country: Country of the user (demographic information).
- payer_type: Type of payer (payer_type, DolphinLapse, WhaleLapse, BassLapse, Whale, Bass, MinnowLapse, Dolphin, Blue, Minnow, OrcaLapse, BlueLapse, NULL for Non-Payer).
- slot_spins: Number of spins in a day.
- slot_coins_used: Tokens/coins used in a day.
- slot_coins_gained: Tokens/coins gained in a day.
- platform: ios, android, amazon are mobile platforms; others are web/webstore.
- engagement_7d: Count of days the user was active in the last 7 days including today (7 = regular users).

PAYER GROUPS:
- High Payer: Blue, BlueLapse, Orca, OrcaLapse, Whale, WhaleLapse
- Low Payer: Bass, BassLapse, Dolphin, DolphinLapse, Minnow, MinnowLapse
- Non-Payer: NULL (always surfaced as the label 'Non-Payer' using COALESCE)

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

def generate_result_insights(df, user_query: str):
    """Generate insights and chart specifications for the query results.

    Returns a Python dict with at least:
    {
        "insights": ["..."],
        "charts": [
            {"type": "bar", "x": "Payer_type", "y": "total_revenue", "title": "..."},
            {"type": "pie", "names": "Payer_type", "values": "total_revenue", "title": "..."},
            ...
        ]
    }

    If the model does not return valid JSON, a fallback dict with a single
    free-form insight string is returned.
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "OpenAI API key not configured. Cannot generate insights."

        client = OpenAI(api_key=api_key)

        sample_csv = df.head(50).to_csv(index=False)
        prompt = f"""
You are a highly experienced senior data analyst.

IMPORTANT RUNTIME CONTEXT
- You are used strictly via an API that sends and receives **text only**.
- You CANNOT return actual charts, images, or other media.
- Instead, you must describe analytics as:
  1) Quantitative insight sentences, and
  2) A machine-readable chart specification that another tool will
     use to render visualizations.

INPUT YOU RECEIVE
- The user's natural-language question about a dataset
- A small CSV sample of the query results

WHAT YOU MUST RETURN
Return a single **JSON object only** (no extra text) with these
top-level keys:

{{
  "insights": [
    "string insight 1",
    "string insight 2"
  ],
  "charts": [
    {{
      "type": "bar" | "pie" | "line" | "histogram",
      "x": "column_name (for bar/line) or null",
      "y": "metric_column (for bar/line) or null",
      "names": "column_name (for pie) or null",
      "values": "metric_column (for pie) or null",
      "title": "Human readable chart title"
    }},
    ...
  ]
}}

Rules for INSIGHTS (text part):
- Always be quantitative (shares, rankings, concentration, peaks/lows, etc.).
- 4–6 short bullet-style sentences.
- Each insight should mention numbers or percentages when possible.
- Keep each insight under 160 characters.
- Do NOT restate the table in a generic way (e.g., "Blue is the highest").

Rules for CHART SPECS (for downstream visualization tools):
- You are NOT drawing the charts yourself; you are specifying how
  another system should draw them.
- For categorical totals (e.g., payer-type revenue), output **two charts**:
  1) Bar chart with type="bar", x = category column, y = metric column.
  2) Pie chart with type="pie", names = category column, values = metric column.
- For time-series data, use type="line" with x = date column, y = metric column.
- For distributions of a single numeric metric, use type="histogram" with x = metric column.
- Use column names exactly as they appear in the CSV sample.
- If a field (x, y, names, values) is not relevant to a chart type,
  set it to null or omit it.

OUTPUT FORMAT REQUIREMENTS
- Return ONLY the JSON object described above.
- Do NOT include markdown, explanations, natural-language text, or
  any content outside of the JSON.

User question:
{user_query}

Sample rows from the query results in CSV format:
{sample_csv}
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a senior data analyst that returns ONLY valid JSON following the requested schema. The entire response must fit comfortably within 600 tokens."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=600,
            temperature=0.3,
        )
        raw = response.choices[0].message.content.strip()

        # Try to extract a clean JSON object even if the model wrapped it
        # in markdown fences or extra explanation text.
        cleaned = raw

        # If there are markdown code fences, take the content inside the first pair
        if "```" in cleaned:
            parts = cleaned.split("```")
            # Heuristic: pick the largest chunk that looks like JSON
            json_like_chunks = [p for p in parts if "{" in p and "}" in p]
            if json_like_chunks:
                cleaned = max(json_like_chunks, key=len).strip()

        # Trim to the outermost JSON object if there is extra text
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start : end + 1]

        # Try to parse the cleaned response as JSON, with a Python-literal
        # fallback if the model used single quotes or minor JSON mistakes.
        try:
            parsed = json.loads(cleaned)
        except Exception:
            try:
                parsed = ast.literal_eval(cleaned)
            except Exception:
                parsed = None

        if isinstance(parsed, dict):
            if "insights" not in parsed:
                parsed["insights"] = []
            if "charts" not in parsed:
                parsed["charts"] = []
            return parsed
        else:
            # Fallback: treat the whole text as a single insight string
            return {"insights": [raw], "charts": []}

    except Exception as e:
        return f"Insight generation failed: {str(e)}"

def _set_query_from_example():
    """Update the main query input when a preset example is chosen."""
    selected = st.session_state.get("example_query", "")
    if selected:
        st.session_state.user_query_input = selected


def main():
    # Header (restore small spacer so logo is not flush with the top)
    st.markdown("<div style='margin-top: 0.4rem'></div>", unsafe_allow_html=True)
    header_logo_col, header_text_col = st.columns([1, 3])

    with header_logo_col:
        st.image("assets/gsn_logo.png", width=180)

    with header_text_col:
        # Slightly smaller offset so text sits higher relative to the logo
        st.markdown("<div style='margin-top: 0rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="gsn-hero-title">CASINO ANALYTICS AI ASSISTANT</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="gsn-hero-subtitle">Leveraging SQL and AI for advanced casino analytics insights.</div>',
            unsafe_allow_html=True,
        )

    # Very tight spacing between hero and main content
    st.markdown("<hr />", unsafe_allow_html=True)

    # Main content area (no sidebar) with a spacer to push options further right
    col1, col_spacer, col2 = st.columns([2.2, 0.3, 1])
    
    with col1:
        st.header("💬 Let me know what you’d like to ask below")

        # Main free-form question input with shared tight-label styling
        st.markdown(
            '<div class="tight-label">Enter your GSN Casino analytics question</div>',
            unsafe_allow_html=True,
        )
        user_query = st.text_area(
            label="Enter your question",
            placeholder="e.g., Get DAU for last 7 days or Show revenue by payer type",
            height=120,
            key="user_query_input",
        )

        # Example queries shown below as "frequently asked questions"
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
            "Get mobile platform DAU vs web platform DAU",
        ]

        st.markdown(
            '<div class="wide-gap-label">Or select from frequently asked questions</div>',
            unsafe_allow_html=True,
        )

        st.selectbox(
            label="Select an example",
            options=[""] + example_queries,
            key="example_query",
            on_change=_set_query_from_example,
        )
    
    with col2:
        # Options panel heading using custom smaller heading style
        st.markdown('<div class="right-panel-heading">🔧 Options</div>', unsafe_allow_html=True)

        show_prompt = st.checkbox("📋 Show generated prompt", value=False)
        copy_to_clipboard = st.checkbox("📋 Enable copy to clipboard", value=True, label="Enable copy to clipboard")

        st.markdown("---")

        # Match heading size for custom prompt section
        st.markdown('<div class="right-panel-heading">🎯 Custom Prompt (Optional)</div>', unsafe_allow_html=True)
        use_custom_prompt = st.checkbox("Use custom prompt")

        custom_prompt = ""
        if use_custom_prompt:
            custom_prompt = st.text_area(
                label="Custom Prompt",
                key="custom_prompt_text",
                height=200,
                placeholder="Enter your custom prompt here. Use {user_query} where you want the user's question to be inserted.",
                help="Create a custom prompt for SQL generation. Use {user_query} where you want the user's question to be inserted."
            )
    
    # Generate query button
    if st.button("Run query & show results", type="primary", use_container_width=True, label="Run query & show results"):
        if not user_query.strip():
            st.warning("Please enter a query!")
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
            )
            
            if sql_query:
                # Basic safety check to prevent destructive operations
                upper_sql = sql_query.upper()
                dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT", "UPDATE"]
                if any(keyword in upper_sql for keyword in dangerous_keywords):
                    st.error("Generated query contains potentially destructive operations and will not be executed.")
                    return

                # Display generated SQL
                st.subheader("✨ Generated SQL Query")
                st.code(sql_query, language="sql")

                # Execute against local database and store results in session_state
                result_df = st.session_state.db_manager.execute_query(sql_query)
                if result_df is not None and not result_df.empty:
                    # Remove any existing index so it is never treated as a data column
                    result_df = result_df.reset_index(drop=True)

                    # Coerce numeric-looking object columns (e.g., totals returned as strings)
                    for col in result_df.select_dtypes(include=["object"]).columns:
                        try:
                            series_str = result_df[col].astype(str).str.replace(",", "").str.strip()
                            converted = pd.to_numeric(series_str, errors="coerce")
                            if converted.notna().any():
                                result_df[col] = converted
                        except Exception:
                            pass

                    # Persist the cleaned result and query for later display/insights
                    st.session_state.last_result_df = result_df
                    st.session_state.last_user_query = user_query
                else:
                    st.info("Query executed but returned no rows.")
                
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
                    mime="text/plain",
                    key="download_sql"
                )
                
                st.success("✅ SQL query generated and executed successfully!")

    # Separate section: always show latest query results (if any)
    if st.session_state.last_result_df is not None and not st.session_state.last_result_df.empty:
        result_df = st.session_state.last_result_df

        st.markdown("---")
        st.subheader("📊 Latest Query Results")
        st.markdown('<div class="gsn-card">', unsafe_allow_html=True)
        # Ensure index is clean and hidden for display
        result_df = result_df.reset_index(drop=True)
        try:
            st.dataframe(result_df, use_container_width=True, hide_index=True)
        except TypeError:
            # Fallback for older Streamlit versions without hide_index
            st.dataframe(result_df, use_container_width=True)

        # Show detected dtypes and per-column summary
        with st.expander("📂 Result details & column profile", expanded=False):
            st.write("Raw dtypes:")
            st.write(result_df.dtypes.astype(str))

            st.write("\nColumn summary:")
            summary_rows = []
            for col in result_df.columns:
                series = result_df[col]
                dtype = str(series.dtype)
                distinct = int(series.nunique(dropna=True))
                samples = series.dropna().unique()[:5]
                samples_display = ", ".join(map(str, samples))
                definition = COLUMN_DEFINITIONS.get(col, "")
                summary_rows.append({
                    "column": col,
                    "dtype": dtype,
                    "distinct_values": distinct,
                    "sample_values": samples_display,
                    "definition": definition,
                })

            if summary_rows:
                st.dataframe(pd.DataFrame(summary_rows))

        csv_str = result_df.to_csv(index=False)
        csv_data = csv_str.encode("utf-8")

        # Place download and copy buttons side by side
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            st.download_button(
                label="📥 Download Query Results (CSV)",
                data=csv_data,
                file_name=f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        # Visual-only copy button (no clipboard functionality, per limitation)
        copy_html = """
        <button id=\"copy-table-btn\" style=\"width: 100%; cursor: default; text-align: center;\">📥 Copy data to clipboard</button>
        """

        with btn_col2:
            st.markdown(copy_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Insights and visualizations for the last successful result
        st.subheader("🧠 Insights & Visualizations")

        if st.button(
            "✨ Generate Insights & Visualizations",
            key="generate_insights_global",
            type="primary",
            use_container_width=True,
        ):
            user_query = st.session_state.last_user_query

            with st.spinner("🎰 Spinning up reels, crunching coins, and drawing charts..."):
                # Time-series visualization (event_day_pst + numeric metrics)
                numeric_cols = result_df.select_dtypes(include=["number"]).columns.tolist()
                if "event_day_pst" in result_df.columns and numeric_cols:
                    ts_df = result_df.copy()
                    try:
                        ts_df["event_day_pst"] = pd.to_datetime(ts_df["event_day_pst"], errors="coerce")
                        ts_df = ts_df.dropna(subset=["event_day_pst"])
                        ts_df = ts_df.sort_values("event_day_pst")

                        st.subheader("📈 Trend over time")
                        st.line_chart(ts_df.set_index("event_day_pst")[numeric_cols[0]])
                    except Exception:
                        pass

                insight_spec = generate_result_insights(result_df, user_query)
                if isinstance(insight_spec, dict):
                    insights_list = insight_spec.get("insights") or []
                    charts_spec = insight_spec.get("charts") or []

                    if insights_list:
                        st.subheader("🔍 Insights")
                        bullets = "\n".join(f"- {text}" for text in insights_list)
                        st.markdown(bullets)

                    # Render any charts requested by the agent spec using a cleaned DataFrame
                    plot_df = result_df.copy()

                    # Drop obvious index-like columns by name
                    drop_cols = [
                        c for c in plot_df.columns
                        if c.lower() == "index" or c.startswith("Unnamed")
                    ]

                    # Also drop any column that is a simple positional index (0..n-1)
                    for c in list(plot_df.columns):
                        series = plot_df[c]
                        try:
                            # Non-null part equals range(len) -> looks like index
                            non_null = series.dropna()
                            if (
                                pd.api.types.is_integer_dtype(non_null) and
                                non_null.reset_index(drop=True).equals(pd.Series(range(len(non_null))))
                            ):
                                drop_cols.append(c)
                        except Exception:
                            continue

                    if drop_cols:
                        plot_df = plot_df.drop(columns=list(set(drop_cols)))

                    # Best-effort: coerce any remaining numeric-looking object columns
                    for col in plot_df.select_dtypes(include=["object"]).columns:
                        try:
                            series_str = plot_df[col].astype(str).str.replace(",", "").str.strip()
                            converted = pd.to_numeric(series_str, errors="coerce")
                            if converted.notna().any():
                                plot_df[col] = converted
                        except Exception:
                            continue

                    for chart in charts_spec:
                        ctype = str(chart.get("type", "")).lower()
                        title = chart.get("title")
                        try:
                            if ctype == "bar":
                                x_col = chart.get("x")
                                y_col = chart.get("y")
                                if not x_col or not y_col:
                                    continue
                                if x_col in plot_df.columns and y_col in plot_df.columns:
                                    fig = px.bar(
                                        plot_df,
                                        x=x_col,
                                        y=y_col,
                                        title=title,
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                            elif ctype == "pie":
                                names_col = chart.get("names")
                                values_col = chart.get("values")
                                if not names_col or not values_col:
                                    continue
                                if names_col in plot_df.columns and values_col in plot_df.columns:
                                    fig = px.pie(
                                        plot_df,
                                        names=names_col,
                                        values=values_col,
                                        title=title,
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                            elif ctype == "line":
                                x_col = chart.get("x")
                                y_col = chart.get("y")
                                if not x_col or not y_col:
                                    continue
                                if x_col in plot_df.columns and y_col in plot_df.columns:
                                    fig = px.line(
                                        plot_df,
                                        x=x_col,
                                        y=y_col,
                                        title=title,
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                            elif ctype == "histogram":
                                x_col = chart.get("x")
                                if not x_col:
                                    continue
                                if x_col in plot_df.columns:
                                    fig = px.histogram(
                                        plot_df,
                                        x=x_col,
                                        title=title,
                                    )
                                    st.plotly_chart(fig, use_container_width=True)
                        except Exception:
                            continue

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
