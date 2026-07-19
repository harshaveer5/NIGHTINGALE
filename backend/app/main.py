from app.api.chat_router import router as chat_router
from app.api.chat_session import router as chat_session_router
from app.api.documents import router as document_router
from app.api.health import router as health_router
from app.api.medical_records import router as record_router

# Routers
from app.api.users import router as user_router
from app.core.config import CORS_ORIGINS
from app.db.database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Models


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(user_router)
app.include_router(record_router)
app.include_router(document_router)
app.include_router(chat_session_router)
app.include_router(chat_router)
app.include_router(health_router)
