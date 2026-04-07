import os
import json
import redis
import psycopg2
import httpx
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Připojení k AI (Gemma 3)
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL"),
    http_client=httpx.Client(verify=False)
)

# Připojení k Redis (Cache pro sezení)
cache = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=6379)

# Připojení k PostgreSQL (Databáze profilů)
def get_db_connection():
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    return conn

# Inicializace DB (vytvoření tabulek při startu)
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                id SERIAL PRIMARY KEY,
                name TEXT,
                tags TEXT,
                history TEXT
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Chyba DB: {e}")

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/generate", methods=["POST"])
def generate_gift():
    data = request.json
    tags = data.get("tags", [])
    description = data.get("description", "")
    
    # Prompt pro inovativní AI (Anti-klišé filtr)
    system_prompt = (
        "Jsi 'Gift Neural Architect' – expert na psychologii dárků a kreativní analytik. "
        "Tvým úkolem je navrhnout 3 naprosto unikátní dárky na základě tagů a popisu. "
        "PRAVIDLO 1: Ignoruj klišé (ponožky, hrnky, knihy, parfémy). "
        "PRAVIDLO 2: Hledej průniky zájmů (např. 'Technologie' + 'Vaření' = 'Molekulární kuchyně'). "
        "PRAVIDLO 3: Odpovídej v češtině, tónem inspirativního přítele. "
        "Vrať JSON formát: {'gifts': [{'title': '...', 'reason': '...', 'vibe': '...'}]}"
    )
    
    user_prompt = f"Osoba: {', '.join(tags)}. Další info: {description}. Navrhni něco, co nikdo nečeká."

    try:
        response = client.chat.completions.create(
            model="gemma3:27b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
