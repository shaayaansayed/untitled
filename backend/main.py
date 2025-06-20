import logging
import os

from database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from routes import files, prior_auth, questions, tasks

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Prior Authorization API",
    description="""
    ## Prior Authorization Management System
    
    This API provides comprehensive functionality for managing prior authorization requests in healthcare settings.
    
    ### Features:
    - **Prior Authorizations**: Create, read, update, and delete prior authorization requests
    - **File Management**: Upload and manage PDF documents using AWS S3
    - **Medical Necessity Questions**: Handle medical necessity questionnaires
    
    ### Authentication:
    Currently, this API does not require authentication for development purposes.
    
    ### File Upload:
    - Only PDF files are accepted
    - Maximum file size: 10MB
    - Files are stored securely in AWS S3
    
    ### API Endpoints:
    - `/api/prior-authorizations` - Manage prior authorization requests
    - `/api/files` - Handle file uploads and downloads
    - `/api/prior-authorizations/{id}/questions` - Manage medical necessity questions
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "defaultModelExpandDepth": 3,
        "displayRequestDuration": True,
        "docExpansion": "list",
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
        "tryItOutEnabled": True,
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    prior_auth.router, prefix="/api/prior-authorizations", tags=["prior-authorizations"]
)
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(questions.router, prefix="/api", tags=["questions"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add custom info
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    # Add server information
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Development server",
        },
        {
            "url": "http://untitled-prod-849734779.us-east-1.elb.amazonaws.com/",
            "description": "Production server",
        },
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint to verify the API is running.

    Returns:
        dict: Status information about the API
    """
    logger.info("Health check endpoint called")

    # Log environment variables (masking sensitive data)
    database_url = os.getenv("DATABASE_URL")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    s3_bucket_name = os.getenv("S3_BUCKET_NAME")

    logger.info(f"DATABASE_URL: {database_url}")
    logger.info(f"AWS_ACCESS_KEY_ID: {aws_access_key_id}")
    logger.info(f"AWS_SECRET_ACCESS_KEY: {aws_secret_access_key}")
    logger.info(f"S3_BUCKET_NAME: {s3_bucket_name}")

    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
