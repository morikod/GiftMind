import os
from flask import Flask, render_template, request, jsonify
import httpx
from openai import OpenAI
from pypdf import PdfReader # Библиотека для RAG

app = Flask(__name__, static_folder='static', template_folder='templates')

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1"),
    http_client=httpx.Client(verify=False)
)

# Хранилище сессий (в реальности лучше использовать Redis, но для лимитов Курима сойдет dict)
sessions = {}

def extract_text(file):
    if file.filename.endswith('.pdf'):
        reader = PdfReader(file)
        return " ".join([page.extract_text() for page in reader.pages])
    return file.read().decode('utf-8')

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
    
    sessions[user_id] = {
        "context": text_context[:2000], # Ограничение для контекста
        "topic": topic,
        "question_count": 0,
        "errors": 0,
        "history": []
    }
    
    return generate_question(user_id)

def generate_question(user_id):
    session = sessions[user_id]
    session["question_count"] += 1
    
    if session["question_count"] > 10:
        return jsonify({"status": "win", "message": "TERMINAL BREACHED! You hacked the system."})

    system_prompt = (
        "You are a Security Terminal. Generate a multiple-choice question (A, B, C). "
        f"Context: {session['context']}. Topic: {session['topic']}. "
        "Return ONLY JSON: {\"q\": \"question\", \"a\": \"opt\", \"b\": \"opt\", \"c\": \"opt\", \"correct\": \"A\"}"
    )
    
    response = client.chat.completions.create(
        model="gemma3:27b",
        messages=[{"role": "system", "content": system_prompt}],
        response_format={ "type": "json_object" }
    )
    
    q_data = response.choices[0].message.content
    session["current_question"] = q_data # Сохраняем для проверки
    return jsonify({"status": "game", "data": q_data, "progress": session["question_count"]})

@app.route("/api/answer", methods=["POST"])
def check_answer():
    user_id = request.remote_addr
    answer = request.json.get("answer").upper()
    session = sessions.get(user_id)
    
    correct_answer = eval(session["current_question"])["correct"]
    
    if answer != correct_answer:
        session["errors"] += 1
        if session["errors"] >= 3:
            return jsonify({"status": "boss_fight", "message": "SECURITY ALERT! Defeat the Boss to continue."})
        return jsonify({"status": "wrong", "correct": correct_answer})
    
    return generate_question(user_id)
