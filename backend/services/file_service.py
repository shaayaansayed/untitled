import os
import uuid
from pathlib import Path
from typing import Tuple

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException, UploadFile


class FileService:
    def __init__(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")

        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME environment variable is required")

        try:
            self.s3_client = boto3.client(
                "s3",
                region_name=self.aws_region,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            )
        except NoCredentialsError:
            raise ValueError("AWS credentials not configured properly")

    def generate_file_key(self, file_type: str, original_filename: str) -> str:
        """Generate a unique S3 key for the file"""
        file_id = str(uuid.uuid4())
        file_extension = Path(original_filename).suffix
        return f"{file_type}/{file_id}{file_extension}"

    def validate_file(self, file: UploadFile, file_type: str) -> None:
        """Validate uploaded file"""
        # Check file type
        if not file.content_type == "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if file.size and file.size > max_size:
            raise HTTPException(
                status_code=400, detail="File size too large (max 10MB)"
            )

        # Validate file type parameter
        valid_types = ["prior_authorization", "clinical_notes"]
        if file_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Must be one of: {valid_types}",
            )

    async def upload_file(self, file: UploadFile, file_type: str) -> Tuple[str, str]:
        """
        Upload file to S3 and return (file_id, s3_key)

        Args:
            file: The uploaded file
            file_type: Type of file ("prior_authorization" or "clinical_notes")

        Returns:
            Tuple of (file_id, s3_key)
        """
        self.validate_file(file, file_type)

        # Generate unique file key
        s3_key = self.generate_file_key(file_type, file.filename)
        file_id = s3_key.split("/")[1].split(".")[0]  # Extract UUID from key

        try:
            # Upload file to S3
            file.file.seek(0)  # Reset file pointer
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    "ContentType": file.content_type,
                    "Metadata": {
                        "original_filename": file.filename,
                        "file_type": file_type,
                    },
                },
            )

            return file_id, s3_key

        except ClientError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to upload file: {str(e)}"
            )

    def get_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for file access"""
        try:
            response = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expiration,
            )
            return response
        except ClientError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to generate presigned URL: {str(e)}"
            )

    def delete_file(self, s3_key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            print(f"Error deleting file {s3_key}: {str(e)}")
            return False
