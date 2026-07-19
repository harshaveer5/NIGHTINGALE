from app.db.database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    patient_name = Column(String, nullable=False)

    age = Column(Integer)

    gender = Column(String)

    medical_history = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("Users", back_populates="medical_records")

    documents = relationship(
        "Document", back_populates="medical_record", cascade="all, delete"
    )
