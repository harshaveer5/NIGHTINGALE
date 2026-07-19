from datetime import datetime

from pydantic import BaseModel


class CreateChatSessionRequest(BaseModel):
    medical_record_id: int
    title: str

    model_config = {
        "json_schema_extra": {
            "example": {"medical_record_id": 1, "title": "Blood Test Review"}
        }
    }


class ChatSessionResponse(BaseModel):
    id: int
    medical_record_id: int
    title: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 4,
                "medical_record_id": 1,
                "title": "Blood Test Review",
                "created_at": "2026-07-14T10:30:00",
            }
        },
    }


class ChatSessionListResponse(BaseModel):
    id: int
    medical_record_id: int
    title: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 4,
                "medical_record_id": 1,
                "title": "Blood Test Review",
                "created_at": "2026-07-14T10:30:00",
            }
        },
    }

class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }