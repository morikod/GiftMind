import os
import psycopg2
import redis
import json
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import httpx

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL"),
    http_client=httpx.Client(verify=False)
)

cache = redis.Redis(host=os.environ.get("REDIS_HOST", "cache"), port=6379)

def init_db():
    try:
        conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS profiles (id SERIAL PRIMARY KEY, name TEXT, tags TEXT, description TEXT, history TEXT);')
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
def generate():
    data = request.json
    tags = data.get("tags", [])
    description = data.get("description", "")
    budget = data.get("budget", "Nezadáno")
    occasion = data.get("occasion", "Nespecifikováno")
    
    
    system_prompt = (
        "Jsi expert na výběr dárků. Tvé návrhy musí být PRAKTICKÉ, REALISTICKÉ a REÁLNĚ KOUPITELNÉ. "
        "ZÁKAZ navrhovat dárky typu 'vyrob si sám', 'namaluj obraz', 'vytvoř puzzle'. "
        "Pokud uživatel hraje hry (např. Dota 2, CS:GO), navrhni in-game měnu, skiny, Steam dárkové karty nebo herní hardware. "
        "Pokud má rád anime, navrhni konkrétní figurky (Funko Pop, Nendoroid), mangu, nebo předplatné Crunchyroll. "
        "Musíš respektovat zadaný ROZPOČET. "
        "Odpovídej v češtině. Vrať striktně JSON: {'gifts': [{'title': 'Název', 'reason': 'Proč je to super', 'price': 'Odhad ceny'}]}"
    )
    
    user_prompt = f"Příležitost: {occasion}. Rozpočet: {budget}. Tagy: {', '.join(tags)}. Popis: {description}. Navrhni 3 reálné dárky ke koupi."

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
