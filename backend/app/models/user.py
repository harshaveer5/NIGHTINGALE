from app.db.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    medical_records = relationship(
        "MedicalRecord", back_populates="owner", cascade="all, delete"
    )

    documents = relationship("Document", back_populates="owner", cascade="all, delete")
