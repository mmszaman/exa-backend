"""Configuration module - dynamic settings loader.

Supports multiple environment files selected via APP_ENV:
- APP_ENV=development -> .env.development (default)
- APP_ENV=staging     -> .env.staging (optional)
- APP_ENV=production  -> .env.production

OS environment variables always override values from files.
"""
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.logger import get_logger

_env = os.getenv("APP_ENV", "development").lower().strip()
_env_file_map = {
    "development": ".env.development",
    "staging": ".env.staging",
    "production": ".env.production",
}
_selected_env_file = _env_file_map.get(_env, ".env.development")
_logger = get_logger("config")


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    See .env.example for template.
    """
    model_config = SettingsConfigDict(
        env_file=_selected_env_file,
        case_sensitive=True,
    )

    # App config
    APP_NAME: str = "Exa-Backend"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS - store as string, parse when needed
    FRONTEND_ORIGINS: str = "http://localhost:3000"
    
    def get_frontend_origins(self) -> List[str]:
        """Get FRONTEND_ORIGINS as a list"""
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
