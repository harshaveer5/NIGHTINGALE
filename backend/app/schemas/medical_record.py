from datetime import datetime

from pydantic import BaseModel, Field

age: int = Field(..., ge=0, le=150)


class MedicalRecordCreate(BaseModel):
    patient_name: str
    age: int
    gender: str
    medical_history: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_name": "John Doe",
                "age": 42,
                "gender": "Male",
                "medical_history": "History of hypertension and type 2 diabetes.",
            }
        }
    }


class MedicalRecordResponse(BaseModel):
    id: int
    patient_name: str
    age: int
    gender: str
    medical_history: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "patient_name": "John Doe",
                "age": 42,
                "gender": "Male",
                "medical_history": "History of hypertension and type 2 diabetes.",
                "created_at": "2026-07-12T10:30:00",
            }
        },
    }


class MedicalRecordUpdate(BaseModel):
    patient_name: str
    age: int
    gender: str
    medical_history: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_name": "John Doe",
                "age": 43,
                "gender": "Male",
                "medical_history": "Hypertension under control with medication.",
            }
        }
    }
