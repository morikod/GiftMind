import os
from flask import Flask, render_template, request, jsonify
import httpx
from openai import OpenAI

# --- Inicializace ---
app = Flask(__name__, static_folder='static', template_folder='templates')

# Klient pro AI server (používá proměnné prostředí z Dockeru/Compose)
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "your_key_here"),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1"),
    http_client=httpx.Client(verify=False)
)

# --- RAG databáze (Načítání z lokálního souboru) ---
def ziskat_lore():
    try:
        if os.path.exists("data/game_info.txt"):
            with open("data/game_info.txt", "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        print(f"RAG Error: {e}")
    return "Škola Cyber-Lincoln High, USA. Přísné zabezpečení známek."

# --- Pomocné AI funkce ---

def zavolat_ai(system_prompt, user_prompt):
    try:
        odpoved = client.chat.completions.create(
            model="gemma3:27b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return odpoved.choices[0].message.content
    except Exception as e:
        return f"[ SYSTEM ERROR ]: Komunikace s neuronovou sítí selhala. {str(e)}"

# --- HLAVNÍ ROUTY ---

@app.route("/")
def index():
    # Tato routa zobrazí tvůj Cyberpunk HTML soubor
    return render_template("index.html")

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json
    user_input = data.get("prompt", "").strip()
    is_start = data.get("is_start", False)
    lang = data.get("lang", "cs")
    
    lore = ziskat_lore()

    if is_start:
        # ÚVOD A PRVNÍ HACKERSKÁ OTÁZKA
        system_prompt = (
            f"Jsi školní bezpečnostní terminál. Jazyk: {lang}. "
            f"Kontext světa: {lore}. "
            "Hráč zadal 3 témata. Tvým úkolem je vytvořit úvod do hackování "
            "a položit PRVNÍ OTÁZKU (A, B, C) založenou na těchto tématech. "
            "Buď stručný a technický. Používej ASCII art (max 5 řádků)."
        )
        vysledek = zavolat_ai(system_prompt, f"Témata pro hack: {user_input}")
    else:
        # ANALÝZA ODPOVĚDI A DALŠÍ POSTUP
        system_prompt = (
            f"Jsi školní bezpečnostní terminál. Jazyk: {lang}. "
            "Vyhodnoť odpověď hráče na předchozí otázku. "
            "Pokud je správná, popiš postup v hackování databáze známek a dej DALŠÍ OTÁZKU (A, B, C). "
            "Pokud je špatná, vypiš varování o sledování IP adresy a dej opravnou otázku. "
            "Buď velmi stručný (max 3 věty + ASCII)."
        )
        vysledek = zavolat_ai(system_prompt, f"Odpověď hráče: {user_input}")

    return jsonify({"response": vysledek})

# --- DODATEČNÉ ENDPOINTY (Pro jistotu) ---

@app.route("/api/boss", methods=["GET"])
def boss():
    system_prompt = "Jsi finální firewall. Vytvoř jednu extrémně těžkou otázku (A, B, C) pro dokončení hacku."
    vysledek = zavolat_ai(system_prompt, "FINAL_BREAK_IN")
    return jsonify({"otazka": vysledek})

# --- Start serveru ---
if __name__ == "__main__":
    # Port se bere z environment proměnné (důležité pro hosting)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
