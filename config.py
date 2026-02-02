import os
from dotenv import load_dotenv, find_dotenv

env_path = find_dotenv()
if env_path:
    print(f"[DEBUG] .env found at: {env_path}")
    load_dotenv(env_path)
else:
    print("[DEBUG] .env not found; relying on system environment variables")

class Config:
    API_KEY = os.getenv("OPENAI_API_KEY")
    print(f"[DEBUG] OPENAI_API_KEY loaded: {bool(API_KEY)}")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///analytics.db")
    DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite")
    LOGIN_USERNAME = os.getenv("LOGIN_USERNAME", "analytics_user")
    LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "change_me")
    DB_DOWNLOAD_URL = os.getenv("DB_DOWNLOAD_URL") or "https://dl.dropboxusercontent.com/scl/fi/cbl7rjyb59ype02ybuaub/analytics.db?rlkey=9i120uadvqgs5wq64pc3kd6fj&st=shpogi23&dl=1"
    print(f"[DEBUG] DB_DOWNLOAD_URL loaded: {bool(DB_DOWNLOAD_URL)}")
    
    @staticmethod
    def get_direct_drive_url(share_url: str) -> str:
        """Convert Google Drive share URL to direct download URL."""
        if "drive.google.com" in share_url and "/file/d/" in share_url:
            file_id = share_url.split("/file/d/")[1].split("/")[0]
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        return share_url
    
    # OpenAI Configuration
    OPENAI_MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 1000
    TEMPERATURE = 0.1
    
    # Streamlit Configuration
    PAGE_TITLE = "Analytics AI Tool"
    PAGE_ICON = "📊"
    LAYOUT = "wide"
