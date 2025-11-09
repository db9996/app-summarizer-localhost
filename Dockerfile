# Use lightweight Python image
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y gcc

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy app code
COPY . .

# Set environment variables
ENV FLASK_APP=app
ENV FLASK_ENV=production

# Expose the Flask port
EXPOSE 5001

# CMD for development (remove/rewrite if using gunicorn for prod)
CMD ["celery", "-A", "backend.tasks", "worker", "--loglevel=info"]
# For gunicorn production:
# CMD ["gunicorn", "-b", "0.0.0.0:5001", "app:app"]
