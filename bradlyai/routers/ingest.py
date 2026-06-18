"""
BradlyAI - Real Log Ingestion Router (Phase 1)
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Dict, Any
import json
from ..services.log_ingestion import log_ingestion

router = APIRouter(prefix="/ingest", tags=["Real Log Ingestion"])

@router.post("/logs/text")
async def ingest_text_logs(logs: str = Form(...)):
    if not logs.strip():
        raise HTTPException(400, "No logs provided")
    return log_ingestion.ingest_text(logs)

@router.post("/logs/json")
async def ingest_json_logs(logs: List[Dict[str, Any]]):
    if not logs:
        raise HTTPException(400, "Empty log array")
    return log_ingestion.ingest_json(logs)

@router.post("/logs/upload")
async def upload_log_file(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8", errors="ignore")
    if file.filename and file.filename.endswith(".json"):
        try:
            data = json.loads(content)
            if isinstance(data, list):
                return log_ingestion.ingest_json(data)
            return log_ingestion.ingest_json([data])
        except:
            pass
    return log_ingestion.ingest_text(content)

@router.get("/events")
async def get_ingested_events(limit: int = 50):
    return {"count": len(log_ingestion.events), "events": log_ingestion.get_events(limit)}

@router.get("/alerts")
async def get_real_alerts(limit: int = 100):
    return {"count": len(log_ingestion.alerts), "alerts": log_ingestion.get_alerts(limit)}

@router.post("/clear")
async def clear_data():
    log_ingestion.clear()
    return {"status": "success", "message": "All data cleared"}
