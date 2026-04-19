"""Telegram authentication validation module."""

from secrets import compare_digest

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.config import settings
from auth_service.models import User

MAX_AUTH_AGE_SECONDS = 60 * 5


def verify_telegram_api_key(api_key: str) -> bool:
    """Validate Telegram API key."""
    return compare_digest(api_key, settings.TELEGRAM_API_KEY)


async def verify_telegram_user_exists(db: AsyncSession, telegram_id: int) -> bool:
    """Check if Telegram user exists in database."""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None
