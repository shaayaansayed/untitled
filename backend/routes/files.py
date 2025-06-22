from celery_client import celery_client
from database import UploadedFile, get_db
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import RedirectResponse
from schemas import UploadedFileResponse
from services.file_service import FileService
from sqlalchemy.orm import Session

router = APIRouter()
file_service = FileService()


@router.post("/upload", response_model=UploadedFileResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = Query(
        ..., description="Type of file: 'prior_authorization' or 'clinical_notes'"
    ),
    db: Session = Depends(get_db),
):
    """
    Upload PDF file to S3 bucket

    Args:
        file: The PDF file to upload
        file_type: Type of file ('prior_authorization' or 'clinical_notes')
    """
    try:
        # Upload file to S3
        file_id, s3_key = await file_service.upload_file(file, file_type)

        # Save file metadata to database
        db_file = UploadedFile(
            id=file_id,
            filename=s3_key.split("/")[-1],  # Get filename from S3 key
            original_name=file.filename,
            mime_type=file.content_type,
            size=file.size,
            file_path=s3_key,  # Store S3 key as file_path
        )

        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        if file_type == "prior_authorization":
            _ = celery_client.send_task(
                "tasks.process_prior_auth_document",
                args=[db_file.id],
            )
        return db_file

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/{file_id}")
def get_file(file_id: str, db: Session = Depends(get_db)):
    """
    Get file by redirecting to presigned S3 URL
    """
    db_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Generate presigned URL for the file
        presigned_url = file_service.get_presigned_url(db_file.file_path)
        return RedirectResponse(url=presigned_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to access file: {str(e)}")


@router.delete("/{file_id}")
def delete_file(file_id: str, db: Session = Depends(get_db)):
    """Delete file from both S3 and database"""
    db_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete from S3
    file_service.delete_file(db_file.file_path)

    # Delete from database
    db.delete(db_file)
    db.commit()

    return {"message": "File deleted successfully"}
