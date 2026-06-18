
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from bradlyai.services.llm_client import llm_client
from bradlyai.database import SessionLocal
from bradlyai.models.alert import AlertModel
import asyncio

router = APIRouter()

async def generate_ai_stream(user_query: str, context_data: str):
    system_prompt = (
        "You are the BradlyAI Cyber-AI Copilot, the brain of a Driverless SOC. "
        "You have access to real-time security alerts. Be precise, technical, and actionable. "
        "If the user asks about the network, refer to the provided context alerts. "
        "Always conclude with a suggested remediation step."
    )
    
    full_prompt = f"Context Alerts:\n{context_data}\n\nUser Question: {user_query}"
    
    # For the sake of the streaming demo, we simulate the chunking 
    # because the LLM client returns the full string (unless we use streaming API).
    response_text = await llm_client.generate_response(full_prompt, system_prompt)
    
    for word in response_text.split(" "):
        yield word + " "
        await asyncio.sleep(0.05)

@router.get("/chat")
async def chat(query: str):
    # 1. Fetch current alerts from DB to provide context to the AI
    db = SessionLocal()
    alerts = db.query(AlertModel).all()
    context = "\n".join([f"ID: {a.id}, Title: {a.title}, Status: {a.status}" for a in alerts])
    db.close()
    
    return StreamingResponse(generate_ai_stream(query, context), media_type="text/plain")
