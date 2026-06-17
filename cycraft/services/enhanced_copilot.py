"""
CyCraft AI - Enhanced Real-World Copilot (Phase 1)
Analyzes actual ingested logs instead of hardcoded responses.
"""
import requests
import asyncio
from typing import AsyncGenerator
from cycraft.config import settings
from .log_ingestion import log_ingestion

class RealWorldCyberCopilot:
    def __init__(self):
        self.system_prompt = "You are an elite CyCraft Cyber-AI Security Analyst. Analyze the REAL security logs and alerts ingested by the user. Be precise and actionable."

    def _get_real_context(self) -> str:
        alerts = log_ingestion.get_alerts(5)
        events = log_ingestion.get_events(8)
        ctx = "=== REAL DATA IN SYSTEM ===\n\n"
        if alerts:
            ctx += "DETECTED ALERTS:\n" + "\n".join([f"- [{a['severity']}] {a['title']} on {a['endpoint']} (Rule: {a['rule_id']})" for a in alerts]) + "\n\n"
        if events:
            ctx += "RECENT EVENTS:\n" + "\n".join([f"- {e['source']}: {e['message'][:120]}" for e in events]) + "\n"
        if not alerts and not events:
            ctx += "No real logs ingested yet.\n"
        return ctx

    def get_reply(self, query: str) -> str:
        context = self._get_real_context()
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.startswith("sk-"):
            try:
                res = requests.post("https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"},
                    json={"model": settings.DEFAULT_AI_MODEL, "messages": [
                        {"role": "system", "content": self.system_prompt + "\n" + context},
                        {"role": "user", "content": query}
                    ], "max_tokens": 650}, timeout=15)
                if res.status_code == 200:
                    return res.json()["choices"][0]["message"]["content"]
            except Exception as e: print(f"OpenAI error: {e}")

        q = query.lower()
        alerts = log_ingestion.get_alerts(5)
        if ("summary" in q or "what happened" in q) and alerts:
            return "Real alerts from your logs:\n" + "\n".join([f"• {a['title']} on {a['endpoint']} (Rule {a['rule_id']})" for a in alerts])
        if "yara" in q and alerts:
            a = alerts[0]
            return f'rule CyCraft_{a["rule_id"]} {{ strings: $s = /powershell|VirtualAllocEx/i condition: $s }}'
        if not alerts:
            return "No real data ingested. Use /ingest/logs/text or upload a file."
        return f"Analyzed your real data:\n{context}\nQuery: {query}"

    async def get_reply_stream(self, query: str):
        reply = self.get_reply(query)
        for word in reply.split(" "):
            await asyncio.sleep(0.01)
            yield word + " "

real_copilot = RealWorldCyberCopilot()
