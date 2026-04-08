# 🎁 GiftMind — AI průvodce výběrem dárků

> Chytré doporučení dárků na základě profilu příjemce, jeho zájmů a vzpomínek.  
> Postaveno na lokálním LLM (Gemma 3 27B) bez závislosti na externích AI službách.

---

## ✨ Co umí

| Funkce | Popis |
|---|---|
| ⚡ **Rychlý výběr** | Popis situace → 3 konkrétní tipy na dárek během sekund |
| 👤 **Profily příjemců** | Uložení zájmů, vztahu, věku a poznámek pro opakované použití |
| 🔒 **Soukromí** | Každý uživatel vidí pouze svoje profily a historii (izolace podle IP) |
| 💬 **Konverzační AI** | Přirozený dialog, AI se ptá a upřesňuje |
| 📚 **Historie dárků** | Přehled všech darovaných věcí s hodnocením |
| 🗑️ **Mazání** | Možnost smazat profil nebo konkrétní dárek |
| 🌙 **Dark UI** | Moderní tmavý design s animacemi |

---

## 🚀 Spuštění (lokálně)

### Požadavky
- Python 3.12+
- Přístup k OpenAI-compatible API (nebo lokální Ollama)

### Instalace

```bashgit clone https://github.com/morikod/GiftMind.git
cd GiftMind
pip install -r requirements.txt

### Konfigurace

Vytvoř soubor `.env` (nikdy jej nepřidávej do Gitu!):

```envOPENAI_API_KEY=tvůj-klíč
OPENAI_BASE_URL=https://tvůj-server/v1
PORT=5000

### Spuštění

```bashpython app.py

Otevři prohlížeč na `http://localhost:5000`

---

## 🐳 Docker

```bashdocker build -t giftmind .
docker run -p 5000:5000 
-e OPENAI_API_KEY=tvůj-klíč 
-e OPENAI_BASE_URL=https://tvůj-server/v1 
giftmind

---

## ⚙️ Proměnné prostředí

| Proměnná | Popis | Výchozí |
|---|---|---|
| `OPENAI_API_KEY` | API klíč pro LLM | — (povinné) |
| `OPENAI_BASE_URL` | URL OpenAI-compatible API | `https://api.openai.com/v1` |
| `PORT` | Port aplikace | `5000` |

> ⚠️ **Nikdy nevkládej API klíč přímo do kódu ani do Gitu.**  
> Vždy používej proměnné prostředí nebo tajný trezor.

---

## 🏗️ ArchitekturaGiftMind/
├── app.py              # Flask backend + REST API
├── templates/
│   └── index.html      # Single-page aplikace
├── static/
│   ├── style.css       # Dark theme UI
│   └── script.js       # Frontend logika
├── requirements.txt
└── Dockerfile

### Soukromí uživatelů

Aplikace nepoužívá přihlášení ani cookies.  
Každý uživatel je identifikován **anonymním hashem IP adresy** (SHA-256, prvních 16 znaků).  
Samotná IP adresa se nikam neukládá.

---

## 🧠 AI model

Aplikace používá **Gemma 3 27B** přes OpenAI-compatible API.  
Lze snadno přepnout na jakýkoliv jiný model změnou proměnné prostředí.

---

## 📄 Licence

MIT — volně použitelné a upravitelné.
