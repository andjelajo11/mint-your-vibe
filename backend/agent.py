"""
The agent chain. Three sequential Mistral calls, each one feeding into the next.
This is what makes it an "agent" rather than a single prompt -> output call:
each step makes a decision that shapes what the next step does.
"""

import json
import os
from mistralai import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
MODEL = "mistral-small-latest"  # cheap + fast, plenty for this


def _call_json(system_prompt: str, user_prompt: str) -> dict:
    """Helper: call Mistral and force a JSON object back."""
    response = client.chat.complete(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
    )
    return json.loads(response.choices[0].message.content)


# ---------- STEP 1: analyze the prompt ----------

STEP1_SYSTEM = """You are a mood and theme analyzer for a generative art system.
Given a short user prompt describing a "vibe", extract structured data about it.

Respond ONLY with a JSON object matching this exact schema:
{
  "mood": "<one or two words, e.g. 'chaotic', 'serene', 'melancholic'>",
  "theme": "<one short phrase, e.g. 'deep ocean', 'cyberpunk night'>",
  "energy_level": <integer 1-10, 1 = very calm, 10 = very intense>,
  "keywords": ["<3-5 evocative single words derived from the prompt>"]
}
No prose, no markdown, just the JSON object."""


def analyze_prompt(user_input: str) -> dict:
    return _call_json(STEP1_SYSTEM, f"Prompt: {user_input}")


# ---------- STEP 2: decide traits ----------

STEP2_SYSTEM = """You are the trait engine for an AI-generated NFT collection.
You will be given the mood/theme analysis of a prompt. Based on it, decide the
NFT's traits. Rarer traits should be assigned more sparingly and deliberately -
treat "legendary" as something you only choose when the input is genuinely
unusual or extreme (energy_level 9-10, or a very distinctive theme).

Respond ONLY with a JSON object matching this exact schema:
{
  "rarity": "<one of: common, uncommon, rare, epic, legendary>",
  "palette": ["<3 hex color codes that fit the mood, e.g. '#1a1a2e'>"],
  "traits": {
    "Aura": "<short descriptive value>",
    "Pattern": "<one of: waves, shards, orbits, static, bloom>",
    "Element": "<one of: fire, water, air, earth, void>",
    "Density": "<one of: sparse, balanced, dense>"
  }
}
No prose, no markdown, just the JSON object."""


def decide_traits(analysis: dict, market_flavor: str | None = None) -> dict:
    context = f"Analysis: {json.dumps(analysis)}"
    if market_flavor:
        context += f"\nCurrent market mood (use lightly for flavor, don't overweight it): {market_flavor}"
    return _call_json(STEP2_SYSTEM, context)


# ---------- STEP 3: write the lore ----------

STEP3_SYSTEM = """You write short, evocative flavor text for NFT cards, in the
voice of the card's own "personality" as implied by its traits. Keep it to
2-3 sentences. No hashtags, no emoji, no markdown formatting.

Respond ONLY with a JSON object matching this exact schema:
{
  "lore": "<2-3 sentence flavor text>",
  "name": "<a short evocative name for this piece, 2-4 words>"
}"""


def write_lore(analysis: dict, traits: dict) -> dict:
    context = f"Mood/theme: {json.dumps(analysis)}\nTraits: {json.dumps(traits)}"
    return _call_json(STEP3_SYSTEM, context)


# ---------- orchestration ----------

def run_agent(user_input: str, market_flavor: str | None = None) -> dict:
    """
    Runs the full three-step chain and returns everything, including the
    intermediate reasoning at each step (so the frontend can display it).
    """
    step1 = analyze_prompt(user_input)
    step2 = decide_traits(step1, market_flavor)
    step3 = write_lore(step1, step2)

    return {
        "steps": {
            "1_analysis": step1,
            "2_traits": step2,
            "3_lore": step3,
        },
        "final": {
            "name": step3["name"],
            "mood": step1["mood"],
            "theme": step1["theme"],
            "energy_level": step1["energy_level"],
            "rarity": step2["rarity"],
            "palette": step2["palette"],
            "traits": step2["traits"],
            "lore": step3["lore"],
        },
    }
