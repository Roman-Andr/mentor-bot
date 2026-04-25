"""Configuration settings for the Feedback Service."""

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
    APP_NAME: str = "Feedback Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: PostgresDsn = Field(default="postgresql+asyncpg://user:password@localhost:5432/feedback_db")
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_HOSTS: list[str] = ["*"]
    CORS_ORIGINS: list[str] = ["*"]

    # Auth service integration
    AUTH_SERVICE_URL: str = Field(default="http://auth_service:8000")
    AUTH_SERVICE_TIMEOUT: int = Field(default=10, ge=1)

    # Service-to-service authentication
    SERVICE_API_KEY: str | None = Field(default=None)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")


settings = Settings()
