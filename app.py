import os
import json
import uuid
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)

API_KEY = os.environ.get("OPENAI_API_KEY", "")
BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1")
MODEL = "gemma3:27b"
DATA_FILE = "/tmp/giftmind_data.json"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

SYSTEM_PROMPT = """Jsi GiftMind, přátelský AI asistent pro výběr dárků.
Pomáháš najít ideální dárek tím, že kladeš chytré otázky.

Pravidla:
- Komunikuj česky, přátelsky a s lehkým humorem
- Pokládej vždy jen jednu otázku najednou
- Vyhýbej se banálním dárkům (ponožky, generické sady, nudné věci)
- Zohledni zájmy, věk, příležitost a rozpočet
- Jakmile máš dostatek informací, navrhni přesně 3 konkrétní dárky
- Každý dárek formátuj takto:

🎁 **Název dárku**
📝 Proč se hodí: [vysvětlení]
💰 Cena: [rozsah v Kč]
🛒 Kde koupit: [konkrétní obchody / weby]

- Po navržení dárků se zeptej: "Který z návrhů se ti líbí nejvíc? Nebo chceš něco upřesnit?"
- Pokud máš k dispozici profil příjemce, využij ta data co nejvíc"""


def get_user_id():
    """Anonymní ID uživatele z IP adresy (hash, nikdy se neukládá samotná IP)."""
    ip = request.headers.get('X-Forwarded-For', request.remote_addr or '0.0.0.0')
    ip = ip.split(',')[0].strip()
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"profiles": [], "gifts": []}


def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    body = request.get_json()
    messages = body.get("messages", [])
    profile = body.get("profile", None)

    system = SYSTEM_PROMPT
    if profile:
        system += f"\n\nProfil příjemce dárku:\n"
        system += f"Jméno: {profile.get('name', '—')}\n"
        system += f"Věk: {profile.get('age', '—')}\n"
        system += f"Vztah: {profile.get('relation', '—')}\n"
        system += f"Zájmy: {profile.get('interests', '—')}\n"
        system += f"Poznámky: {profile.get('notes', '—')}"

    api_messages = [{"role": "system", "content": system}] + messages

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=api_messages,
            max_tokens=1000,
            temperature=0.8,
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Chyba připojení k AI: {str(e)}"}), 500


@app.route("/api/profile", methods=["POST"])
def save_profile():
    uid = get_user_id()
    data = load_data()
    profile = request.get_json()
    profile["id"] = str(uuid.uuid4())
    profile["owner"] = uid
    profile["created_at"] = datetime.now().isoformat()
    data["profiles"].append(profile)
    save_data(data)
    return jsonify({"success": True, "profile": profile})


@app.route("/api/profiles", methods=["GET"])
def get_profiles():
    uid = get_user_id()
    data = load_data()
    my = [p for p in data["profiles"] if p.get("owner") == uid]
    return jsonify(my)


@app.route("/api/profile/<profile_id>", methods=["DELETE"])
def delete_profile(profile_id):
    uid = get_user_id()
    data = load_data()
    before = len(data["profiles"])
    data["profiles"] = [
        p for p in data["profiles"]
        if not (p["id"] == profile_id and p.get("owner") == uid)
    ]
    # smaž i dárky tohoto profilu patřící tomuto uživateli
    data["gifts"] = [
        g for g in data["gifts"]
        if not (g.get("profile_id") == profile_id and g.get("owner") == uid)
    ]
    save_data(data)
    deleted = before > len(data["profiles"])
    return jsonify({"success": deleted})


@app.route("/api/gift", methods=["POST"])
def save_gift():
    uid = get_user_id()
    data = load_data()
    gift = request.get_json()
    gift["id"] = str(uuid.uuid4())
    gift["owner"] = uid
    gift["created_at"] = datetime.now().isoformat()
    data["gifts"].append(gift)
    save_data(data)
    return jsonify({"success": True, "gift": gift})


@app.route("/api/gifts", methods=["GET"])
def get_gifts():
    uid = get_user_id()
    data = load_data()
    profile_id = request.args.get("profile_id")
    gifts = [g for g in data["gifts"] if g.get("owner") == uid]
    if profile_id:
        gifts = [g for g in gifts if g.get("profile_id") == profile_id]
    return jsonify(gifts)


@app.route("/api/gift/<gift_id>", methods=["DELETE"])
def delete_gift(gift_id):
    uid = get_user_id()
    data = load_data()
    data["gifts"] = [
        g for g in data["gifts"]
        if not (g["id"] == gift_id and g.get("owner") == uid)
    ]
    save_data(data)
    return jsonify({"success": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
