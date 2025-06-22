from celery import Celery
from config.settings import settings
from database import SessionLocal, UploadedFile
from services.auth_service import extract_and_format_statements
from services.file_service import FileService
from services.parse_service import parse_to_boolean_structure

app = Celery("worker")
app.conf.broker_url = settings.REDIS_URL
app.conf.result_backend = settings.REDIS_URL


@app.task
def hello_world():
    """Simple test task"""
    print("Hello from Celery worker!")
    return "Task completed successfully"


@app.task
def process_data(data):
    """Example task that processes some data"""
    print(f"Processing data: {data}")
    return f"Processed: {data}"


@app.task
def process_prior_auth_document(file_id: str):
    """Process prior authorization document and extract questions"""

    db = SessionLocal()
    try:
        file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
        file_content = FileService.read_file(file.file_path)
        criteria = extract_and_format_statements(file_content)
        boolean_structure = parse_to_boolean_structure(criteria)

        print(boolean_structure)

    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()
