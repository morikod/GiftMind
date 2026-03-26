import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import httpx

app = Flask(__name__, static_folder='static', template_folder='templates')

# Klient pro AI server
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
    
    # Instrukce pro AI - stručnost a kontrola voleb
    instructions = (
        "Jsi vypravěč textové hry. Odpovídej KRÁTCE (max 2-3 věty).\n"
        "1. Pokud is_start=True, vytvoř úvod ze 3 slov, malý ASCII art a volby A, B, C.\n"
        "2. Pokud is_start=False, reaguj pouze na volby A, B, C. Pokud uživatel napíše něco jiného, "
        "vypiš pouze: 'Prosím, zvolte A, B nebo C.'\n"
        "3. ASCII art dělej malý (max 5 řádků). Odpovídej česky."
    )

    try:
        response = client.chat.completions.create(
            model="gemma3:27b",
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": f"{'START: ' if is_start else 'VOLBA: '}{user_prompt}"}
            ]
        )
        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"response": f"[CHYBA AI]: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
