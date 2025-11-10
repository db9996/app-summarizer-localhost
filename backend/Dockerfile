# Use lightweight Python image
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y gcc

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY backend /app

# Set environment variables
ENV FLASK_APP=app
ENV FLASK_ENV=production

# Expose the Flask port
EXPOSE 5001

# CMD for development (remove/rewrite if using gunicorn for prod)
#CMD ["gunicorn", "-b", "0.0.0.0:5001", "app:app"]
# For gunicorn production:
# CMD ["gunicorn", "-b", "0.0.0.0:5001", "app:app"]
