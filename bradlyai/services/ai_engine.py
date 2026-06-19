"""
BradlyAI Multi-Model AI Engine
Real AI-powered anomaly analysis, root-cause storyline generation,
and automated threat classification using LLM backends.
"""
import datetime
import random
import logging
from bradlyai.services.llm_client import llm_client

logger = logging.getLogger("bradlyai.ai_engine")


class AIEngine:
    """
    Core AI engine for autonomous alert analysis, storyline generation,
    and simulated anomaly creation for the live simulation worker.
    """

    # ── Dynamic Anomaly Generator (used by LiveSimulationWorker) ───────

    def analyze_anomaly(self, endpoint: str, ip: str, raw_behavior: str) -> dict:
        """Generate a realistic security alert with a full storyline."""
        now = datetime.datetime.now(datetime.timezone.utc)
        ts = now.strftime("%H:%M:%S")

        severities = ["CRITICAL", "HIGH", "HIGH", "MEDIUM", "MEDIUM", "LOW"]
        severity = random.choice(severities)

        statuses = ["Auto-Contained", "Auto-Contained", "Investigating", "Resolved"]
        status = random.choice(statuses)

        confidence = random.choice(["98%", "95%", "92%", "89%", "85%"])

        mitre_map = {
            "Reflective DLL Kernel Injection": "T1055 - Process Injection",
            "Anomalous Lateral SMB Enumeration": "T1210 - Exploitation of Remote Services",
            "Encrypted DNS Tunnel Establishment": "T1048 - Exfiltration Over Alternative Protocol",
            "Anomalous AdministratorAccess Attachment": "T1078 - Valid Accounts",
            "15 Failed Okta Push Authentications": "T1110 - Brute Force",
            "Unexpected Scheduled Task Registration": "T1053 - Scheduled Task/Job",
            "Privileged Container Shell Escape Attempt": "T1611 - Escape to Host",
            "Reflective DLL Memory Injection & Credential Harvesting": "T1055 - Process Injection",
            "Unauthorized Lateral Movement via SMB Exploitation": "T1210 - Exploitation of Remote Services",
            "Exfiltration Attempt to Known Tor Exit Node": "T1048 - Exfiltration Over Alternative Protocol",
        }
        mitre = mitre_map.get(raw_behavior, "T1203 - Exploitation for Client Execution")

        sec = int(now.strftime("%S"))
        storyline = [
            {"time": f"{now.strftime('%H:%M')}:{max(0, sec-10):02d}",
             "event": f"Anomalous activity detected on {endpoint} from source IP {ip}"},
            {"time": f"{now.strftime('%H:%M')}:{max(0, sec-6):02d}",
             "event": f"Behavioral ML model flagged {raw_behavior.lower()}"},
            {"time": f"{now.strftime('%H:%M')}:{max(0, sec-3):02d}",
             "event": "BradlyAI Multi-Model AI correlated TTPs with known adversary profiles"},
            {"time": ts,
             "event": "BradlyAIR autonomous engine executed containment: process killed, NIC isolated"},
        ]

        alert_id = f"ALT-{random.randint(9000, 9999)}"

        return {
            "id": alert_id,
            "severity": severity,
            "title": raw_behavior,
            "endpoint": endpoint,
            "ip": ip,
            "timestamp": "Just now",
            "mitre": mitre,
            "status": status,
            "ai_confidence": confidence,
            "storyline": storyline,
        }

    # ── LLM-Powered Alert Analysis ─────────────────────────────────────

    async def analyze_alert(self, alert_id: str, title: str, mitre: str, endpoint: str) -> list[str]:
        """Use an LLM to generate a professional 4-step forensic root-cause storyline."""
        system_prompt = (
            "You are an elite Cyber Security Forensic Expert. "
            "Analyze the following alert and provide a professional 4-step root cause storyline. "
            "Each step should be a concise security event (e.g., '14:02:01 - Initial Access via...'). "
            "Focus on TTPs (Tactics, Techniques, and Procedures). "
            "Format: Return ONLY the 4 steps, one per line, no introduction."
        )

        prompt = (
            f"Alert ID: {alert_id}\n"
            f"Title: {title}\n"
            f"MITRE: {mitre}\n"
            f"Endpoint: {endpoint}\n\n"
            f"Generate the 4-step forensic storyline:"
        )

        analysis = await llm_client.generate_response(prompt, system_prompt)
        return analysis.strip().split("\n")


ai_engine = AIEngine()
