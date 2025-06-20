from celery_app import app
import time

@app.task
def hello_world():
    """Simple test task"""
    print("Hello from Celery worker!")
    return "Task completed successfully"

@app.task
def process_data(data):
    """Example task that processes some data"""
    print(f"Processing data: {data}")
    time.sleep(2)  # Simulate work
    return f"Processed: {data}"