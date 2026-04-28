import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# Validation
def validate_api_keys():
    """Validate that required API keys are configured."""
    if not GEMINI_API_KEY:
        print("⚠️  WARNING: GEMINI_API_KEY not configured in .env file")
    if not NVIDIA_API_KEY:
        print("⚠️  WARNING: NVIDIA_API_KEY not configured in .env file")
    return bool(GEMINI_API_KEY or NVIDIA_API_KEY)

# App settings
APP_NAME = "SentinelNet AI"
VERSION = "1.0.0"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# AI Provider Settings
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")  # "gemini" or "nvidia"