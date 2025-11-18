from google.cloud import firestore
from datetime import datetime
import uuid
import os

# --- CONFIG ---
# 🚨 REPLACE WITH YOUR ACTUAL PROJECT ID
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "local-dev-project")
LOCATION = os.getenv("GCP_REGION", "us-central1")

def get_db():
    """
    Initializes the Firestore Client.
    """
    try:
        db = firestore.Client(project=PROJECT_ID)
        return db
    except Exception as e:
        return None

def save_report(user_id, report_json, summary_text, report_date):
    """
    Saves the report to Google Cloud Firestore.
    """
    db = get_db()
    if not db: return None

    try:
        data = {
            "user_id": user_id,
            "date": report_date,
            "created_at": datetime.now(),
            "summary": summary_text,
            "biomarkers": report_json,
            "status": "Analyzed"
        }
        update_time, doc_ref = db.collection("users").document(user_id).collection("reports").add(data)
        return doc_ref.id
    except Exception as e:
        return None

def get_patient_history(user_id):
    """
    Fetches all reports for a user from Firestore.
    Returns a list of dictionaries.
    """
    db = get_db()
    if not db: return []

    try:
        docs_stream = db.collection("users").document(user_id).collection("reports").stream()
        
        history = []
        for doc in docs_stream:
            record = doc.to_dict()
            record['id'] = doc.id
            
            if 'created_at' in record and hasattr(record['created_at'], 'isoformat'):
                record['created_at'] = record['created_at'].isoformat()
                
            history.append(record)
        
        # Sort by date, newest first
        history.sort(key=lambda x: x.get('date', ''), reverse=True)
        return history
    except Exception as e:
        return []