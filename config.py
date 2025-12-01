import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///analytics.db")
    DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite")
    
    # OpenAI Configuration
    OPENAI_MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 1000
    TEMPERATURE = 0.1
    
    # Streamlit Configuration
    PAGE_TITLE = "Analytics AI Tool"
    PAGE_ICON = "📊"
    LAYOUT = "wide"
