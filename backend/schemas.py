from datetime import datetime
from typing import List, Optional

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


class MedicalNecessityQuestionBase(BaseModel):
    category: str
    question: str
    answer: Optional[str] = None
    required: bool = True
    question_type: str = "text"


class MedicalNecessityQuestionCreate(MedicalNecessityQuestionBase):
    pass


class MedicalNecessityQuestionUpdate(BaseModel):
    answer: str


class MedicalNecessityQuestionResponse(MedicalNecessityQuestionBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    prior_auth_id: str
    created_at: datetime


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
    auth_document: Optional[UploadedFileResponse] = None
    clinical_notes: Optional[UploadedFileResponse] = None


class PriorAuthorizationDetailResponse(PriorAuthorizationResponse):
    questions: List[MedicalNecessityQuestionResponse] = []


class QuestionAnswerUpdate(BaseModel):
    question_id: str
    answer: str
