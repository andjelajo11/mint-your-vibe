# Mint Your Vibe 🎨🤖

An **AI-native full-stack application** that transforms a user's prompt into a unique NFT concept artefact through a multi-step **Mistral AI agent**, then renders a **deterministic generative artwork** using Python and Pillow.

Unlike diffusion-based image generation, the artwork is produced through rule-based rendering, making every output **reproducible, explainable, and derived from structured AI decisions**.

<p align="center">
  <img src="https://github.com/user-attachments/assets/706386fd-bbe9-4928-a66d-5b4f35764e4c" />

</p>
---

## 🚀 Live Demo

🎥 Video Walkthrough (2 min)
https://www.loom.com/share/c2869ad52d814ae0b293ad7604b8d066

**Live Application:** *(https://mint-your-vibe.vercel.app/)*


---

## Features

* 🤖 Multi-step AI agent powered by **Mistral**
* 📋 Structured JSON outputs for transparent reasoning
* 🎨 Deterministic generative art engine built with **Pillow**
* ⚡ FastAPI backend with REST API endpoints
* ⚛️ React frontend for prompt submission and visualization
* ☁️ Full-stack deployment using **Vercel** and **Render**
* 🔄 Reproducible outputs using prompt-derived deterministic seeds

---

## AI Workflow

```text
User Prompt
      │
      ▼
Analyze Prompt
      │
      ▼
Generate Traits
      │
      ▼
Create Lore
      │
      ▼
Deterministic Art Renderer
      │
      ▼
Generated NFT + Metadata
```

---

## Tech Stack

| Category         | Technologies    |
| ---------------- | --------------- |
| Frontend         | React           |
| Backend          | FastAPI, Python |
| AI               | Mistral API     |
| Image Generation | Pillow          |
| Deployment       | Vercel, Render  |

---

## Project Structure

```text
mint-your-vibe/
│
├── frontend/          # React application
├── backend/
│   ├── agent.py       # Multi-step AI workflow
│   ├── art_generator.py
│   ├── main.py
│   └── requirements.txt
└── README.md
```

---

## Running Locally

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

---

## API

### Generate Artwork

`POST /generate`

```json
{
  "prompt": "A chaotic storm over a neon city"
}
```

Returns:

* Generated artwork
* AI-generated traits
* Lore
* Step-by-step reasoning metadata

---

## Why This Project?

This project demonstrates several AI-native software engineering concepts:

* Building applications around LLM agents instead of traditional pipelines
* Producing structured AI outputs for downstream systems
* Separating AI reasoning from deterministic rendering
* Developing and deploying a complete full-stack AI application

---

## Future Improvements

* Wallet integration
* NFT minting on testnet
* Gallery persistence
* Authentication
* Streaming AI reasoning
* On-chain proof of generation
* More complex, layered NFT 

---

## License

MIT
