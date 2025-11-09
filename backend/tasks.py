import os
import re
from dotenv import load_dotenv
from celery import Celery
import google.generativeai as genai
import sys
sys.path.append('/app')  # ensures correct import in Docker
from app import app as flask_app   # <--- KEY FIX: import flask app as flask_app
from models import db, User, Summary, SummaryHistory

# Load environment variables
load_dotenv()

# Configure Celery with Redis broker/backend
celery = Celery("tasks", broker="redis://localhost:6380/0", backend="redis://localhost:6380/0")

# Initialize Gemini client
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
client = genai.GenerativeModel("models/gemini-flash-latest")

def chunk_text(text, chunk_size=4000):
    # Only use chunking for very long texts (adjust chunk_size as needed)
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) <= chunk_size:
            current += sentence + " "
        else:
            chunks.append(current.strip())
            current = sentence + " "
    if current:
        chunks.append(current.strip())
    return chunks

def generate_summary(prompt):
    try:
        response = client.generate_content(prompt)
        print("Gemini RAW response:", response)
        return response.text.strip()
    except Exception as e:
        print(f"Error during summary: {e}")
        return "Error: Unable to generate summary."

def summarize_large_text(text):
    # Use chunking for very large input, else summarize directly
    chunk_size = 4000  # Adjust as needed
    if len(text) <= chunk_size:
        return generate_summary(f"Summarize the following text:\n{text}")
    else:
        chunks = chunk_text(text, chunk_size=chunk_size)
        print(f"Input split into {len(chunks)} chunks.")
        summaries = []
        for i, chunk in enumerate(chunks):
            print(f"Summarizing chunk {i + 1}/{len(chunks)}")
            prompt = f"Summarize the following paragraph:\n{chunk}"
            summary = generate_summary(prompt)
            print(f"Chunk {i + 1} summary: {summary}")
            summaries.append(summary)
        final_prompt = "Summarize the following collection of summaries:\n" + " ".join(summaries)
        print("Generating final summary from partial summaries")
        return generate_summary(final_prompt)

@celery.task
def my_summarize_task(text, summary_id):
    with flask_app.app_context():   # <--- KEY FIX: use flask_app here!
        print("Received text:")
        print(repr(text))
        summary = summarize_large_text(text)
        print("Summary:")
        print(summary)
        # Save summary to DB
        record = Summary.query.get(summary_id)
        if record:
            record.summary = summary
            db.session.commit()
        return summary

# Celery needs to find the app with -A, so add this at the end:
app = celery
