from app.models.medical_record import MedicalRecord
from sqlalchemy.orm import Session


def build_patient_context(db: Session, medical_record_id: int, user_id: int):
    patient = (
        db.query(MedicalRecord)
        .filter(MedicalRecord.id == medical_record_id, MedicalRecord.user_id == user_id)
        .first()
    )

    if not patient:
        return ""

    return f"""
Patient Information

Name: {patient.patient_name}

Age: {patient.age}

Gender: {patient.gender}

Medical History:
{patient.medical_history}
"""
