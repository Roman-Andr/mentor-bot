"""Telegram integration service."""

import logging

import httpx

from notification_service.config import settings

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for sending messages via Telegram Bot API."""

    def __init__(self) -> None:
        """Initialize Telegram service with bot token."""
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.api_url = f"{settings.TELEGRAM_API_URL}{self.token}"

    async def send_message(self, chat_id: int, text: str) -> bool:
        """Send a plain text message to a Telegram chat."""
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",  # Allow basic formatting
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=10.0)
                response.raise_for_status()
                result = response.json()
                if result.get("ok"):
                    return True
                logger.error(f"Telegram API error: {result}")
                return False
            except Exception as e:
                logger.exception(f"Failed to send Telegram message: {e}")
                return False
