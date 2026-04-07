import os
from flask import Flask, render_template, request, jsonify
import httpx
from openai import OpenAI

app = Flask(__name__)

# Инициализация OpenAI клиента с твоими переменными окружения
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1"),
    http_client=httpx.Client(verify=False) # Отключаем SSL проверку для локальных сетей
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    mode = data.get("mode", "quick")
    profile_data = data.get("profile", {})

    # Системный промпт зависит от режима
    system_prompt = (
        "Ты профессиональный AI-ассистент по подбору подарков. "
        "Общайся вежливо, креативно и используй эмодзи. "
    )

    if mode == "quick":
        system_prompt += (
            "Режим: Быстрый подбор. Задай 1-2 уточняющих вопроса (бюджет, повод), "
            "а затем предложи 3 крутые, небанальные идеи подарка. Опиши каждую идею с ценой и почему она подойдет."
        )
    else:
        system_prompt += (
            f"Режим: Полный профиль. Данные получателя: Имя: {profile_data.get('name')}, "
            f"Отношение: {profile_data.get('relation')}, Интересы: {profile_data.get('interests')}. "
            "Используй эти данные для супер-персонализированной подборки из 3-5 подарков."
        )

    # Формируем историю для AI
    ai_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        ai_messages.append({"role": msg["role"], "content": msg["content"]})

    try:
        response = client.chat.completions.create(
            model="gemma3:27b",
            messages=ai_messages,
            temperature=0.7
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"❌ Ошибка соединения с нейросетью: {str(e)}"}), 500

if __name__ == "__main__":
    # Сервер требует использования порта из переменной окружения
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
