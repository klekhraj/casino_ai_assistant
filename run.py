#!/usr/bin/env python3
"""
Analytics AI Tool - Startup Script
Run this script to start the Streamlit application
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import streamlit
        import openai
        import pandas
        import plotly
        import sqlalchemy
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("⚠️  .env file not found")
        print("Please copy .env.example to .env and add your OpenAI API key")
        return False
    return True

def main():
    print("🚀 Starting Analytics AI Tool...")
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check environment file
    if not check_env_file():
        print("Continuing without .env file (you can set environment variables manually)")
    
    # Start Streamlit app
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Analytics AI Tool stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting application: {e}")

if __name__ == "__main__":
    main()
