import os

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from settings import settings


class FileService:
    """Handles file operations for both local and S3 files"""

    @staticmethod
    def read_file(file_path: str) -> bytes:
        """Read file from local path or S3 based on environment"""
        if settings.DEVELOPMENT_MODE:
            return FileService._read_local_file(file_path)
        else:
            return FileService._read_s3_file(file_path)

    @staticmethod
    def _read_local_file(file_path: str) -> bytes:
        """Read file from local filesystem"""
        # Handle both absolute and relative paths
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.LOCAL_PDF_DIR, file_path)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as f:
            return f.read()

    @staticmethod
    def _read_s3_file(s3_key: str) -> bytes:
        """Read file from S3"""
        if not settings.S3_BUCKET_NAME:
            raise ValueError("S3_BUCKET_NAME not configured")

        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            raise ValueError("AWS credentials not configured")

        try:
            # Create S3 client
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )

            # Get object from S3
            response = s3_client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_key)

            return response["Body"].read()

        except NoCredentialsError:
            raise ValueError("AWS credentials are invalid or not provided")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchKey":
                raise FileNotFoundError(f"File not found in S3: {s3_key}")
            elif error_code == "NoSuchBucket":
                raise ValueError(f"S3 bucket not found: {settings.S3_BUCKET_NAME}")
            else:
                raise RuntimeError(f"Error reading from S3: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error reading from S3: {e}")

    @staticmethod
    def get_file_name(file_path: str) -> str:
        """Extract filename from path or S3 key"""
        return os.path.basename(file_path)
