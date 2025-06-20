from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Redis configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# Create Celery client for sending tasks
celery_client = Celery('worker')
celery_client.conf.broker_url = REDIS_URL
celery_client.conf.result_backend = REDIS_URL