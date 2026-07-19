from app.db.database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    filename = Column(String, nullable=False)

    stored_filename = Column(String, nullable=False)

    file_path = Column(String)
    file_type = Column(String)

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("Users", back_populates="documents")

    text_content = relationship("DocumentText", backref="document", uselist=False)

    chunks = relationship("DocumentChunk", back_populates="document")

    document_type = Column(String, nullable=True)

    report_date = Column(String, nullable=True)

    medical_record_id = Column(
        Integer, ForeignKey("medical_records.id"), nullable=False
    )

    medical_record = relationship("MedicalRecord", back_populates="documents")

    # document_metadata = relationship(
    # "DocumentMetadata",
    # back_populates="document",
    # uselist=False,
    # cascade="all, delete-orphan"
    # )
