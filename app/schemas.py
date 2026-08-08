from typing import List
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    product: str = Field(..., min_length=1, description="Product or service description")
    audience: str = Field(..., min_length=1, description="Target audience")
    platform: str = Field(..., min_length=1, description="Instagram, Facebook, LinkedIn, Email Marketing")
    content_type: str = Field(..., min_length=1, description="Caption, Ad Copy, Post Copy, Promotional Email, etc.")
    tone: str = Field(..., min_length=1, description="Professional, Friendly, Persuasive")
    goal: str = Field(..., min_length=1, description="Increase Sales, Boost Engagement, Build Awareness")


class ContentVersion(BaseModel):
    label: str
    body: str
    hashtags: List[str]
    cta: str


class GenerateResponse(BaseModel):
    versions: List[ContentVersion]
    source: str  # "groq" or "template-fallback"
