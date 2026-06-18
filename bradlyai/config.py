
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "BradlyAI - Driverless SOC"
    APP_VERSION: str = "2.0.0-PRO"
    DATABASE_URL: str = "sqlite:///./bradlyai_soc.db"
    
    # AI Configuration
    # Providers: 'groq' (Open Source Llama-3) or 'openai' (GPT-4)
    LLM_PROVIDER: str = "groq" 
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    
    # Simulation Settings
    LIVE_SIMULATION_WORKER_ACTIVE: bool = True
    SIMULATION_INTERVAL_SECONDS: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
