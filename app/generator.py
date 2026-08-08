"""
Content generation engine for MarketMate.

Primary path: Groq API (free tier) using a fast open-weight LLM
(Llama 3.3 70B by default) for real generative text.

Fallback path: if no GROQ_API_KEY is configured, or the API call fails
for any reason (network issue, rate limit, bad key), MarketMate falls
back to a deterministic template engine so the product ALWAYS returns
a usable result during a live demo.
"""

import os
import re
import json
import requests
from typing import List
from dotenv import load_dotenv

load_dotenv()  # reads .env into the process environment — without this, GROQ_API_KEY is never seen

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL_ID = os.getenv("GROQ_MODEL_ID", "llama-3.3-70b-versatile").strip()
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_TIMEOUT = float(os.getenv("GROQ_TIMEOUT_SECONDS", "20"))

# Three distinct creative angles -> gives the "3 versions" the UI expects
ANGLES = [
    {"label": "Bold", "key": "bold", "instruction": "Bold, confident, energetic voice."},
    {"label": "Warm", "key": "warm", "instruction": "Warm, honest, relatable voice."},
    {"label": "Punchy", "key": "punchy", "instruction": "Short, punchy, scroll-stopping voice."},
]

GOAL_CTA = {
    "Increase Sales": "Shop Now →",
    "Boost Engagement": "Tell Us Below →",
    "Build Awareness": "Learn More →",
}

PLATFORM_WORD_RANGE = {
    "Instagram": (30, 60),
    "Facebook": (45, 80),
    "LinkedIn": (55, 90),
    "Email Marketing": (80, 120),
}


def _clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = text.strip('"').strip()
    return text


def _hashtags(product: str, audience: str, goal: str) -> List[str]:
    def tag(s: str) -> str:
        s = re.sub(r"[^a-zA-Z0-9\s]", "", s)
        return "#" + "".join(w.capitalize() for w in s.split())

    tags = [tag(product or "Brand"), tag(audience), tag(goal)]
    return [t for t in tags if t and t != "#"]


def _cta(goal: str) -> str:
    return GOAL_CTA.get(goal, "Learn More →")


def _build_prompt(req) -> str:
    word_min, word_max = PLATFORM_WORD_RANGE.get(req.platform, (45, 80))
    angle_lines = "\n".join(
        f'- "{a["key"]}": {a["instruction"]}' for a in ANGLES
    )
    return (
        f"You are a senior copywriter at a marketing agency, writing real {req.content_type} "
        f"copy for {req.platform} for an actual paying client. This is the finished text a "
        f"customer will read — not a description of a marketing strategy, not a summary of "
        f"the brief, and not a pitch about the campaign itself.\n\n"
        f"Client brief (for your eyes only — never repeat these words back or explain your approach):\n"
        f"- What they sell: {req.product}\n"
        f"- Who reads this: {req.audience}\n"
        f"- Voice: {req.tone}\n"
        f"- What success looks like: {req.goal}\n\n"
        f"Rules:\n"
        f"- Speak directly to the reader (\"you\"), never about them in third person.\n"
        f"- Never use the words \"marketing\", \"campaign\", \"brand\", \"overpromises\", or "
        f"\"content\" in the copy itself — those are planning words, not customer-facing words.\n"
        f"- Open with something specific and concrete (a feeling, a moment, a detail) — never "
        f"with \"Meet [product]\" or \"Introducing [product]\".\n"
        f"- Sound like a person who actually uses this, not a press release.\n"
        f"- Each version MUST be a full, complete piece of copy - {word_min} to {word_max} words. "
        f"A one-line headline or a single short sentence is NOT acceptable; write complete "
        f"sentences with real detail and flow, the way finished ad copy actually reads. "
        f"No hashtags, no CTA line - those are added separately.\n\n"
        f"Write THREE completely different versions, one per angle below — different opening "
        f"line, different structure, different specific detail each time, each meeting the "
        f"{word_min}-{word_max} word requirement:\n{angle_lines}\n\n"
        f'Respond ONLY with valid JSON, no other text: '
        f'{{"bold": "...", "warm": "...", "punchy": "..."}}'
    )


def _call_groq(prompt: str) -> dict:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not configured")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL_ID,
        "messages": [
            {"role": "system", "content": "You are a marketing copywriter. You always respond with strict JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.85,
        "top_p": 0.92,
        "max_tokens": 900,
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=GROQ_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    content = data["choices"][0]["message"]["content"]
    parsed = json.loads(content)

    result = {}
    for angle in ANGLES:
        body = parsed.get(angle["key"], "")
        if not body:
            raise RuntimeError(f"Missing '{angle['key']}' in Groq response")
        result[angle["label"]] = _clean(body)
    return result


def _template_fallback(req) -> dict:
    product = req.product.strip() or "this product"
    audience = req.audience.lower()

    templates = {
        "Bold": f"Meet {product} — made for {audience} who don't have time for marketing that overpromises.",
        "Warm": f"Real thought, real quality. {product} was designed with {audience} in mind — simple, honest, effective.",
        "Punchy": f"Skip the guesswork. {product} is the {req.tone.lower()} pick for {audience} ready for real results.",
    }
    return templates


def generate_content(req) -> dict:
    """Returns dict matching GenerateResponse shape."""
    source = "groq"
    try:
        prompt = _build_prompt(req)
        bodies = _call_groq(prompt)
    except Exception:
        source = "template-fallback"
        bodies = _template_fallback(req)

    versions = []
    for angle in ANGLES:
        versions.append(
            {
                "label": angle["label"],
                "body": bodies.get(angle["label"], ""),
                "hashtags": _hashtags(req.product, req.audience, req.goal),
                "cta": _cta(req.goal),
            }
        )

    return {"versions": versions, "source": source}
