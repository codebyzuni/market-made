# MarketMate

### AI-Powered Marketing Content Assistant

Built as a Final Year AI & Data Science Project

## Demo

- **Live App:** https://marketmate-fu1n.onrender.com/
- **PPTX:** https://docs.google.com/presentation/d/1MBop3FidEI0N8VbXwDZgL20H3IkXDJWJ/edit?usp=drivesdk&ouid=111890711508229540647&rtpof=true&sd=true

---

# Project Description

Small businesses, startups, and independent entrepreneurs need marketing content constantly — social captions, ad copy, promotional emails — but most don't have a copywriter on staff and don't have time to write from scratch for every platform.

**MarketMate** is an AI-powered marketing content assistant that walks a user through a guided, step-by-step workflow — product, audience, platform, content type, tone, and goal — and generates **3 distinct, platform-optimized content variations**, each with contextually relevant hashtags and a call-to-action.

Instead of one generic block of text, MarketMate produces three genuinely different angles on the same brief — a bold version, a warm version, and a punchy version — so the user has real options to choose from rather than a single AI guess.

---

# The Problem

Creating marketing content is repetitive and time-consuming.

Writing copy from scratch for every platform is often:

- Time-consuming for non-writers
- Inconsistent in quality
- Hard to tailor per platform (what works on Instagram doesn't work in a promotional email)
- A blocker for small businesses without a marketing budget

Most people either pay for a copywriter or settle for generic, unoptimized text.

---

# Our Solution

MarketMate combines a guided input workflow with a generative language model to produce ready-to-post marketing copy in seconds.

For every request, the platform:

- Collects structured inputs through a 6-step wizard (no blank-page problem)
- Dynamically narrows content type options based on the selected platform
- Sends a structured prompt to a large language model
- Generates 3 distinct copy variations in a single request
- Attaches platform-appropriate hashtags and a goal-driven call-to-action
- Falls back to a built-in template engine if no AI key is configured or the AI call fails, so the app never breaks

---

# Key Capabilities

### Guided Step-by-Step Workflow

Six sequential steps — Product, Audience, Platform, Content Type, Tone, Goal — instead of one overwhelming form.

### Dynamic Content Type Selection

Content type options change based on the platform selected in the previous step, so irrelevant options are never shown (e.g. Email Marketing never shows "Instagram Caption").

### Three Distinct AI-Generated Variations

Every request returns three copy versions with different creative angles — Bold, Warm, and Punchy — not three near-identical rewrites.

### Automatic Hashtags & CTA

Hashtags are generated from the product, audience, and goal. The call-to-action is chosen based on the marketing goal (e.g. "Increase Sales" → "Shop Now →").

### Offline-Safe Fallback

If no API key is set, or the AI request fails for any reason, MarketMate automatically falls back to a template-based engine — the app always returns a usable result, even during a live demo with no internet.

---

# Solution Architecture

```text
User fills 6-step wizard
          │
          ▼
  Frontend (HTML/CSS/JS)
          │
          ▼
   POST /api/generate  (FastAPI)
          │
          ▼
  app/generator.py
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
Groq API    Template Fallback
(LLM call)   (if no key / call fails)
    │           │
    └─────┬─────┘
          ▼
 3 Content Variations
 + Hashtags + CTA
          │
          ▼
   Displayed to User
```

---

# AI Architecture

| Component | Purpose |
|-----------|---------|
| Groq API (`llama-3.3-70b-versatile`) | Generates the 3 marketing copy variations from a structured prompt |
| Prompt builder (`app/generator.py`) | Constructs a single prompt combining product, audience, platform, content type, tone, and goal |
| JSON-mode response parsing | Forces the model to return strictly structured output (one field per version) |
| Template fallback engine | Deterministic backup copy generator used when no API key is set or the AI call fails |
| Hashtag/CTA logic | Rule-based generation from product, audience, and goal — not AI-generated |

---

# Project Structure

```text
MarketMate/
├── app/
│   ├── main.py          # FastAPI app — API routes + serves the frontend
│   ├── generator.py     # Groq integration + offline template fallback engine
│   ├── schemas.py       # Request/response models
│   └── __init__.py
│
├── static/
│   └── index.html       # Frontend wizard UI (guided 6-step flow)
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── .env.example
└── README.md
```

---

# API

### `POST /api/generate`

Generates 3 marketing content variations based on the submitted brief.

**Example Request**

```json
{
  "product": "Organic face wash for sensitive skin",
  "audience": "Working Women",
  "platform": "Instagram",
  "content_type": "Caption",
  "tone": "Friendly",
  "goal": "Increase Sales"
}
```

**Example Response**

```json
{
  "versions": [
    {
      "label": "Bold",
      "body": "...",
      "hashtags": ["#OrganicFaceWash", "#WorkingWomen", "#IncreaseSales"],
      "cta": "Shop Now →"
    },
    {
      "label": "Warm",
      "body": "...",
      "hashtags": ["#OrganicFaceWash", "#WorkingWomen", "#IncreaseSales"],
      "cta": "Shop Now →"
    },
    {
      "label": "Punchy",
      "body": "...",
      "hashtags": ["#OrganicFaceWash", "#WorkingWomen", "#IncreaseSales"],
      "cta": "Shop Now →"
    }
  ],
  "source": "groq"
}
```

### `GET /api/health`

Returns `{"status": "ok"}` — used for container/platform healthchecks.

---

# Technology Stack

- Python
- FastAPI
- Uvicorn
- Groq API (`llama-3.3-70b-versatile`)
- HTML / CSS / vanilla JavaScript
- Docker
- Docker Compose

---

# Repository Contents

- FastAPI backend serving both the API and the frontend
- Guided 6-step wizard UI with dynamic, platform-aware content type selection
- Groq LLM integration for real generative AI output
- Deterministic offline fallback engine (no API key required to run)
- Docker configuration for one-command local runs and free-tier deployment
- Project documentation

---

# Setup Instructions

## Prerequisites

- Python 3.11+
- A free Groq account (optional — only needed for real AI-generated output)

## 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/MarketMate.git
cd MarketMate
```

## 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Configure Environment Variables

```bash
cp .env.example .env
```

Leave `GROQ_API_KEY` blank to run fully offline on the template fallback, or add a free key from https://console.groq.com/keys for real AI-generated output.

## 4. Run the Application

```bash
uvicorn app.main:app --reload --port 8000
```

Open:

```text
http://localhost:8000
```

## 5. Run with Docker (optional)

```bash
docker build -t marketmate .
docker run -p 8000:8000 --env-file .env marketmate
```

or

```bash
docker compose up --build
```

---

# Deployment

MarketMate can be deployed on:

- Render (recommended — free web service tier, auto-detects the Dockerfile)
- Railway
- Any platform that supports a Dockerfile or a Python/FastAPI app

---

# Why MarketMate?

- Removes the blank-page problem for non-writers
- Produces platform-specific content instead of one generic block of text
- Gives 3 genuinely different creative angles per request, not near-duplicate rewrites
- Works even without an API key, so a demo never breaks
- Simple, modular FastAPI codebase that's easy to explain in a project defense
