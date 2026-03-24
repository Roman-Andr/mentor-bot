"""Escalation keyboards."""

from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.i18n import t
from telegram_bot.keyboards.utils import create_inline_button


def get_escalation_menu_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build escalation menu keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\u2795 {t('escalation.btn_new', locale=locale)}",
            callback_data="new_escalation",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f4cb {t('escalation.btn_my', locale=locale)}",
            callback_data="my_escalations",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u2190 {t('common.menu_button', locale=locale)}", callback_data="menu"
        ),
    )
    builder.adjust(1)
    return builder


def get_new_escalation_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build new escalation type selection keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\u2753 {t('escalation.type_question', locale=locale)}",
            callback_data="escalate_question",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f465 {t('escalation.type_mentor', locale=locale)}",
            callback_data="escalate_mentor",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f4de {t('escalation.type_hr', locale=locale)}",
            callback_data="escalate_hr",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\u26a0\ufe0f {t('escalation.type_technical', locale=locale)}",
            callback_data="escalate_technical",
            style=ButtonStyle.DANGER,
        ),
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="escalate_menu",
        ),
    )
    builder.adjust(1)
    return builder


def get_my_escalations_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build back button keyboard for my escalations."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="escalate_menu",
        )
    )
    return builder


def get_escalation_details_keyboard(*, locale: str = "en") -> InlineKeyboardBuilder:
    """Build back button keyboard for escalation details."""
    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button(
            f"\u2190 {t('common.back_button', locale=locale)}",
            callback_data="my_escalations",
        )
    )
    return builder
