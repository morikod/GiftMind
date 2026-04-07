from flask import Flask, render_template, request, jsonify
import os
import httpx
from openai import OpenAI

app = Flask(__name__)

# 🔑 берём из переменных окружения
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL"),
    http_client=httpx.Client(verify=False)
)

profiles = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_profile', methods=['POST'])
def create_profile():
    data = request.json
    profiles[data['name']] = data
    return jsonify({"status": "ok"})

@app.route('/get_profiles')
def get_profiles():
    return jsonify(profiles)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    profile = data.get('profile')

    if not profile:
        return jsonify({"response": "Nejdřív vyber profil."})

    # 🧠 СИЛЬНЫЙ ПРОМПТ
    system_prompt = f"""
Jsi kreativní AI specialista na dárky.

Tvoje úkoly:
- Navrhnout ORIGINÁLNÍ a NEBANÁLNÍ dárek
- Vyhnout se věcem jako: kniha, puzzle, hrnek
- Myslet logicky a kreativně
- Můžeš navrhnout zážitek, DIY, personalizaci

Profil osoby:
Jméno: {profile.get('name')}
Zájmy: {profile.get('tags')}
Popis: {profile.get('desc')}
Rozpočet: {profile.get('budget')} Kč
Příležitost: {profile.get('reason')}

Odpověď:
- krátká
- konkrétní
- 2–4 návrhy
"""

    try:
        response = client.chat.completions.create(
            model="gemma3:27b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )

        ai_text = response.choices[0].message.content

    except Exception as e:
        ai_text = f"Chyba AI: {str(e)}"

    return jsonify({"response": ai_text})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
