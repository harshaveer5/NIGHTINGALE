from app.core.logging import logger

logger.info("STEP 1 - Importing chat router")
from app.api.chat_router import router as chat_router

logger.info("STEP 2 - Importing chat session router")
from app.api.chat_session import router as chat_session_router

logger.info("STEP 3 - Importing documents router")
from app.api.documents import router as document_router

logger.info("STEP 4 - Importing health router")
from app.api.health import router as health_router

logger.info("STEP 5 - Importing medical records router")
from app.api.medical_records import router as record_router

logger.info("STEP 6 - Importing users router")
from app.api.users import router as user_router

logger.info("STEP 7 - Importing configuration")
from app.core.config import CORS_ORIGINS

logger.info("STEP 8 - Importing database")
from app.db.database import Base, engine

logger.info("STEP 9 - Importing FastAPI")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger.info("STEP 10 - Creating FastAPI application")

app = FastAPI(
    title="NIGHTINGALE",
    summary="Secure AI-powered Medical Document Assistant",
    description="""
# NIGHTINGALE

Secure Multimodal Medical AI Assistant.

NIGHTINGALE helps users securely understand their own medical records using
OCR, Retrieval-Augmented Generation (RAG), semantic search, and intelligent
document routing.

## Core Features

- JWT Authentication
- Patient Management
- Medical Document Upload
- OCR & Text Extraction
- Intelligent Document Selection
- Retrieval-Augmented Generation (RAG)
- Conversation Memory
- Multi-document Comparison
- Source Citations
- Provider Abstraction (Ollama / Groq)
- Health Monitoring
- Rate Limiting
- Structured Logging

## Disclaimer

NIGHTINGALE is an educational medical document understanding system.

It does **not** diagnose diseases, prescribe medications, or replace professional medical advice.
""",
    version="1.0.0",
    terms_of_service="https://github.com/<your-github>/blob/main/LICENSE",
    contact={
        "name": "Harsha",
        "url": "https://github.com/<your-github>",
    },
    license_info={
        "name": "MIT License",
    },
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User registration and JWT authentication.",
        },
        {
            "name": "Medical Records",
            "description": "Manage patient medical records.",
        },
        {
            "name": "Documents",
            "description": "Upload and manage medical documents.",
        },
        {
            "name": "Chat",
            "description": "AI-powered document understanding.",
        },
        {
            "name": "Chat Sessions",
            "description": "Conversation history management.",
        },
        {
            "name": "Health",
            "description": "Application health and dependency status.",
        },
    ],
)

logger.info("STEP 11 - FastAPI app created")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("STEP 12 - CORS middleware added")

logger.info("STEP 13 - Creating database tables")
Base.metadata.create_all(bind=engine)
logger.info("STEP 14 - Database tables ready")

logger.info("STEP 15 - Including users router")
app.include_router(user_router)

logger.info("STEP 16 - Including medical records router")
app.include_router(record_router)

logger.info("STEP 17 - Including documents router")
app.include_router(document_router)

logger.info("STEP 18 - Including chat session router")
app.include_router(chat_session_router)

logger.info("STEP 19 - Including chat router")
app.include_router(chat_router)

logger.info("STEP 20 - Including health router")
app.include_router(health_router)

logger.info("STEP 21 - NIGHTINGALE startup complete. Waiting for Uvicorn to accept connections.")
