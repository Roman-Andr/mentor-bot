"""Configuration settings for Telegram Bot."""

from typing import TYPE_CHECKING

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from pydantic import PostgresDsn, RedisDsn
else:
    PostgresDsn = str
    RedisDsn = str


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram Bot API Token")
    TELEGRAM_API_KEY: str = Field(..., description="Telegram API Key for auth")
    TELEGRAM_PROXY: str = Field(default="", description="Proxy URL for Telegram Bot (e.g., socks5://127.0.0.1:1080)")

    # Application
    APP_NAME: str = "Mentor Bot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Redis
    REDIS_URL: RedisDsn = Field(...)
    REDIS_CACHE_TTL: int = Field(default=3600, ge=1)

    # Database
    DATABASE_URL: PostgresDsn = Field(...)

    # Services
    AUTH_SERVICE_URL: str = Field(...)
    CHECKLISTS_SERVICE_URL: str = Field(...)
    KNOWLEDGE_SERVICE_URL: str = Field(...)
    NOTIFICATION_SERVICE_URL: str = Field(...)
    ESCALATION_SERVICE_URL: str = Field(...)
    MEETING_SERVICE_URL: str = Field(...)
    FEEDBACK_SERVICE_URL: str = Field(...)
    API_V1_PREFIX: str = Field(default="/api/v1")

    # Timeouts
    SERVICE_TIMEOUT: int = Field(default=10, ge=1)
    SERVICE_RETRIES: int = Field(default=3, ge=0)

    # Inter-service communication
    SERVICE_API_KEY: str = Field(...)

    # Admin
    ADMIN_IDS: list[int] = Field(default_factory=list)

    # Features
    ENABLE_WELCOME_TOUR: bool = Field(default=True)
    ENABLE_NOTIFICATIONS: bool = Field(default=True)
    NOTIFICATION_HOUR: int = Field(default=9, ge=0, le=23)
    THROTTLING_ENABLED: bool = Field(default=False)

    # Google Calendar Integration
    GOOGLE_CLIENT_ID: str = Field(...)
    GOOGLE_CLIENT_SECRET: str = Field(...)
    GOOGLE_REDIRECT_URI: str = Field(...)
    GOOGLE_CALENDAR_SCOPES: list[str] = Field(default=["https://www.googleapis.com/auth/calendar.events"])

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")


settings = Settings()
