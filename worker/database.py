import os

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class PriorAuthorization(Base):
    __tablename__ = "prior_authorizations"

    id = Column(String, primary_key=True, index=True)
    patient_name = Column(String, nullable=False)
    procedure = Column(String, nullable=False)
    date = Column(DateTime, default=func.now())
    auth_document_id = Column(String, ForeignKey("uploaded_files.id"))
    clinical_notes_id = Column(String, ForeignKey("uploaded_files.id"))
    status = Column(String, default="pending")  # pending, approved, denied
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    auth_document = relationship("UploadedFile", foreign_keys=[auth_document_id])
    clinical_notes = relationship("UploadedFile", foreign_keys=[clinical_notes_id])
    questions = relationship("MedicalNecessityQuestion", back_populates="prior_auth")


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)  # Local file path
    upload_date = Column(DateTime, default=func.now())


class MedicalNecessityQuestion(Base):
    __tablename__ = "medical_necessity_questions"

    id = Column(String, primary_key=True, index=True)
    prior_auth_id = Column(String, ForeignKey("prior_authorizations.id"))
    category = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    required = Column(Boolean, default=True)
    question_type = Column(String, default="text")  # text, boolean, multiple_choice
    created_at = Column(DateTime, default=func.now())

    # Relationships
    prior_auth = relationship("PriorAuthorization", back_populates="questions")


# Create tables
Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
