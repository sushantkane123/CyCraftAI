"""Pydantic Schemas for AI Security Copilot"""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    stream: bool = Field(False, description="Enable streaming SSE response")


class ChatResponse(BaseModel):
    reply: str
    confidence: str = "98.9%"
    source_models: list[str] = ["BradlyAI Multi-Model Cyber Mesh", "FastAPI Core"]
