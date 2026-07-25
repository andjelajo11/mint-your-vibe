import base64
import hashlib
import time
import uuid

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import run_agent
from art_generator import generate_image, image_to_bytes

app = FastAPI(title="Mint Your Vibe")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before actually shipping anywhere public
    allow_methods=["*"],
    allow_headers=["*"],
)

# in-memory gallery - swap for a real DB later, fine for a weekend demo
GALLERY: list[dict] = []


class GenerateRequest(BaseModel):
    prompt: str


@app.post("/generate")
def generate(req: GenerateRequest):
    if not req.prompt or len(req.prompt.strip()) < 3:
        raise HTTPException(400, "Give it a bit more to work with.")

    result = run_agent(req.prompt)
    final = result["final"]
    final["seed_source"] = req.prompt  # keeps art deterministic per prompt

    img = generate_image(final)
    img_bytes = image_to_bytes(img)
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    # this is the "verifiable" touch: hash the full reasoning trace so you
    # can later prove this exact output came from this exact agent run
    reasoning_hash = hashlib.sha256(
        str(result["steps"]).encode("utf-8")
    ).hexdigest()

    card = {
        "id": str(uuid.uuid4()),
        "prompt": req.prompt,
        "created_at": int(time.time()),
        "image_base64": img_b64,
        "reasoning_hash": reasoning_hash,
        "steps": result["steps"],       # for the "how I decided this" panel
        "metadata": final,               # name, rarity, traits, lore
    }

    GALLERY.insert(0, card)
    return card


@app.get("/gallery")
def gallery(limit: int = 20):
    return GALLERY[:limit]


@app.get("/health")
def health():
    return {"status": "ok"}
