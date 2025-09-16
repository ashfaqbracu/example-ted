import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = "https://teddybackend-mivk.onrender.com/api/v1"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# FastAPI Configuration
APP_TITLE = "Teddy - Personal Finance Assistant API"
APP_DESCRIPTION = "A RAG-based personal finance assistant that helps you manage your expenses"
APP_VERSION = "1.0.0"
