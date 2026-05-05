"""Keyboard utility functions with style support."""

from aiogram.types import InlineKeyboardButton, KeyboardButton

from telegram_bot.core.enums import ButtonStyle


def create_inline_button(
    text: str,
    callback_data: str | None = None,
    url: str | None = None,
    style: ButtonStyle | None = None,
) -> InlineKeyboardButton:
    """Create an inline keyboard button."""
    kwargs = {"text": text}

    if callback_data:
        kwargs["callback_data"] = callback_data
    if url:
        kwargs["url"] = url
    if style:
        kwargs["style"] = style.value

    return InlineKeyboardButton(**kwargs)


def create_keyboard_button(
    text: str,
    style: ButtonStyle | None = None,
) -> KeyboardButton:
    """Create a reply keyboard button with optional style."""
    kwargs = {"text": text}

    if style:
        kwargs["style"] = style.value

    return KeyboardButton(**kwargs)
