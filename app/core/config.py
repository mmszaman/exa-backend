# app/core/config.py
# Configuration management for the application using Pydantic BaseSettings.
# Loads settings from environment variables and .env file.
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.logger import get_logger

_env = os.getenv("APP_ENV", "development").lower().strip()
_selected_env_file = ".env"
_logger = get_logger("config")

# Determine the appropriate .env file based on the environment
# Priority: production > staging > development
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_selected_env_file,
        case_sensitive=True,
    )

    # App config
    APP_NAME: str = "SMB-Backend"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS - store as string, parse when needed
    FRONTEND_ORIGINS: str = "http://localhost:3000,http://localhost:4000"
    BACKEND_ORIGINS: str = "http://localhost:8000"
    
    # Parse FRONTEND_ORIGINS into a list
    def get_frontend_origins(self) -> List[str]:
        return [origin.strip() for origin in self.FRONTEND_ORIGINS.split(",")]

    # Email configuration
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USER: str = ""
    EMAIL_PASSWORD: str = ""
    ADMIN_TO: str = "exateks@gmail.com"
    SEND_FROM: str = ""

    # Dev mode
    DEV_FAKE_EMAILS: bool = False
    DEV_FAKE_LOG: str = "sent_emails.log"
    
    # Database
    DATABASE_URL: str = ""
    
    # Clerk Authentication
    CLERK_SECRET_KEY: str = ""
    CLERK_PUBLISHABLE_KEY: str = ""
    CLERK_WEBHOOK_SECRET: str = ""
    
    # AI API for SMBPilot (OpenAI, Anthropic, or Groq)
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    AI_PROVIDER: str = "groq"  # "openai", "anthropic", or "groq" (FREE!)
    
    # Security
    SECRET_KEY: str = ""

settings = Settings()

# Startup diagnostics
_logger.info(f"Loaded settings for APP_ENV='{_env}' from '{_selected_env_file}'")

if _env == "production":
    missing = []
    if not settings.EMAIL_USER:
        missing.append("EMAIL_USER")
    if not settings.EMAIL_PASSWORD:
        missing.append("EMAIL_PASSWORD")
    if missing:
        _logger.warning(
            "Production environment missing critical email config: " + ", ".join(missing)
        )
