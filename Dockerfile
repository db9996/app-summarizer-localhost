# Use lightweight Python image
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y gcc

# Only copy requirements (faster build, small context)
COPY backend/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --default-timeout=100 --retries 5 -r requirements.txt


# Only copy backend code (not the full repo!)
COPY backend/ .

# Expose port if needed by Flask (Celery doesn't need it, harmless)
# Start Celery worker
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
