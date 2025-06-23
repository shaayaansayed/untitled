import os

from dotenv import load_dotenv
from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    text,
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

    auth_questions = Column(JSON, nullable=False)

    # Relationships
    auth_document = relationship("UploadedFile", foreign_keys=[auth_document_id])
    clinical_notes = relationship("UploadedFile", foreign_keys=[clinical_notes_id])
    document_chunks = relationship(
        "DocumentChunk", back_populates="prior_authorization"
    )


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)  # Local file path
    upload_date = Column(DateTime, default=func.now())


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, index=True)
    prior_authorization_id = Column(
        String, ForeignKey("prior_authorizations.id"), nullable=False
    )
    file_id = Column(String, ForeignKey("uploaded_files.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order of chunk in document
    content = Column(Text, nullable=False)  # The actual text content
    chunk_metadata = Column(JSON)  # Additional metadata (page number, section, etc.)

    # Vector embedding (1536 dimensions for OpenAI text-embedding-ada-002)
    # Adjust dimensions based on your embedding model
    embedding = Column(Vector(1536))

    created_at = Column(DateTime, default=func.now())

    # Relationships
    prior_authorization = relationship(
        "PriorAuthorization", back_populates="document_chunks"
    )
    file = relationship("UploadedFile")

    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, chunk_index={self.chunk_index})>"


def setup_pgvector_extension():
    """Setup pgvector extension in the database"""
    with engine.connect() as conn:
        # Enable the vector extension
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()


# Create tables and setup pgvector
def initialize_database():
    """Initialize database with tables and extensions"""
    setup_pgvector_extension()
    Base.metadata.create_all(bind=engine)


initialize_database()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
