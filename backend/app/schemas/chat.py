from typing import Dict, List, Optional

from pydantic import BaseModel


class SourceCitation(BaseModel):
    document_id: int
    filename: str
    chunk_index: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "document_id": 12,
                "filename": "blood_report.pdf",
                "chunk_index": 4,
            }
        }
    }


class ChatRequest(BaseModel):
    session_id: int | None = None
    medical_record_id: int
    question: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": 3,
                "medical_record_id": 1,
                "question": "Summarize my latest blood test and explain any abnormal values.",
            }
        }
    }


class ChatResponse(BaseModel):
    answer: str

    intent: str

    confidence: float

    sources: List[SourceCitation]

    suggested_questions: List[str]

    warning: Optional[str] = None

    processing_time_ms: Optional[float] = None

    latency_trace: Optional[Dict] = None

    response_source: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "answer": "Your hemoglobin level is slightly below the normal range, which may indicate mild anemia. Please consult your healthcare provider for interpretation in the context of your medical history.",
                "intent": "REPORT_SUMMARY",
                "confidence": 0.97,
                "sources": [
                    {
                        "document_id": 12,
                        "filename": "blood_report.pdf",
                        "chunk_index": 4,
                    }
                ],
                "suggested_questions": [
                    "Compare this report with my previous one.",
                    "Explain my cholesterol values.",
                    "What does low hemoglobin mean?",
                ],
                "warning": None,
                "processing_time_ms": 418.7,
                "latency_trace": {"planner": 8, "retrieval": 74, "llm": 325},
                "response_source": "groq",
            }
        }
    }


class LatencyTrace(BaseModel):
    planner: float
    retrieval: float
    llm: float


latency_trace: Optional[LatencyTrace] = None
