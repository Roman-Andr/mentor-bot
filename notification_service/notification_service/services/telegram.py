"""Telegram integration service via Redis pub/sub."""

import json
import logging

from redis.asyncio import Redis

from notification_service.config import settings

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for sending messages via Telegram Bot using Redis pub/sub."""

    def __init__(self) -> None:
        """Initialize Telegram service with Redis client."""
        self.redis: Redis | None = None
        self.channel = "telegram_notifications"

    async def _get_redis(self) -> Redis:
        """Get or create Redis connection."""
        if self.redis is None:
            self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        return self.redis

    async def send_message(self, chat_id: int, text: str) -> bool:
        """Send a plain text message to a Telegram chat via Redis pub/sub."""
        try:
            redis = await self._get_redis()
            message = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
            }
            await redis.publish(self.channel, json.dumps(message))
            logger.info("Telegram notification published to Redis (chat_id=%s)", chat_id)
            return True
        except Exception:
            logger.exception("Failed to publish Telegram notification to Redis")
            return False

    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis:
            try:
                await self.redis.close()
            except Exception:
                logger.exception("Failed to close Redis connection")
            finally:
                self.redis = None
