"""Feedback and survey keyboards."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.i18n import t
from telegram_bot.keyboards.utils import create_inline_button


def get_feedback_menu_keyboard(*, locale: str = "en") -> InlineKeyboardMarkup:
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
        create_inline_button(f"\u2190 {t('common.menu_button', locale=locale)}", callback_data="menu"),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_pulse_rating_keyboard(*, locale: str = "en", is_anonymous: bool = False) -> InlineKeyboardMarkup:
    """Build pulse rating keyboard (10-1) - reversed with emojis."""
    builder = InlineKeyboardBuilder()
    # Emojis for ratings: 10=🤩, 9=😃, 8=😊, 7=🙂, 6=😐, 5=🤔, 4=😕, 3=😟, 2=😢, 1=😭
    emojis = {
        10: "\U0001f929",
        9: "\U0001f603",
        8: "\U0001f60a",
        7: "\U0001f642",
        6: "\U0001f610",
        5: "\U0001f914",
        4: "\U0001f615",
        3: "\U0001f61f",
        2: "\U0001f622",
        1: "\U0001f62d",
    }
    # Add high ratings first: 10, 9, 8, 7
    for i in range(10, 6, -1):
        builder.add(
            create_inline_button(
                f"{emojis[i]} {i}",
                callback_data=f"pulse_{i}_anon_{is_anonymous}",
                style=ButtonStyle.PRIMARY,
            )
        )
    # Add medium ratings: 6, 5, 4, 3
    for i in range(6, 2, -1):
        builder.add(
            create_inline_button(
                f"{emojis[i]} {i}",
                callback_data=f"pulse_{i}_anon_{is_anonymous}",
                style=ButtonStyle.PRIMARY,
            )
        )
    # Add low ratings: 2, 1
    for i in range(2, 0, -1):
        builder.add(
            create_inline_button(
                f"{emojis[i]} {i}",
                callback_data=f"pulse_{i}_anon_{is_anonymous}",
                style=ButtonStyle.PRIMARY,
            )
        )
    # Add back button in fourth row
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="feedback_menu",
        )
    )
    builder.adjust(4, 4, 2, 1)
    return builder.as_markup()


def get_anonymity_choice_keyboard(*, locale: str = "en", survey_type: str = "pulse") -> InlineKeyboardMarkup:
    """Build anonymity choice keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\U0001f464 {t('feedback.btn_anonymous', locale=locale)}",
            callback_data=f"{survey_type}_anon_choice_true",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f465 {t('feedback.btn_attributed', locale=locale)}",
            callback_data=f"{survey_type}_anon_choice_false",
            style=ButtonStyle.PRIMARY,
        ),
    )
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="feedback_menu",
        )
    )
    builder.adjust(2, 1)
    return builder.as_markup()


def get_experience_rating_keyboard(*, locale: str = "en", is_anonymous: bool = False) -> InlineKeyboardMarkup:
    """Build experience rating keyboard (5-1 stars) - reversed with emojis."""
    builder = InlineKeyboardBuilder()
    # Emojis for ratings: 5=😍, 4=🙂, 3=😐, 2=😕, 1=😢
    emojis = {
        5: "\U0001f60d",
        4: "\U0001f642",
        3: "\U0001f610",
        2: "\U0001f615",
        1: "\U0001f622",
    }
    # Add high ratings first: 5, 4, 3
    for i in range(5, 2, -1):
        builder.add(
            create_inline_button(
                f"{emojis[i]} {i}", callback_data=f"rate_{i}_anon_{is_anonymous}", style=ButtonStyle.PRIMARY
            )
        )
    # Add low ratings: 2, 1
    for i in range(2, 0, -1):
        builder.add(
            create_inline_button(
                f"{emojis[i]} {i}", callback_data=f"rate_{i}_anon_{is_anonymous}", style=ButtonStyle.PRIMARY
            )
        )
    # Add back button in third row
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="feedback_menu",
        )
    )
    builder.adjust(3, 2, 1)
    return builder.as_markup()
