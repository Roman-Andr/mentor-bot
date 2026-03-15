"""Configuration settings for the Meeting Service."""

from typing import TYPE_CHECKING

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    PostgresDsn = str
else:
    from pydantic import PostgresDsn


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Meeting Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: PostgresDsn = Field(default="postgresql+asyncpg://user:password@localhost:5432/meeting_db")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_SCHEMA: str = Field(default="meeting")

    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_HOSTS: list[str] = ["*"]
    CORS_ORIGINS: list[str] = ["*"]

    # Auth service integration
    AUTH_SERVICE_URL: str = Field(default="http://auth_service:8000")
    AUTH_SERVICE_TIMEOUT: int = Field(default=10, ge=1)

    # Google Calendar Integration
    GOOGLE_CLIENT_ID: str = Field(default="")
    GOOGLE_CLIENT_SECRET: str = Field(default="")
    GOOGLE_REDIRECT_URI: str = Field(default="")
    GOOGLE_CALENDAR_SCOPES: list[str] = Field(default=["https://www.googleapis.com/auth/calendar.events"])

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")


settings = Settings()
