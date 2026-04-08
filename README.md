🧠 Labirint AI

Interaktivní AI generátor a řešič labyrintů s moderním webovým rozhraním

🏷️ Běhající štítky (Badges)








✨ Funkce
🧩 Generování labyrintů – rychle a interaktivně
🤖 Automatické řešení AI – Gemma3 model zvládá i komplexní labyrinty
🌐 Webové rozhraní – pohodlné pro uživatele i na mobilu
⚡ Napojení na vlastní API – plně kompatibilní s OpenAI/Gemma API
🔌 Docker ready – snadné nasazení v kontejnerech
🚀 Živá ukázka (Live Demo)

🌐 Spusť Labirint AI online

🛠️ Použité technologie
Python 3.12 – hlavní jazyk aplikace
Flask – webový server a routování
OpenAI SDK – integrace s LLM API
httpx 0.27.0 – pro stabilní HTTP klient
Docker – rychlé nasazení
⚙️ Instalace
1️⃣ Klonování repozitáře
git clone https://github.com/morikod/Labirint-AI.git
cd Labirint-AI
2️⃣ Instalace závislostí
pip install -r requirements.txt
3️⃣ Nastavení proměnných prostředí
export OPENAI_API_KEY=tvuj_klic
export OPENAI_BASE_URL=https://kurim.ithope.eu/v1
4️⃣ Spuštění aplikace lokálně
python app.py
🐳 Docker

Snadné spuštění přes Docker:

docker build -t labirint-ai .
docker run -p 5000:5000 labirint-ai
🧠 Ukázka použití API
from openai import OpenAI

client = OpenAI(
    api_key="tvuj_klic",
    base_url="https://kurim.ithope.eu/v1"
)

response = client.chat.completions.create(
    model="gemma3:27b",
    messages=[{"role": "user", "content": "Vyřeš tento labyrint"}]
)

print(response.choices[0].message.content)
📁 Struktura projektu
Labirint-AI/
├── app.py               # hlavní aplikace
├── requirements.txt     # závislosti
├── templates/           # HTML šablony
├── static/              # CSS, JS, obrázky
└── README.md            # tento soubor
📸 Screenshots / Demo




Tip: nahraj GIF se záznamem generování a řešení labyrintu pro profesionálnější vzhled.

⚠️ Známé problémy
httpx >= 0.28 způsobuje chybu proxies
✅ Řešení: použít httpx==0.27.0
📜 Licence

MIT © Denys Voloshyn

👨‍💻 Autor

Denys Voloshyn – Portfolio / Web

⭐ Inspirace

Projekt inspirován moderními AI nástroji a RAG systémy (ChromaDB Plugin
)
