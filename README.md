# **HealthScope Agent**

HealthScope Agent is a serverless application that extracts medical lab report data and provides hyper-local, actionable health recommendations. It uses the **Gemini 2.5 Flash** model family, **Google Search Grounding**, and **Cloud Run** to deliver real-time, personalized insights.

---

## **How It Works**

The application follows a simple data flow from user upload to actionable insights.

```
User Upload (Image/PDF)
       │
       ▼
[ app.py: /analyze ]
       │
       ├─> [ image_processor.py ] -> Preprocesses image for clarity
       │
       ├─> [ reports_gen.py ] -> Extracts biomarkers with Gemini Vision
       │
       ├─> [ nutrition_agent.py ] -> Generates summary & recommendations
       │
       └─> [ database_manager.py ] -> Saves report to Firestore
       │
       ▼
[ Renders Dashboard ]
```

---

## **Features**

### **Multimodal Report Extraction**
Extracts biomarkers from PDF or image lab reports using **Gemini 1.5 Flash**, converting them into structured JSON.

### **Hyper-Local Nutrition Guidance**
Provides region-specific, affordable food recommendations (e.g., Moringa, Ragi) instead of generic supplements.

### **Real-Time Grounded Search**
Uses official **Google Search Grounding** to fetch:
- Current food prices
- Local availability
- Nearby specialist clinics

### **💬 Empathetic Health Summaries**
Generates clear, non-technical explanations of medical results with safety-aware recommendations.

### **📁 Patient History Storage**
Stores patient lab reports in **Cloud Firestore**, enabling longitudinal tracking and trend analysis.

---

## **Tech Stack**

- **Cloud:** Google Cloud Run, Cloud Firestore
- **AI:** Gemini 1.5 Flash, Google Search Grounding
- **Backend:** Python, Flask
- **Frontend:** HTML, Tailwind CSS

---

## **Running Locally**

1. **Authenticate Google Cloud**
   ```bash
   gcloud auth application-default login
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the app**
   ```bash
   python app.py
   ```
   The application will be available at `http://localhost:8080`.

---

## **☁️ Deploying to Cloud Run**

1. **Build the container image**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/healthscope-agent
   ```

2. **Deploy the service**
   ```bash
   gcloud run deploy healthscope-agent \
     --image gcr.io/PROJECT-ID/healthscope-agent \
     --platform managed
   ```
   > **Note:** Replace `PROJECT-ID` with your actual Google Cloud project ID.

---

## **📂 Repository Structure**

```
├── app.py                  # Main Flask application routes and logic
├── image_processor.py      # Image preprocessing functions
├── reports_gen.py          # Gemini Vision logic for biomarker extraction
├── nutrition_agent.py      # Gemini agent for summaries and chat
├── database_manager.py     # Firestore functions for data persistence
├── templates/              # HTML templates for the frontend
├── static/                 # CSS and JS assets
├── requirements.txt        # Python dependencies
└── README.md               # You are here!
```
