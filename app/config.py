"""
Configuration module - settings from environment variables
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    See .env.example for template.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
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
