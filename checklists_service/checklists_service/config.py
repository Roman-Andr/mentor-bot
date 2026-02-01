"""Configuration settings for the Checklists Service."""

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
    APP_NAME: str = "Checklists Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: PostgresDsn = Field(default="postgresql+asyncpg://user:password@localhost:5432/checklists_db")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_SCHEMA: str = Field(default="checklists")

    # Redis
    REDIS_URL: RedisDsn = Field(default="redis://localhost:6379/1")
    REDIS_CACHE_TTL: int = Field(default=3600, ge=1)

    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_HOSTS: list[str] = ["*"]

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Integration with Auth Service
    AUTH_SERVICE_URL: str = Field(default="http://localhost:8001")
    AUTH_SERVICE_TIMEOUT: int = Field(default=10, ge=1)
    AUTH_SERVICE_RETRIES: int = Field(default=3, ge=0)

    # Circuit Breaker
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = Field(default=3, ge=1)
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = Field(default=30, ge=1)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")


settings = Settings()
