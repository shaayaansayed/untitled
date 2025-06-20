from fastapi import APIRouter
from pydantic import BaseModel
from celery_client import celery_client

router = APIRouter()

class TaskRequest(BaseModel):
    data: str

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

@router.post("/tasks/hello", response_model=TaskResponse)
async def queue_hello_task():
    """Queue a simple hello world task"""
    result = celery_client.send_task('tasks.hello_world')
    return TaskResponse(
        task_id=result.id,
        status="queued",
        message="Hello world task queued successfully"
    )

@router.post("/tasks/process", response_model=TaskResponse)
async def queue_process_task(request: TaskRequest):
    """Queue a data processing task"""
    result = celery_client.send_task('tasks.process_data', args=[request.data])
    return TaskResponse(
        task_id=result.id,
        status="queued",
        message=f"Data processing task queued for: {request.data}"
    )

@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Get the status of a task"""
    result = celery_client.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }