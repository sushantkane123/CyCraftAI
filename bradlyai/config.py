"""
BradlyAI Configuration — Environment settings loaded via Pydantic Settings
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # ── Application Identity ──────────────────────────────────────────
    APP_NAME: str = "BradlyAI - Driverless SOC & Automated Incident Response"
    APP_VERSION: str = "2.1.0-PRO"
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── Database ───────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./bradlyai_soc.db"

    # ── AI / LLM Configuration ────────────────────────────────────────
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_AI_MODEL: str = "gpt-4-turbo-preview"

    # ── Autonomous SOC Settings ────────────────────────────────────────
    AUTO_CONTAINMENT_THRESHOLD: float = 0.85
    LIVE_SIMULATION_WORKER_ACTIVE: bool = True
    SIMULATION_INTERVAL_SECONDS: int = 30

    # ── Rate Limiting ──────────────────────────────────────────────────
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 300
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ── Wazuh Manager API Integration ───────────────────────────────────
    # SAFETY: All disabled by default. Must explicitly enable for production.
    WAZUH_ENABLED: bool = False
    WAZUH_DRY_RUN: bool = True                            # True = log only, no actions
    WAZUH_CLOSE_MODE: str = "comment_only"               # comment_only | archive_only | archive_and_comment
    WAZUH_MANAGER_URL: str = ""                          # https://wazuh.example.com:55000
    WAZUH_USER: str = ""
    WAZUH_PASSWORD: str = ""
    WAZUH_VERIFY_SSL: bool = True

    # ── Security ───────────────────────────────────────────────────────
    CORS_ALLOWED_ORIGINS: list[str] = ["*"]


settings = Settings()
