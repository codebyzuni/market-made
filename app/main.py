import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.schemas import GenerateRequest, GenerateResponse
from app.generator import generate_content

app = FastAPI(
    title="MarketMate API",
    description="AI Marketing Assistant for small businesses and startups.",
    version="1.0.0",
)

# Allow the frontend to call the API. Restrict via ALLOWED_ORIGINS env var in production.
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    try:
        result = generate_content(req)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}")


# Serve the frontend (static/index.html at "/") — must be mounted last
app.mount("/", StaticFiles(directory="static", html=True), name="static")
