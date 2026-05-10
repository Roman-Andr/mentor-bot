"""Publish Telegram bot events from auth service."""

import json
from typing import Any

from loguru import logger
from redis.asyncio import Redis

from auth_service.config import settings

TELEGRAM_EVENTS_CHANNEL = "telegram_events"


async def publish_telegram_event(event_type: str, **payload: Any) -> None:
    """
    Publish an event consumed by the Telegram bot.

    Event delivery must not make user management operations fail, so Redis
    errors are logged and swallowed.
    """
    redis: Redis | None = None
    try:
        redis = Redis.from_url(str(settings.REDIS_URL), decode_responses=True)
        message = json.dumps({"type": event_type, **payload})
        await redis.publish(TELEGRAM_EVENTS_CHANNEL, message)
    except Exception:
        logger.exception("Failed to publish Telegram event (event_type={})", event_type)
    finally:
        if redis:
            try:
                await redis.aclose()
            except Exception:
                logger.exception("Failed to close Redis publisher connection")
