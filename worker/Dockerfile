FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x scripts/dev.py

CMD ["sh", "-c", "\
    if [ \"$CELERY_DEV_MODE\" = \"true\" ]; then \
        python scripts/dev.py; \
    else \
        celery -A tasks worker --loglevel=info; \
    fi \
"]