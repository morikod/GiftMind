import os
import json
import httpx
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from pypdf import PdfReader

app = Flask(__name__, static_folder='static', template_folder='templates')

# Инициализация клиента AI (Курим сервер)
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1"),
    http_client=httpx.Client(verify=False)
)

# Хранилище сессий в оперативной памяти (в реальности лучше Redis)
sessions = {}

def extract_text(file):
    try:
        if file.filename.endswith('.pdf'):
            reader = PdfReader(file)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            return text
        return file.read().decode('utf-8')
    except Exception as e:
        print(f"Extraction Error: {e}")
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
    
    # Расширенная структура сессии
    sessions[user_id] = {
        "context": text_context[:4000], # Ограничение контекста для Gemma 3
        "topic": topic,
        "question_count": 0,
        "errors": 0,
        "current_question": None,
        "wrong_answers_history": [] # История ошибок для финального анализа
    }
    
    return generate_question(user_id)

def generate_question(user_id):
    session = sessions.get(user_id)
    if not session:
        return jsonify({"status": "error", "message": "Session expired."})

    session["question_count"] += 1
    
    # ПОБЕДА: Генерируем Анализ и Конспект
    if session["question_count"] > 10:
        return generate_final_analysis(user_id)

    # Улучшенный промпт для Gemma 3. Теперь он генерирует ПЛИ тесты ИЛИ открытые вопросы.
    system_prompt = (
        "Jsi učitel kyberbezpečnosti v hackerském terminálu. Tvým úkolem je prověřit studenta. "
        f"Použij tento kontext: {session['context']}. Téma: {session['topic']}. Question {session['question_count']}/10. "
        "Vytvoř buď TEST (A,B,C) nebo OTEVŘENOU otázku, kde student musí napsat text. "
        "Vrať POUZE validní JSON. "
        "Pro TEST (type='quiz'): {'type': 'quiz', 'q': 'otázka', 'a': 'opt', 'b': 'opt', 'c': 'opt', 'correct': 'A'} "
        "Pro OTEVŘENOU (type='open'): {'type': 'open', 'q': 'otázka, kde student píše text'}"
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
            "type": q_data.get("type", "quiz"), # Передаем тип фронтенду
            "data": q_data, 
            "progress": session["question_count"],
            "errors": session["errors"]
        })
    except Exception as e:
        print(f"Generation Error: {e}")
        return jsonify({"status": "error", "message": "Failed to generate question."})

@app.route("/api/answer", methods=["POST"])
def check_answer():
    user_id = request.remote_addr
    data = request.json
    user_answer = data.get("answer", "").strip()
    session = sessions.get(user_id)
    
    if not session or not session.get("current_question"):
        return jsonify({"status": "error", "message": "No active question."})
    
    q_data = session["current_question"]
    q_type = q_data.get("type", "quiz")

    # ЛОГИКА ДЛЯ ТЕСТОВ (A, B, C)
    if q_type == "quiz":
        correct_answer = q_data["correct"].upper()
        if user_answer.upper() != correct_answer:
            session["errors"] += 1
            # Запоминаем ошибку
            session["wrong_answers_history"].append({
                "question": q_data["q"],
                "your_answer": user_answer.upper(),
                "correct_answer": correct_answer,
                "context_slice": session["context"][:200]
            })
            
            if session["errors"] >= 3:
                return jsonify({"status": "boss_fight"})
            return jsonify({"status": "wrong", "correct": correct_answer})
        
        return generate_question(user_id)

    # ЛОГИКА ДЛЯ ОТКРЫТЫХ ВОПРОСОВ (Gemma 3 анализирует текст)
    elif q_type == "open":
        analysis_prompt = (
            "Jsi učitel kyberbezpečnosti. Student odpověděl na otevřenou otázку textem. "
            f"Otázka: {q_data['q']}. Odpověď studenta: {user_answer}. Kontext: {session['context']}. "
            "Analyzuj odpověď. Je správná? Pokud ne, vysvětli proč a pomoz mu se naučit. "
            "Vrať validní JSON: {'is_correct': true/false, 'explanation': 'vysvětlení v češtině'}"
        )
        
        try:
            eval_response = client.chat.completions.create(
                model="gemma3:27b",
                messages=[{"role": "user", "content": analysis_prompt}],
                response_format={ "type": "json_object" }
            )
            
            eval_data = json.loads(eval_response.choices[0].message.content)
            
            if not eval_data['is_correct']:
                session["errors"] += 1
                session["wrong_answers_history"].append({
                    "question": q_data["q"],
                    "your_answer": user_answer,
                    "explanation": eval_data['explanation']
                })
                
                if session["errors"] >= 3:
                    return jsonify({"status": "boss_fight"})
                
                # Показываем объяснение от Gemma 3, но переходим к следующему вопросу
                next_q_resp = generate_question(user_id)
                res = next_q_resp.get_json()
                res["status"] = "open_wrong" # Специальный статус для фронтенда
                res["explanation"] = eval_data['explanation']
                return jsonify(res)
            
            # Если правильно - просто следующий вопрос
            return generate_question(user_id)
            
        except Exception as e:
            print(f"Open Eval Error: {e}")
            return generate_question(user_id) # На всякий случай идем дальше

@app.route("/api/boss_success", methods=["POST"])
def boss_success():
    user_id = request.remote_addr
    session = sessions.get(user_id)
    if session:
        session["errors"] = 0 # Сброс ошибок
        # Мы НЕ генерируем вопрос, JS просто должен сказать "ОК" и 
        # при следующем вводе пользователя игра продолжится.
        return jsonify({"status": "success", "message": "Boss defeated. System integrity restored."})
    return jsonify({"status": "error"})

def generate_final_analysis(user_id):
    session = sessions[user_id]
    history = json.dumps(session["wrong_answers_history"])
    
    # Промпт для Gemma 3: сделать Анализ + Конспект на основе PDF
    final_prompt = (
        "Jsi školní bezpečnostní systém. Student dokončil test. "
        f"Zde je historie jeho chyb: {history}. Zde je kontext z PDF: {session['context']}. "
        "Vytvoř v češtině:\n"
        "1. Stručný ANALÝZ chyb (kde udělal chybu, co musí doуčit).\n"
        "2. Краткий КОНСПЕКТ (conspectus) z PDF dat, který mu pomůže tyto mezery zaplnit."
    )
    
    try:
        final_response = client.chat.completions.create(
            model="gemma3:27b",
            messages=[{"role": "user", "content": final_prompt}]
        )
        final_text = final_response.choices[0].message.content
        return jsonify({"status": "win", "analysis": final_text})
    except:
        return jsonify({"status": "win", "analysis": "[ SYSTEM ERROR ]: Nepodařilo se vygenerovat konспект."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
