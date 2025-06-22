FROM python:3.11-slim

WORKDIR /app

# Copy worker application files
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Make development script executable
RUN chmod +x scripts/dev.py

# start command with conditional logic for development vs production
CMD ["sh", "-c", "\
    if [ \"$CELERY_DEV_MODE\" = \"true\" ]; then \
        python scripts/dev.py; \
    else \
        celery -A tasks worker --loglevel=info; \
    fi \
"]