from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from werkzeug.utils import secure_filename
from datetime import datetime
# Import the new processor
from image_processor import preprocess_image
from reports_gen import analyze_blood_report
from nutrition_agent import analyze_health_report, chat_with_agent
from database_manager import save_report, get_patient_history
app = Flask(__name__)
app.secret_key = "nutri_secure_key_999"
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

USER_ID = "patient_blr_01" 

@app.route('/')
def index():
    return render_template('welcome.html')

@app.route('/upload_page')
def upload_page():
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template('upload.html', today=today)

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files: return redirect(url_for('upload_page'))
    file = request.files['file']
    report_date = request.form.get('report_date')

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        with open(filepath, "rb") as f: 
            raw_image_bytes = f.read()
            file_type = file.content_type # Get file type for processing

        # --- CRITICAL NEW STEP: IMAGE PROCESSING ---
        processed_bytes = preprocess_image(raw_image_bytes, file_type)

        # 1. Vision runs on the PROCESSED image
        report_data = analyze_blood_report(processed_bytes, 'image/jpeg') # Force type to JPEG after processing
        
        # 2. Run Agent
        summary = analyze_health_report(report_data)

        # 3. Save to DB
        save_report(USER_ID, report_data, summary, report_date)
        
        session['report_data'] = report_data
        session['medical_summary'] = summary
        session['current_date'] = report_date
        session['chat_history'] = []
        
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('upload_page'))

@app.route('/load_history')
def load_history():
    history = get_patient_history(USER_ID)
    return render_template('reports.html', history=history)

@app.route('/view_report/<report_id>')
def view_report(report_id):
    history = get_patient_history(USER_ID)
    target = next((h for h in history if h.get('id') == report_id), None)
    
    if target:
        if isinstance(target['biomarkers'], str):
            try: session['report_data'] = eval(target['biomarkers'])
            except: session['report_data'] = []
        else:
            session['report_data'] = target['biomarkers']
            
        session['medical_summary'] = target['summary']
        session['current_date'] = target['date']
        session['chat_history'] = []
        
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'report_data' not in session: return redirect(url_for('upload_page'))
    return render_template('dashboard.html', 
                         report_data=session['report_data'], 
                         summary=session['medical_summary'], 
                         chat_history=session.get('chat_history', []),
                         current_date=session.get('current_date'))

# --- API FOR CHAT (FIXED & DEBUGGED) ---
@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.json
        user_input = data.get('message')
        
        summary = session.get('medical_summary', "No context available.")
        history = session.get('chat_history', [])
        
        # Call Agent
        ai_response = chat_with_agent(user_input, summary, "Bengaluru")
        
        # Update Session
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": ai_response})
        session['chat_history'] = history
        
        return jsonify({"response": ai_response})

    except Exception as e:
        return jsonify({"response": "I encountered an error processing your request. Please try again."}), 500

@app.route('/reset')
def reset():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)