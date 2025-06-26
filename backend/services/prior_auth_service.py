import uuid
from typing import List, Optional

from celery_client import celery_client
from database import PriorAuthorization, UploadedFile
from schemas import PriorAuthorizationCreate, PriorAuthorizationUpdate
from sqlalchemy.orm import Session

from services.file_service import FileService


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

        # Create the prior authorization with empty auth_questions initially
        db_prior_auth = PriorAuthorization(
            id=PriorAuthService.generate_id(),
            auth_questions={},  # Initialize as empty, will be populated by worker
            **prior_auth.model_dump(),
        )

        db.add(db_prior_auth)
        db.flush()  # Get the ID without committing
        db.commit()
        db.refresh(db_prior_auth)

        # Trigger async processing of the prior authorization using chains
        try:
            result = celery_client.send_task(
                "tasks.start_processing_workflow", args=[db_prior_auth.id]
            )
            print(
                f"✓ Queued processing workflow for prior auth {db_prior_auth.id} (task ID: {result.id})"
            )
        except Exception as e:
            print(f"⚠ Failed to queue processing workflow: {str(e)}")
            # Don't fail the creation if task queueing fails

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

        file_service = FileService()

        # Get the associated files
        auth_document = db_prior_auth.auth_document
        clinical_notes = db_prior_auth.clinical_notes

        # Delete the prior authorization record
        db.delete(db_prior_auth)

        # Delete the uploaded file records
        files_to_delete = []
        if auth_document:
            files_to_delete.append(auth_document)
            db.delete(auth_document)
        if clinical_notes:
            files_to_delete.append(clinical_notes)
            db.delete(clinical_notes)

        # Commit database changes
        db.commit()

        # Delete files from S3 (done after DB commit to avoid inconsistency)
        for file_record in files_to_delete:
            file_service.delete_file(file_record.file_path)

        return True
