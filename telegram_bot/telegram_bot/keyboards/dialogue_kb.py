"""Dialogue (FAQ) keyboard factory."""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.keyboards.utils import create_inline_button


def get_faq_menu_keyboard(scenarios: list[dict]) -> InlineKeyboardMarkup:
    """Create FAQ menu keyboard with scenarios."""
    builder = InlineKeyboardBuilder()

    for scenario in scenarios:
        builder.add(
            create_inline_button(
                scenario["title"],
                callback_data=f"faq_scenario_{scenario['id']}",
                style=ButtonStyle.PRIMARY,
            )
        )

    builder.add(
        create_inline_button("\u2b05 Back to Menu", callback_data="back_to_menu")
    )

    builder.adjust(1)
    return builder.as_markup()


def get_dialogue_step_keyboard(step: dict) -> InlineKeyboardMarkup:
    """Create keyboard for a dialogue step based on answer_type."""
    builder = InlineKeyboardBuilder()

    answer_type = step.get("answer_type", "TEXT")
    options = step.get("options", [])
    is_final = step.get("is_final", False)

    if answer_type == "CHOICE" and options:
        for option in options:
            builder.add(
                create_inline_button(
                    option.get("label", ""),
                    callback_data=f"faq_next_{option.get('next_step', 0)}",
                    style=ButtonStyle.PRIMARY,
                )
            )
    elif answer_type == "LINK":
        if step.get("answer_content"):
            builder.add(
                create_inline_button(
                    "\U0001f517 Подробнее",
                    url=step["answer_content"],
                    style=ButtonStyle.PRIMARY,
                )
            )

    if not is_final:
        builder.add(create_inline_button("\u2b05 К началу", callback_data="faq_menu"))

    builder.add(
        create_inline_button("\u2b05 В главное меню", callback_data="back_to_menu")
    )

    builder.adjust(1)
    return builder.as_markup()
