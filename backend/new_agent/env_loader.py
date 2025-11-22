# env_loader.py
import os
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    
    # Set default values if not present
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ GOOGLE_API_KEY not found in environment. Using demo mode.")
    
    if not os.getenv("LLM_MODEL"):
        os.environ["LLM_MODEL"] = "gemini-2.5-flash"

def get_llm_api_key() -> str:
    """Get LLM API key from environment"""
    return os.getenv("GOOGLE_API_KEY", "demo-key")

def get_llm_model() -> str:
    """Get LLM model from environment"""
    return os.getenv("LLM_MODEL", "gemini-2.5-flash")