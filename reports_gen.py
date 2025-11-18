from google import genai
from google.genai import types
import json
import os

# --- CONFIG ---
# 🚨 REPLACE WITH YOUR REAL PROJECT ID
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "local-dev-project")
LOCATION = os.getenv("GCP_REGION", "us-central1")

def analyze_blood_report(image_bytes, mime_type="image/jpeg"):
    """
    Uses Gemini 2.5 Flash Image to extract structured medical data.
    Returns a list of dictionaries.
    """
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    except Exception as e:
        print(f"❌ Client Init Error: {e}")
        return []
    
    prompt = """
    You are an expert medical OCR assistant. 
    Extract the blood test table from this image.
    
    Return a JSON list. Each item must have:
    - test_name (string)
    - result (string)
    - unit (string)
    - ref_range (string)
    - status (string: 'High', 'Low', or 'Normal')
    
    Crucial: If the image has no explicit flag, compare Result vs Range to determine status.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ]
        )
        
        text = response.text
        
        # --- FIX 2: ROBUST JSON PARSING ---
        # 1. Clean Markdown if present
        clean_text = text.replace("```json", "").replace("```", "").strip()
        # 2. Attempt load
        return json.loads(clean_text)
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON PARSING FAILED. Raw text response was not valid JSON.")
        print(f"DEBUG: {text[:200]}...") # Print first 200 chars for context
        return []
    except Exception as e:
        print(f"❌ Vision API Error: {e}")
        return []
