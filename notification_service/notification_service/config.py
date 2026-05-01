"""Configuration settings for the Notification Service."""

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
    APP_NAME: str = "Notification Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: PostgresDsn = Field(...)
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_HOSTS: list[str] = ["*"]
    CORS_ORIGINS: list[str] = ["*"]

    # Auth service integration
    AUTH_SERVICE_URL: str = Field(...)
    AUTH_SERVICE_TIMEOUT: int = Field(default=10, ge=1)

    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram Bot Token")
    TELEGRAM_API_URL: str = "https://api.telegram.org/bot"

    # Email SMTP
    SMTP_HOST: str = Field(...)
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str | None = Field(default=None)
    SMTP_PASSWORD: str | None = Field(default=None)
    SMTP_USE_TLS: bool = Field(default=True)
    DEFAULT_FROM_EMAIL: str = Field(...)
    EMAIL_DRY_RUN: bool = Field(
        default=True,
        description="Log emails instead of sending. Set EMAIL_DRY_RUN=False to enable actual email delivery",
    )

    # Scheduler
    SCHEDULER_POLL_INTERVAL_SECONDS: int = Field(default=60, ge=1)  # Check every minute

    # Inter-service communication
    SERVICE_API_KEY: str = Field(...)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")


settings = Settings()
