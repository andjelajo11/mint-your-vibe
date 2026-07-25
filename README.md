# Mint Your Vibe

An AI agent (Mistral) reads a mood/prompt, makes a chain of decisions about
an NFT's traits, and a deterministic generative-art renderer (Pillow, no
image-gen model) turns those decisions into an actual image.

## How the agent works (backend/agent.py)

Three sequential Mistral calls, each one informed by the previous:

1. **Analyze** — reads the raw prompt, extracts mood / theme / energy level
2. **Decide traits** — given the analysis, picks rarity, color palette, and
   named traits (this is the "agent" part — it's making judgment calls, not
   just formatting text)
3. **Write lore** — given the traits, writes flavor text in-character

Every step forces structured JSON output, so the frontend can show exactly
what the agent decided and why (`steps` in the `/generate` response).

## How the art renders (backend/art_generator.py)

No image AI. The trait JSON (palette, pattern type, density, rarity) drives
plain shape-drawing rules — gradients, waves, shards, orbits, particles,
bloom. The random seed is derived from a hash of the original prompt text,
so the same prompt always produces the exact same image. That determinism
is what lets you claim the art is "provably derived from this input" if you
want to lean into the verifiability angle later.

## Running it locally

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then paste your Mistral API key into .env
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`. Test it:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a chaotic storm over a neon city"}'

```

frontend instructions: 
```bash
cd backend 
npm install
cp .env.example .env #(Set up the environment file. This just tells the frontend where your backend is running — the default http://localhost:8000 is already correct if you're running the backend locally too.
npm run dev
```

You'll get back JSON with `image_base64`, `metadata` (traits/rarity/lore),
and `steps` (the agent's reasoning at each stage).

## Where to get a Mistral API key

Sign up at https://console.mistral.ai — there's a free tier, and
`mistral-small-latest` is inexpensive enough that a weekend of testing
plus demo traffic will cost cents, not dollars.

## Next steps (not built yet — this is your starting point)

- **Frontend** (React + Tailwind): input box → loading state that shows
  each agent step as it completes → animated card reveal → gallery page
  hitting `GET /gallery`
- **Deploy**: frontend on Vercel, backend on Render/Railway (both free tiers)
- **Optional stretch**: real testnet minting (Sepolia) using the
  `reasoning_hash` already returned by `/generate` as on-chain proof that
  a specific agent run produced a specific card

## Project structure

```
mint-your-vibe/
├── backend/
│   ├── main.py            FastAPI app, /generate and /gallery endpoints
│   ├── agent.py            the 3-step Mistral chain
│   ├── art_generator.py    trait JSON -> image, deterministic
│   ├── requirements.txt
│   └── .env.example
└── README.md
```
