from app.core.logging import logger
from app.models.medical_record import MedicalRecord
from fastapi import HTTPException
from sqlalchemy.orm import Session


def get_record(db: Session, record_id: int, user_id: int):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")

    if record.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return record


def create_record(db: Session, user_id: int, record_data):
    record = MedicalRecord(
        patient_name=record_data.patient_name,
        age=record_data.age,
        gender=record_data.gender,
        medical_history=record_data.medical_history,
        user_id=user_id,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    logger.info(
        "Medical record created",
        extra={
            "user_id": user_id,
            "patient_id": record.id,
            "patient_name": record.patient_name,
        },
    )

    return record


def update_record(db: Session, record: MedicalRecord, updated_data):
    record.patient_name = updated_data.patient_name
    record.age = updated_data.age
    record.gender = updated_data.gender
    record.medical_history = updated_data.medical_history

    db.commit()
    db.refresh(record)

    logger.info(
        "Medical record updated",
        extra={"patient_id": record.id, "patient_name": record.patient_name},
    )

    return record


def delete_record(db: Session, record: MedicalRecord):
    db.delete(record)
    db.commit()

    logger.info(
        "Medical record deleted",
        extra={"patient_id": record.id, "patient_name": record.patient_name},
    )

    return {"message": "Medical record deleted successfully"}


def get_user_records(db: Session, user_id: int):
    return db.query(MedicalRecord).filter(MedicalRecord.user_id == user_id).all()
