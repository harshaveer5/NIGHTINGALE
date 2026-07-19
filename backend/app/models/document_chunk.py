from app.db.database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(Integer, ForeignKey("documents.id"))

    chunk_index = Column(Integer, index=True)

    chunk_text = Column(Text, nullable=False)
    embedding_created = Column(Boolean, default=False)

    document = relationship("Document", back_populates="chunks")
