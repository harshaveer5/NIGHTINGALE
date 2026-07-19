from datetime import datetime

from pydantic import BaseModel


class PatientSummary(BaseModel):
    id: int
    patient_name: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {"example": {"id": 1, "patient_name": "John Doe"}},
    }


class DocumentResponse(BaseModel):
    id: int
    medical_record_id: int
    filename: str
    file_type: str
    document_type: str | None = None
    report_date: str | None = None
    uploaded_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 8,
                "medical_record_id": 1,
                "filename": "blood_report.pdf",
                "file_type": "application/pdf",
                "document_type": "Blood Test",
                "report_date": "2026-06-18",
                "uploaded_at": "2026-07-12T11:30:00",
            }
        },
    }
