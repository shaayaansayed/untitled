import os

from dotenv import load_dotenv

# Load .env file if it exists (for local development)
load_dotenv()


class Settings:
    # Environment detection
    DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"

    # Redis configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

    # API configuration
    DATALAB_API_KEY = os.getenv("DATALAB_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    # File storage configuration
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

    # Development settings
    LOCAL_PDF_DIR = os.getenv("LOCAL_PDF_DIR", "./dev/sample_pdfs")
    CACHE_DIR = os.getenv("CACHE_DIR", "./dev/cached_responses")


settings = Settings()
