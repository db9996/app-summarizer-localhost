import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "supersecret"
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "superjwtsecret"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "postgresql://db9996:Devu2021@localhost:5432/appsummarizer2"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS
    CORS_HEADERS = "Content-Type"

    # Celery/Redis
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL") or "redis://redis:6379/0"
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND") or "redis://redis:6379/0"

