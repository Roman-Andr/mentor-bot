"""Configuration settings for Telegram Bot."""

from typing import TYPE_CHECKING

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from pydantic import PostgresDsn, RedisDsn
else:
    from pydantic import PostgresDsn, RedisDsn


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram Bot API Token")
    TELEGRAM_API_KEY: str = Field(..., description="Telegram API Key for auth")

    # Application
    APP_NAME: str = "Mentor Bot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Redis
    REDIS_URL: RedisDsn = Field(default="redis://localhost:6379/3")
    REDIS_CACHE_TTL: int = Field(default=3600, ge=1)

    # Database
    DATABASE_URL: PostgresDsn = Field(default="postgresql+asyncpg://user:password@localhost:5432/telegram_bot")
    DATABASE_SCHEMA: str = Field(default="telegram_bot")

    # Services
    AUTH_SERVICE_URL: str = Field(default="http://localhost:8001")
    CHECKLISTS_SERVICE_URL: str = Field(default="http://localhost:8002")

    # Timeouts
    SERVICE_TIMEOUT: int = Field(default=10, ge=1)
    SERVICE_RETRIES: int = Field(default=3, ge=0)

    # Admin
    ADMIN_IDS: list[int] = Field(default_factory=list)

    # Features
    ENABLE_WELCOME_TOUR: bool = Field(default=True)
    ENABLE_NOTIFICATIONS: bool = Field(default=True)
    NOTIFICATION_HOUR: int = Field(default=9, ge=0, le=23)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")


settings = Settings()
