from datetime import datetime

from pydantic import BaseModel


class PatientSummary(BaseModel):
    medical_record_id: int
    patient_name: str
    age: int | None = None
    gender: str | None = None

    class Config:
        from_attributes = True


class DocumentSummaryResponse(BaseModel):
    document_id: int
    filename: str
    file_type: str
    document_type: str | None = None
    uploaded_at: datetime

    patient: PatientSummary

    class Config:
        from_attributes = True
