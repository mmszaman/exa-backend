"""
Configuration module - settings from environment variables
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    See .env.example for template.
    """

    # App config
    APP_NAME: str = "Exakeep Backend"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    FRONTEND_ORIGINS: List[str] = ["http://localhost:3000"]

    # Email configuration
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USER: str = ""
    EMAIL_PASSWORD: str = ""
    ADMIN_TO: str = "exateks@gmail.com"

    # Dev mode
    DEV_FAKE_EMAILS: bool = False
    DEV_FAKE_LOG: str = "sent_emails.log"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
