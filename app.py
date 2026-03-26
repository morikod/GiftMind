import os, httpx, sqlite3
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv() # Načte .env lokálně

app = Flask(__name__)

# Databáze - vytvoření tabulky pro historii
def init_db():
    conn = sqlite3.connect('game.db')
    conn.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, role TEXT, content TEXT)')
    conn.commit()
    conn.close()

init_db()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL"),
    http_client=httpx.Client(verify=False)
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    user_input = request.json.get('input', '')
    
    # Uložit vstup do DB
    conn = sqlite3.connect('game.db')
    conn.execute('INSERT INTO history (role, content) VALUES (?, ?)', ('user', user_input))
    
    # Načíst historii pro AI
    cursor = conn.execute('SELECT role, content FROM history ORDER BY id DESC LIMIT 5')
    history = [{"role": r, "content": c} for r, c in cursor.fetchall()][::-1]

    instructions = "Jsi vypravěč textové hry. Piš příběh, ASCII art a volby A,B,C."

    try:
        response = client.chat.completions.create(
            model="gemma3:27b",
            messages=[{"role": "system", "content": instructions}] + history
        )
        answer = response.choices[0].message.content
        conn.execute('INSERT INTO history (role, content) VALUES (?, ?)', ('assistant', answer))
        conn.commit()
        return jsonify({"response": answer})
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))