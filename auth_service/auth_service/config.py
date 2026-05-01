"""Configuration settings for the Auth Service."""

from typing import TYPE_CHECKING

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    PostgresDsn = str
    RedisDsn = str
else:
    from pydantic import PostgresDsn, RedisDsn


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Auth Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: PostgresDsn = Field(...)
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: RedisDsn = Field(...)

    # Security - MUST be set via environment variables
    SECRET_KEY: str = Field(min_length=32)
    JWT_SECRET_KEY: str = Field(min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12

    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_HOSTS: list[str] = ["*"]

    # Invitations
    INVITATION_TOKEN_LENGTH: int = 32
    INVITATION_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Telegram
    TELEGRAM_API_KEY: str = Field(...)
    TELEGRAM_BOT_USERNAME: str = Field(...)

    # Inter-service communication
    CHECKLISTS_SERVICE_URL: str = Field(...)
    KNOWLEDGE_SERVICE_URL: str = Field(...)
    MEETING_SERVICE_URL: str = Field(...)
    NOTIFICATION_SERVICE_URL: str = Field(...)
    SERVICE_API_KEY: str = Field(...)

    # Password reset
    ADMIN_WEB_URL: str = Field(...)

    # Default admin user
    ADMIN_EMAIL: str = Field(...)
    ADMIN_PASSWORD: str = Field(...)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")


settings = Settings()  # type: ignore[call-arg]
