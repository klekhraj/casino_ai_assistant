import os
from dotenv import load_dotenv, find_dotenv

env_path = find_dotenv()
if env_path:
    print(f"[DEBUG] .env found at: {env_path}")
    load_dotenv(env_path)
else:
    print("[DEBUG] .env not found; relying on system environment variables")

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    print(f"[DEBUG] OPENAI_API_KEY loaded: {bool(OPENAI_API_KEY)}")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///analytics.db")
    DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite")
    LOGIN_USERNAME = os.getenv("LOGIN_USERNAME", "analytics_user")
    LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "change_me")
    
    # OpenAI Configuration
    OPENAI_MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 1000
    TEMPERATURE = 0.1
    
    # Streamlit Configuration
    PAGE_TITLE = "Analytics AI Tool"
    PAGE_ICON = "📊"
    LAYOUT = "wide"
