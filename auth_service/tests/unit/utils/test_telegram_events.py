"""Tests for Telegram event publishing helpers."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from auth_service.utils import telegram_events


@pytest.mark.asyncio
async def test_publish_telegram_event_publishes_json_payload(monkeypatch):
    """Test successful Telegram event publishing."""
    redis = MagicMock()
    redis.publish = AsyncMock()
    redis.aclose = AsyncMock()
    from_url = MagicMock(return_value=redis)

    monkeypatch.setattr(telegram_events.Redis, "from_url", from_url)

    await telegram_events.publish_telegram_event(
        "user_deactivated",
        user_id=1,
        telegram_id=123456,
    )

    from_url.assert_called_once_with(
        str(telegram_events.settings.REDIS_URL),
        decode_responses=True,
    )
    redis.publish.assert_awaited_once()
    channel, message = redis.publish.await_args.args
    assert channel == telegram_events.TELEGRAM_EVENTS_CHANNEL
    assert json.loads(message) == {
        "type": "user_deactivated",
        "user_id": 1,
        "telegram_id": 123456,
    }
    redis.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_publish_telegram_event_swallows_publish_errors(monkeypatch):
    """Test Redis publish errors are logged and swallowed."""
    redis = MagicMock()
    redis.publish = AsyncMock(side_effect=RuntimeError("publish failed"))
    redis.aclose = AsyncMock()
    logger = MagicMock()

    monkeypatch.setattr(telegram_events.Redis, "from_url", MagicMock(return_value=redis))
    monkeypatch.setattr(telegram_events, "logger", logger)

    await telegram_events.publish_telegram_event("user_deactivated", user_id=1)

    logger.exception.assert_called_once_with(
        "Failed to publish Telegram event (event_type={})",
        "user_deactivated",
    )
    redis.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_publish_telegram_event_swallows_connection_errors(monkeypatch):
    """Test Redis creation errors are logged and swallowed."""
    logger = MagicMock()

    monkeypatch.setattr(
        telegram_events.Redis,
        "from_url",
        MagicMock(side_effect=RuntimeError("connection failed")),
    )
    monkeypatch.setattr(telegram_events, "logger", logger)

    await telegram_events.publish_telegram_event("user_deactivated", user_id=1)

    logger.exception.assert_called_once_with(
        "Failed to publish Telegram event (event_type={})",
        "user_deactivated",
    )


@pytest.mark.asyncio
async def test_publish_telegram_event_swallows_close_errors(monkeypatch):
    """Test Redis close errors are logged and swallowed."""
    redis = MagicMock()
    redis.publish = AsyncMock()
    redis.aclose = AsyncMock(side_effect=RuntimeError("close failed"))
    logger = MagicMock()

    monkeypatch.setattr(telegram_events.Redis, "from_url", MagicMock(return_value=redis))
    monkeypatch.setattr(telegram_events, "logger", logger)

    await telegram_events.publish_telegram_event("user_deactivated", user_id=1)

    redis.publish.assert_awaited_once()
    logger.exception.assert_called_once_with("Failed to close Redis publisher connection")
