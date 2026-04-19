"""Configuration settings for the Knowledge Service."""

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
    APP_NAME: str = "Knowledge Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: PostgresDsn = Field(default="postgresql+asyncpg://user:password@localhost:5432/knowledge_db")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_SCHEMA: str = Field(default="knowledge")

    # Redis
    REDIS_URL: RedisDsn = Field(default="redis://localhost:6379/2")
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

    # Service-to-service authentication
    SERVICE_API_KEY: str = Field(default="")

    # Circuit Breaker
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = Field(default=3, ge=1)
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = Field(default=30, ge=1)

    # File Storage - S3/MinIO
    MAX_FILE_SIZE_MB: int = Field(default=10, ge=1)
    ALLOWED_FILE_TYPES: list[str] = Field(
        default=["pdf", "jpg", "jpeg", "png", "docx", "xlsx", "txt", "md", "ics", "zip", "py", "pptx"]
    )
    S3_ENDPOINT: str = Field(default="http://minio:9000")
    S3_ACCESS_KEY: str = Field(default="")
    S3_SECRET_KEY: str = Field(default="")
    S3_REGION: str = Field(default="us-east-1")
    S3_USE_SSL: bool = Field(default=False)
    KNOWLEDGE_S3_BUCKET: str = Field(default="knowledge-files")
    S3_PRESIGNED_URL_EXPIRY: int = Field(default=3600, ge=60, le=604800)
    S3_SECURE_MODE: bool = Field(default=False)

    # Search Configuration
    SEARCH_RESULTS_LIMIT: int = Field(default=10, ge=1, le=100)
    SEARCH_CACHE_TTL: int = Field(default=300, ge=1)
    SEARCH_SUGGESTIONS_CACHE_TTL: int = Field(default=300, ge=1)
    POPULAR_SEARCHES_CACHE_TTL: int = Field(default=3600, ge=1)

    # Integration Cache TTLs
    AUTH_TOKEN_CACHE_TTL: int = Field(default=300, ge=1)
    AUTH_USER_CACHE_TTL: int = Field(default=600, ge=1)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")


settings = Settings()
