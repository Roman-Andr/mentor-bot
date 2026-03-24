"""Registration utilities for Telegram Bot."""

import logging

from aiogram.fsm.context import FSMContext
from aiogram.types import User as TgUser

from telegram_bot.services.auth_client import auth_client
from telegram_bot.services.cache import user_cache
from telegram_bot.utils.validators import validate_invitation_token

logger = logging.getLogger(__name__)


async def register_by_token(
    token: str,
    tg_user: TgUser,
    state: FSMContext,
) -> tuple[bool, dict | str]:
    """Register user by invitation token."""
    if not validate_invitation_token(token):
        return False, "❌ Invalid token format. Please check your invitation link."

    invitation = await auth_client.validate_invitation_token(token)

    if not invitation:
        return (
            False,
            "❌ Invalid or expired invitation token.\nPlease check your invitation link or contact HR.",
        )

    telegram_data = {
        "api_key": auth_client.client.headers.get("X-API-Key"),
        "telegram_id": tg_user.id,
        "username": tg_user.username,
        "first_name": tg_user.first_name,
        "last_name": tg_user.last_name,
        "phone": None,
    }

    registration_result = await auth_client.register_with_invitation(
        token, telegram_data
    )

    if not registration_result:
        return False, "❌ Registration failed. Please try again or contact HR."

    user_data = await auth_client.get_current_user(registration_result["access_token"])

    if user_data:
        await user_cache.set_user(
            tg_user.id,
            {
                **user_data,
                "access_token": registration_result["access_token"],
                "refresh_token": registration_result["refresh_token"],
            },
        )

        await state.clear()

        return True, user_data
    return False, "❌ Failed to retrieve user information. Please contact support."
