import os

from dotenv import load_dotenv

load_dotenv()

APP_NAME = "NIGHTINGALE"

APP_VERSION = "1.0.0"

APP_DESCRIPTION = (
    "Secure Multimodal Medical AI Assistant "
    "powered by Retrieval-Augmented Generation."
)

DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

QDRANT_URL = os.getenv("QDRANT_URL")

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:latest")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

LOGIN_RATE_LIMIT = 5
LOGIN_RATE_WINDOW = 60

REGISTER_RATE_LIMIT = 3
REGISTER_RATE_WINDOW = 60

CHAT_RATE_LIMIT = 60
CHAT_RATE_WINDOW = 60
