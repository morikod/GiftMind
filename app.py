import os
import json
from flask import Flask, render_template, request, jsonify
import httpx
from openai import OpenAI
from pypdf import PdfReader

app = Flask(__name__, static_folder='static', template_folder='templates')

# Инициализация клиента
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1"),
    http_client=httpx.Client(verify=False)
)

sessions = {}

def extract_text(file):
    try:
        if file.filename.endswith('.pdf'):
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + " "
            return text
        return file.read().decode('utf-8')
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/start", methods=["POST"])
def start_game():
    user_id = request.remote_addr
    text_context = ""
    
    if 'file' in request.files:
        text_context = extract_text(request.files['file'])
    
    topic = request.form.get("topic", "General IT Security")
    
    # Создаем сессию
    sessions[user_id] = {
        "context": text_context[:3000], 
        "topic": topic,
        "question_count": 0,
        "errors": 0,
        "current_question": None
    }
    
    return generate_question(user_id)

def generate_question(user_id):
    session = sessions.get(user_id)
    if not session:
        return jsonify({"status": "error", "message": "Session expired. Reload page."})

    session["question_count"] += 1
    
    if session["question_count"] > 10:
        return jsonify({"status": "win", "message": "TERMINAL BREACHED! You hacked the system."})

    system_prompt = (
        "You are a Security Terminal. Generate a multiple-choice question (A, B, C) in Czech. "
        f"Context: {session['context']}. Topic: {session['topic']}. "
        "Return ONLY valid JSON: {\"q\": \"otázka\", \"a\": \"možnost\", \"b\": \"možnost\", \"c\": \"možnost\", \"correct\": \"A\"}"
    )
    
    try:
        response = client.chat.completions.create(
            model="gemma3:27b",
            messages=[{"role": "system", "content": system_prompt}],
            response_format={ "type": "json_object" }
        )
        
        q_data = json.loads(response.choices[0].message.content)
        session["current_question"] = q_data # Сохраняем как объект
        
        return jsonify({
            "status": "game", 
            "data": q_data, 
            "progress": session["question_count"]
        })
    except Exception as e:
        print(f"AI Error: {e}")
        return jsonify({"status": "error", "message": "AI failed to respond."})

@app.route("/api/answer", methods=["POST"])
def check_answer():
    user_id = request.remote_addr
    data = request.json
    if not data or 'answer' not in data:
        return jsonify({"status": "error", "message": "No answer provided"})
        
    answer = data.get("answer").upper()
    session = sessions.get(user_id)
    
    if not session or not session.get("current_question"):
        return jsonify({"status": "error", "message": "No active question"})
    
    correct_answer = session["current_question"]["correct"].upper()
    
    if answer != correct_answer:
        session["errors"] += 1
        if session["errors"] >= 3:
            return jsonify({"status": "boss_fight", "message": "SECURITY ALERT! Defeat the Boss to continue."})
        return jsonify({"status": "wrong", "correct": correct_answer})
    
    return generate_question(user_id)

@app.route("/api/boss_success", methods=["POST"])
def boss_success():
    user_id = request.remote_addr
    session = sessions.get(user_id)
    if session:
        session["errors"] = 0
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
