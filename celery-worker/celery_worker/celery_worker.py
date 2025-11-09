from backend.app import app
from models import db, Summary
from celery import Celery

celery = Celery("tasks", broker=app.config["CELERY_BROKER_URL"], backend=app.config["CELERY_RESULT_BACKEND"])

@celery.task
def my_summarize_task(text, summary_id):
    with app.app_context():
        record = Summary.query.get(summary_id)
        ...
        db.session.commit()
