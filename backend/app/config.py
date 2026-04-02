import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("YOUR_API_KEY")

# App settings
APP_NAME = "SentinelNet AI"
VERSION = "1.0.0"