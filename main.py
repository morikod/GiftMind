import os
from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import httpx
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL"),
    http_client=httpx.Client(verify=False)
)

# Временное хранилище (для MVP). В идеале использовать SQLAlchemy с БД из compose
profiles = {}

class Profile(BaseModel):
    id: str
    name: str
    tags: List[str]
    history: List[str] = []

@app.post("/generate-analogies")
async def generate_analogies(tag: str = Body(..., embed=True)):
    """Механика: Minecraft -> Kreativita, Stavebnice, Architektura"""
    prompt = f"Uživatel přidal zájem: '{tag}'. Navrhni 3 související abstraktní kategorie nebo koníčky, které by tuto osobu mohly zajímat. Odpovídej pouze česky, oddělené čárkou."
    try:
        response = client.chat.completions.create(
            model="gemma3:27b",
            messages=[{"role": "user", "content": prompt}]
        )
        analogies = response.choices[0].message.content.split(",")
        return {"analogies": [a.strip() for a in analogies]}
    except:
        return {"analogies": []}

@app.post("/chat")
async def chat(message: str, profile_id: Optional[str] = None):
    profile_info = ""
    if profile_id in profiles:
        p = profiles[profile_id]
        profile_info = f"Informace o příjemci ({p['name']}): Zájmy: {', '.join(p['tags'])}. Historie úspěšných dárků: {', '.join(p['history'])}."

    system_prompt = (
        "Jsi expert na dárky 'GiftAI'. Mluv česky. Tvým úkolem je radit kreativně. "
        f"{profile_info} "
        "Pokud uživatel napíše, že se dárek líbil, ulož si to do paměti a pogratuluj."
    )

    response = client.chat.completions.create(
        model="gemma3:27b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
    )
    return {"reply": response.choices[0].message.content}

@app.post("/save-profile")
async def save_profile(profile: Profile):
    profiles[profile.id] = profile.dict()
    return {"status": "success"}

@app.get("/profiles")
async def get_profiles():
    return list(profiles.values())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
