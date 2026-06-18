
import os
from bradlyai.config import settings

class LLMClient:
    """
    Unified LLM Client to handle multiple providers (Groq, OpenAI).
    Supports open-source Llama-3 via Groq for high-speed free tier.
    """
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.api_key = settings.GROQ_API_KEY if self.provider == "groq" else settings.OPENAI_API_KEY

    async def generate_response(self, prompt: str, system_prompt: str = "You are a professional SOC Analyst."):
        if not self.api_key:
            return "⚠️ API Key missing. Please add GROQ_API_KEY or OPENAI_API_KEY to your .env file or config.py"

        try:
            if self.provider == "groq":
                import requests
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "llama3-70b-8192",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2
                }
                response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                return response.json()['choices'][0]['message']['content']

            elif self.provider == "openai":
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=self.api_key)
                response = await client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2
                )
                return response.choices[0].message.content
            
            else:
                return "Unsupported provider."
        except Exception as e:
            return f"❌ LLM Error: {str(e)}"

llm_client = LLMClient()
