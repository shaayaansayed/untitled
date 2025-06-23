from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


# Pydantic Models for API
class UploadedFileBase(BaseModel):
    filename: str
    original_name: str
    mime_type: str
    size: int


class UploadedFileResponse(UploadedFileBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    file_path: str
    upload_date: datetime

    @property
    def url(self) -> str:
        return f"/api/files/{self.id}"


class PriorAuthorizationBase(BaseModel):
    patient_name: str
    procedure: str


class PriorAuthorizationCreate(PriorAuthorizationBase):
    auth_document_id: str
    clinical_notes_id: str


class PriorAuthorizationUpdate(BaseModel):
    patient_name: Optional[str] = None
    procedure: Optional[str] = None
    status: Optional[str] = None


class PriorAuthorizationResponse(PriorAuthorizationBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    date: datetime
    status: str
    created_at: datetime
    updated_at: datetime
    auth_questions: Optional[Dict[str, Any]] = None  # Added this field!
    auth_document: Optional[UploadedFileResponse] = None
    clinical_notes: Optional[UploadedFileResponse] = None


class QuestionAnswerUpdate(BaseModel):
    question_id: str
    answer: str
