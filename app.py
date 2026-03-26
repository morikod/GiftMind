import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import httpx

app = Flask(__name__, static_folder='static', template_folder='templates')

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1"),
    http_client=httpx.Client(verify=False)
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    user_prompt = data.get('prompt', '').strip().upper()
    is_start = data.get('is_start', False)
    lang = data.get('lang', 'cs') # Default čeština

    # Přísný systémový prompt
    instructions = (
        f"Jsi profesionální vypravěč textových RPG her. Odpovídej v jazyce: {lang}.\n"
        "PRAVIDLA:\n"
        "1. Pokud is_start=True, vytvoř ÚVODNÍ SCÉNU podle 3 slov uživatele.\n"
        "2. Pokud is_start=False, uživatel zvolil A, B nebo C. TY MUSÍŠ detailně popsat, co se stalo (3 věty), "
        "udržet logickou návaznost na předchozí děj, nakreslit ASCII art a dát nové volby A, B, C.\n"
        "3. NIKDY neměň téma hry (např. z matematiky na les).\n"
        "4. ASCII art musí odpovídat aktuální scéně."
    )

    try:
        response = client.chat.completions.create(
            model="gemma3:27b",
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": f"AKCE: {user_prompt}"}
            ]
        )
        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
