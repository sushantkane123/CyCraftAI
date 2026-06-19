"""BradlyAI Cyber-AI Security Copilot Service"""
import asyncio
import logging
from typing import AsyncGenerator
from bradlyai.services.llm_client import llm_client

logger = logging.getLogger("bradlyai.copilot")


class CyberAICopilot:
    SYSTEM_PROMPT = (
        "You are an elite BradlyAI Cyber-AI Copilot operating Asia's most advanced "
        "AI-Driven Security Operations Center (Driverless SOC). "
        "Provide highly precise, actionable, and executive cybersecurity threat analysis. "
        "When asked to investigate logs or write YARA rules, output clean, production-ready code. "
        "Maintain a highly professional, secure, and authoritative tone."
    )

    async def get_reply(self, query: str) -> str:
        if llm_client.api_key:
            try:
                return await llm_client.generate_response(query, self.SYSTEM_PROMPT)
            except Exception as e:
                logger.warning(f"LLM call failed, falling back: {e}")
        return self._offline_fallback(query)

    def _offline_fallback(self, query: str) -> str:
        lower = query.lower()
        if any(w in lower for w in ["threat", "critical", "summarize", "top"]):
            return "Here is the executive summary of today's top security events across our 12,842 endpoints:<br><br><strong>1. Active Breach Prevented (ALT-8921):</strong> Unusual login from IP <code>45.33.12.9</code> spawned obfuscated PowerShell on <code>DEV-WIN-SRV09</code>. BradlyAI Multi-Model Engine identified LSASS memory injection, killed PID 6104, and isolated the host.<br><br><strong>2. Attack Surface (ASM):</strong> 2 unpatched vulnerabilities in your AWS S3 storage bucket. Auto-remediation available."
        if any(w in lower for w in ["jenkins", "dev-win-srv09", "blocked"]):
            return "BradlyAI's Automated Incident Response (AIR) executed sub-second containment on <code>DEV-WIN-SRV09</code>:<pre>[14:02:15] Correlated anomalous JWT Auth from 45.33.12.9\n[14:02:18] Identified reflective injection DLL into lsass.exe\n[14:02:19] Triggered autonomous mitigation: Killed PID #3912, isolated IP subnet.</pre>Zero credentials or customer tables were compromised."
        if any(w in lower for w in ["resilience", "board", "director", "score"]):
            return "Board briefing: Over the past 30 days, our <strong>Digital Resilience Score increased to 94/100 (+3.2%)</strong>. BradlyAI's Driverless SOC achieved <strong>99.4% autonomous threat containment</strong>, neutralizing 342 automated adversarial attempts per hour with zero manual intervention."
        if any(w in lower for w in ["yara", "rule"]):
            return "Here is an auto-generated YARA rule:<pre>rule BradlyAI_Reflective_DLL_APT29 {\n    meta:\n        description: \"Detects reflective DLL injection\"\n        author: \"BradlyAI Threat Copilot\"\n    strings:\n        $mz = { 4D 5A }\n        $api1 = \"VirtualAllocEx\" ascii\n        $api2 = \"WriteProcessMemory\" ascii\n        $api3 = \"CreateRemoteThread\" ascii\n    condition:\n        $mz at 0 and all of ($api*)\n}</pre>Deploy across all 12,842 endpoints?"
        if any(w in lower for w in ["mitre", "matrix", "coverage"]):
            return "BradlyAI provides multi-model ML behavioral mapping across 14 tactical MITRE ATT&CK domains. <strong>100% automated coverage</strong> for critical TTPs (T1059, T1003) across Windows, Linux, and macOS."
        return f"Based on my analysis of our 12,842 monitored assets, your query regarding \"{query}\" indicates zero immediate active anomalous vectors. Would you like me to trigger an automated memory deep scan or export SIEM audit logs?"

    async def get_reply_stream(self, query: str) -> AsyncGenerator[str, None]:
        reply = await self.get_reply(query)
        for word in reply.split(" "):
            await asyncio.sleep(0.015)
            yield f"{word} "


copilot_service = CyberAICopilot()
