from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Redis configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# Create Celery app
app = Celery('worker')
app.conf.broker_url = REDIS_URL
app.conf.result_backend = REDIS_URL

# Import tasks
from tasks import *