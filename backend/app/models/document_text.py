from app.db.database import Base
from sqlalchemy import Column, ForeignKey, Integer, Text


class DocumentText(Base):
    __tablename__ = "document_texts"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(Integer, ForeignKey("documents.id"), unique=True)

    extracted_text = Column(Text, nullable=False)
