
from bradlyai.services.llm_client import llm_client

class AIEngine:
    """
    Real AI Engine that uses LLMs to analyze security alerts 
    and generate actual root-cause storylines.
    """
    async def analyze_alert(self, alert_id: str, title: str, mitre: str, endpoint: str):
        system_prompt = (
            "You are an elite Cyber Security Forensic Expert. "
            "Analyze the following alert and provide a professional 4-step root cause storyline. "
            "Each step should be a concise security event (e.g., '14:02:01 - Initial Access via...'). "
            "Focus on TTPs (Tactics, Techniques, and Procedures). "
            "Format: Return ONLY the 4 steps, one per line, no introduction."
        )
        
        prompt = f"Alert ID: {alert_id}\nTitle: {title}\nMITRE: {mitre}\nEndpoint: {endpoint}\n\nGenerate the 4-step forensic storyline:"
        
        analysis = await llm_client.generate_response(prompt, system_prompt)
        return analysis.strip().split('\n')

ai_engine = AIEngine()
