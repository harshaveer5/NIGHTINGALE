from app.db.database import Base
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class DocumentMetadata(Base):
    __tablename__ = "document_metadata"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        Integer, ForeignKey("documents.id"), unique=True, nullable=False
    )

    report_type = Column(String, nullable=True)

    report_date = Column(Date, nullable=True)

    hospital_name = Column(String, nullable=True)

    doctor_name = Column(String, nullable=True)

    department = Column(String, nullable=True)

    confidence = Column(Float, default=0.0)

    extraction_method = Column(String, default="rule_based")

    document = relationship("Document", back_populates="document_metadata")
