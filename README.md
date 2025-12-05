# 🎰 Casino Analytics AI Assistant

An AI-powered Streamlit app that turns natural-language questions about GSN Casino data
into SQL, executes them against a local SQLite database, and generates insights
and visualizations.

---

## 🚀 Key Features

- **Natural language → SQL** using OpenAI
- **SQLite-backed demo dataset** via `analytics.db`
- **Latest results panel** with data preview & column profile
- **AI-generated insights & charts** for the most recent query result
- **Query history** with generated SQL
- **Download results as CSV** (plus a visual copy button)

This repo is designed for **local analytics workflows** and internal demos.

---

## 1. Requirements

- Python 3.9+
- pip
- OpenAI API key

---

## 2. Install dependencies

From the project root:

```bash
pip install -r requirements.txt
```

If you prefer a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

---

## 3. Get `analytics.db` (required)

The app expects a local SQLite database named `analytics.db` in the
project root. This file is **not committed to Git**.

Instead, download it from the shared Google Drive folder:

- **Drive folder:**  
  https://drive.google.com/drive/folders/1TUXvwqOa5JtEl4maYUmI_6vI2MNVGX5C?usp=sharing

Steps:

1. Open the link above.
2. Download the `analytics.db` file.
3. Place it in the repository root so the structure looks like:

   ```text
   casino_ai_assistant/
   ├── analytics.db          # ← put the downloaded file here
   ├── simple_app.py
   ├── database.py
   ├── assets/
   ├── requirements.txt
   └── README.md
   ```

> Anyone cloning this repo must download `analytics.db` from the Drive link
> and place it as shown above before running the app.

---

## 4. Configure your OpenAI API key

The app reads `OPENAI_API_KEY` from the environment (or `.env` via `python-dotenv`).

### Option A – Environment variable

macOS / Linux:

```bash
export OPENAI_API_KEY="sk-..."
```

Windows (PowerShell):

```powershell
$env:OPENAI_API_KEY="sk-..."
```

### Option B – `.env` file

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
```

---

## 5. Run the app

From the project root (where `simple_app.py` lives and `analytics.db` is placed):

```bash
streamlit run simple_app.py
```

Open the URL shown in the terminal (typically http://localhost:8501).

---

## 6. How to use the app

1. **Ask a question**  
   In the main left panel, type your GSN Casino analytics question in
   natural language, or choose one from **GSN Casino Example Queries**.

2. **Run query**  
   Click **Run query & show results**. The app will:

   - Generate SQL from your question
   - Execute it against `analytics.db` (table: `user_days`)
   - Show the result table under **📊 Latest Query Results**

3. **Inspect results**  
   - Preview the table
   - See column dtypes + definitions in **Result details & column profile**
   - Download results as CSV
   - (Right now the **Copy data to clipboard** button is visual only; due to
     Streamlit constraints we don’t inject JS clipboard handlers.)

4. **Generate insights & charts**  
   - Scroll to **🧠 Insights & Visualizations**
   - Click **✨ Generate Insights & Visualizations**
   - The app sends the latest results sample + question to OpenAI to produce:
     - Short, quantitative insight bullets
     - A small set of chart specs (bar/line/pie/histogram) which are rendered
       with Plotly in the app.

5. **Review query history**  
   At the bottom, you can expand previous entries to see:
   - The natural-language question
   - The generated SQL

---

## 7. Dataset notes (`user_days`)

`analytics.db` contains a `user_days` table with columns such as:

- `event_day_pst` – Snapshot date
- `user_id` – Unique user id
- `bookings` – Revenue for that day
- `bookings_lifetime` – Lifetime revenue (LTV) up to `event_day_pst`
- `transactions` – Number of transactions
- `payer_type` – Payer segmentation (with NULL = not active payer)
- `slot_spins`, `slot_coins_used`, `slot_coins_gained`
- `balance_coins_begin`, `balance_coins_end`
- `install_first_date_pst` – Install date (used for tenure)
- `platform` – ios / android / amazon (mobile) vs others (web/webstore)
- `country` – User country
- `engagement_7d` – Active days in last 7 days (7 = regular user)

The SQL prompt in `simple_app.py` explains how to interpret
active vs lifetime payers, including `bookings_lifetime = 0` for
**lifetime non-payers**.

---

## 8. Limitations & notes

- `analytics.db` is **not** in the Git repo; it must be downloaded
  from the Drive link each time you set up a fresh clone.
- The **Copy data to clipboard** button is currently a visual element only
  (no JS clipboard access in standard Streamlit markdown).
- OpenAI usage depends on your API quota and billing; heavy usage may incur cost.

---

## 9. Development hints

- Main app entrypoint: `simple_app.py`
- DB helper: `database.py` (manages the SQLite connection to `analytics.db`)
- To modify the SQL prompt/behavior, edit `generate_sql_query` in `simple_app.py`.
- To tweak insight generation, edit `generate_result_insights` in `simple_app.py`.

---

## 10. License / internal use

This project is intended for internal/demo use around casino analytics.
Check with your team before sharing outside your organization.
