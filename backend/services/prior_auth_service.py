import uuid
from typing import List, Optional

from database import MedicalNecessityQuestion, PriorAuthorization, UploadedFile
from schemas import PriorAuthorizationCreate, PriorAuthorizationUpdate
from sqlalchemy.orm import Session


class PriorAuthService:
    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def get_all(db: Session) -> List[PriorAuthorization]:
        return db.query(PriorAuthorization).all()

    @staticmethod
    def get_by_id(db: Session, auth_id: str) -> Optional[PriorAuthorization]:
        return (
            db.query(PriorAuthorization)
            .filter(PriorAuthorization.id == auth_id)
            .first()
        )

    @staticmethod
    def create(db: Session, prior_auth: PriorAuthorizationCreate) -> PriorAuthorization:
        # Verify files exist
        auth_doc = (
            db.query(UploadedFile)
            .filter(UploadedFile.id == prior_auth.auth_document_id)
            .first()
        )
        clinical_notes = (
            db.query(UploadedFile)
            .filter(UploadedFile.id == prior_auth.clinical_notes_id)
            .first()
        )

        if not auth_doc or not clinical_notes:
            raise ValueError("Referenced files not found")

        db_prior_auth = PriorAuthorization(
            id=PriorAuthService.generate_id(), **prior_auth.model_dump()
        )

        # Add default medical necessity questions
        default_questions = [
            {
                "category": "Patient History",
                "question": "Has the patient tried conservative treatment for at least 6 weeks?",
            },
            {
                "category": "Patient History",
                "question": "Are there any documented physical therapy sessions?",
            },
            {
                "category": "Current Symptoms",
                "question": "Is there presence of neurological symptoms?",
            },
            {
                "category": "Current Symptoms",
                "question": "Pain level on a scale of 1-10?",
            },
            {
                "category": "Imaging",
                "question": "Has an X-ray been performed in the last 3 months?",
            },
        ]

        db.add(db_prior_auth)
        db.flush()  # Get the ID

        # Add questions
        for q_data in default_questions:
            question = MedicalNecessityQuestion(
                id=PriorAuthService.generate_id(),
                prior_auth_id=db_prior_auth.id,
                **q_data,
            )
            db.add(question)

        db.commit()
        db.refresh(db_prior_auth)
        return db_prior_auth

    @staticmethod
    def update(
        db: Session, auth_id: str, prior_auth_update: PriorAuthorizationUpdate
    ) -> Optional[PriorAuthorization]:
        db_prior_auth = PriorAuthService.get_by_id(db, auth_id)
        if not db_prior_auth:
            return None

        update_data = prior_auth_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_prior_auth, field, value)

        db.commit()
        db.refresh(db_prior_auth)
        return db_prior_auth

    @staticmethod
    def delete(db: Session, auth_id: str) -> bool:
        db_prior_auth = PriorAuthService.get_by_id(db, auth_id)
        if not db_prior_auth:
            return False

        db.delete(db_prior_auth)
        db.commit()
        return True
