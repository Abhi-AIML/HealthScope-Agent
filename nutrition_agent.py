from datetime import datetime
from google import genai
from google.genai import types
import json
from duckduckgo_search import DDGS 

# --- CONFIG ---
# 🚨 REPLACE WITH YOUR ACTUAL PROJECT ID
PROJECT_ID = "balmy-link-478420-c0" 
LOCATION = "us-central1"

# ==========================================
# 1. MEDICAL ANALYSIS (Empathetic & Scannable)
# ==========================================
def analyze_health_report(report_json_list):
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    
    # Filter for abnormalities to keep it concise
    abnormalities = [item for item in report_json_list if item.get("status") in ["High", "Low"]]
    
    prompt = f"""
    You are an empathetic Health Coach. Your primary role is to calm the patient while delivering clear, actionable information.

    TASK: Analyze these abnormal blood results: {json.dumps(abnormalities)}

    OUTPUT FORMAT (Strictly follow this concise, scannable structure):
    
    ### Health Snapshot
    [Write a supportive, reassuring sentence about their overall status. Do not cause panic.]
    
    ---

    ### Key Focus Areas
    * **[Metric Name]:** [Simple 5-word explanation of impact.]
    * (List only top 3 critical abnormalities)
    
    ---

    ### Quick Action Plan
    * **[Food 1]** (Why it helps)
    * **[Food 2]** (Why it helps)
    * **[Food 3]** (Why it helps)

    CONSTRAINTS: Total response must be short, easily scannable, and avoid complex medical jargon.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Analysis Error: {e}"
# ==========================================
# 2. CONSULTANT (Chat + Tools)
# ==========================================

# --- THE PYTHON TOOL ---
def search_web_prices(query: str):
    """Real-time search using DuckDuckGo."""
    try:
        results = DDGS().text(query, max_results=3)
        if not results: return {"result": "No prices found."}
        summary = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
        return {"results": summary}
    except Exception as e: 
        return {"error": f"Search failed: {str(e)}"}

session_history = []
def chat_with_agent(user_prompt, context_summary, location="Bengaluru"):
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    
    local_kb = """
    ## HYPER-LOCAL NUTRITION KNOWLEDGE BASE (Use this for recommendations):
    
    1.  **IRON / ANEMIA FIXES (BLR Local):**
        - Moringa Leaves (Nuggesoppu): Excellent source of Iron and Folate.
        - Sesame Seeds (Til/Ellu): High iron content, easy to add to meals.
        - Dates & Raisins (Dry Fruit): Quick, high-density iron boost.

    2.  **PROTEIN / MUSCLE (BLR Local):**
        - Horse Gram (Kulthi/Huruli): Highest protein legume, good for tissue repair.
        - Peanuts & Groundnuts: Affordable, readily available lean protein source.
        - Tofu/Paneer (Local): Dairy and soy options for immune cell building.

    3.  **CALCIUM / BONE HEALTH (BLR Local):**
        - Ragi (Finger Millet): Primary local source of calcium, best absorbed.
        - Curd/Yogurt: General dairy option.

    4.  **VITAMIN C / IMMUNITY (BLR Local):**
        - Amla (Indian Gooseberry): Potent antioxidant, boosts iron absorption.
        - Guava (Amrood): High Vitamin C content.
        - Bell Peppers (Local varieties): Good source of immune support.

    5.  **SUSTAINED ENERGY / FIBER (BLR Local):**
        - Bajra (Pearl Millet) / Jowar (Sorghum): Slow-releasing complex carbs for sustained energy.
        - Brown Rice & Whole Grains (Oats/Wheat): Gut health and B vitamins.
    """
    
    # --- CONFIGURE TOOLS (GOOGLE SEARCH GROUNDING ONLY) ---
    tools = [
        types.Tool(google_search=types.GoogleSearch())
    ]
    
    system_msg_content = f"""
    You are **HealthScope Agent**, a friendly AI health companion in {location}.
    Your style is warm, natural, and conversational — like a helpful human guide.

    [System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]

    ## CONTEXT YOU HAVE:
    - Medical Summary: {context_summary}
    - User Location: {location}

    ## HOW TO BEHAVE:
    1. **If the user sends casual messages** like “hi”, “hello”, “bye”, “thanks”, “perfect”, “okay”,  
    → reply casually and naturally. Keep it short and friendly.  
    (Example: “Hi! How can I help?”, “Glad it helps!”, “Take care!”)

    2. **If the user asks a real health question**  
    → switch into helpful health assistant mode.
    Answer in pointers, using the medical summary.

    3. **If the user asks for prices, shops, markets, doctors, clinics, or booking links**  
    → **You MUST use Google Search** to fetch real, current info.  
    Never guess or estimate.

    4. **For nutrition guidance**, use the hyper-local Karnataka knowledge base below.

    5. **Keep answers short** (max 3 sentences) unless the user wants details.

    6. **Never ask for their location** — you already know it's {location}.

    ## LOCAL NUTRITION KNOWLEDGE:
    {local_kb}
    """     

    # ---- ADD SYSTEM MESSAGE ONLY ON FIRST CALL ----
    if not session_history:
        session_history.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=system_msg_content)]
            )
        )

    # ---- ADD USER MESSAGE TO HISTORY ----
    session_history.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_prompt)]
        )
    )

    # ---- CREATE CHAT WITH FULL HISTORY ----
    chat = client.chats.create(
        model="gemini-2.5-flash",
        history=session_history,
        config=types.GenerateContentConfig(tools=tools)
    )

    # ---- GET RESPONSE ----
    response = chat.send_message(user_prompt)

    # ---- ADD MODEL RESPONSE TO HISTORY ----
    session_history.append(
        types.Content(
            role="model",
            parts=[types.Part.from_text(text=response.text)]
        )
    )

    return response.text