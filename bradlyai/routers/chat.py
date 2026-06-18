"""
BradlyAI - Updated Chat Router (Phase 1)
Uses real-data copilot.
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from ..services.enhanced_copilot import real_copilot

router = APIRouter(prefix="/chat", tags=["AI Copilot"])

class ChatRequest(BaseModel):
    message: str
    stream: Optional[bool] = True

@router.post("")
async def ask_copilot(req: ChatRequest):
    if req.stream:
        return StreamingResponse(real_copilot.get_reply_stream(req.message), media_type="text/plain")
    else:
        return {"reply": real_copilot.get_reply(req.message)}

@router.get("/context")
async def get_context():
    from ..services.log_ingestion import log_ingestion
    return {
        "total_events": len(log_ingestion.events),
        "total_alerts": len(log_ingestion.alerts),
        "alerts": log_ingestion.get_alerts(5),
        "events": log_ingestion.get_events(5)
    }
