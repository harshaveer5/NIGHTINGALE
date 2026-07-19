from app.db.database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    medical_record_id = Column(
        Integer, ForeignKey("medical_records.id"), nullable=False
    )

    title = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan"
    )
