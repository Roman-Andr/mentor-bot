"""Feedback and survey keyboards."""

from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.i18n import t
from telegram_bot.keyboards.utils import create_inline_button


def get_feedback_menu_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build feedback menu keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\U0001f60a {t('feedback.btn_pulse', locale=locale)}",
            callback_data="pulse_survey",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2b50 {t('feedback.btn_experience', locale=locale)}",
            callback_data="rate_experience",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f4ac {t('feedback.btn_comments', locale=locale)}",
            callback_data="comments_suggestions",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.menu_button', locale=locale)}", callback_data="menu"
        ),
    )
    builder.adjust(1)
    return builder


def get_experience_rating_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build experience rating keyboard (1-5 stars)."""
    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.add(
            create_inline_button(
                f"\u2b50 {i}", callback_data=f"rate_{i}", style=ButtonStyle.PRIMARY
            )
        )
    builder.adjust(5)
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="feedback_menu",
        )
    )
    return builder
