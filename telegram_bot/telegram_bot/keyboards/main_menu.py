"""Main menu keyboard factory."""

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.keyboards.utils import create_inline_button, create_keyboard_button


def get_main_menu_keyboard(*, is_authenticated: bool = False) -> ReplyKeyboardMarkup:
    """Create main menu keyboard."""
    builder = ReplyKeyboardBuilder()

    if is_authenticated:
        builder.add(
            create_keyboard_button("\U0001f4cb My Tasks", style=ButtonStyle.PRIMARY)
        )
        builder.add(
            create_keyboard_button(
                "\U0001f50d Knowledge Base", style=ButtonStyle.PRIMARY
            )
        )
        builder.add(
            create_keyboard_button("\U0001f4c1 Documents", style=ButtonStyle.PRIMARY)
        )
        builder.add(
            create_keyboard_button("\U0001f4c5 Meetings", style=ButtonStyle.PRIMARY)
        )
        builder.add(
            create_keyboard_button("\U0001f4c5 Calendar", style=ButtonStyle.PRIMARY)
        )
        builder.add(
            create_keyboard_button(
                "\U0001f468\u200d\U0001f3eb My Mentor", style=ButtonStyle.PRIMARY
            )
        )
        builder.add(
            create_keyboard_button("\U0001f4de Contact HR", style=ButtonStyle.PRIMARY)
        )
        builder.add(
            create_keyboard_button("\U0001f4ca Feedback", style=ButtonStyle.PRIMARY)
        )
        builder.add(create_keyboard_button("\u2139\ufe0f Help"))
    else:
        builder.add(create_keyboard_button("/start", style=ButtonStyle.PRIMARY))
        builder.add(create_keyboard_button("/help"))

    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_inline_main_menu() -> InlineKeyboardMarkup:
    """Create inline main menu matching TZ layout: 2 columns."""
    builder = InlineKeyboardBuilder()

    # Row 1: My Tasks | Knowledge Base
    builder.add(
        create_inline_button(
            "\U0001f4cb My Tasks", callback_data="my_tasks", style=ButtonStyle.PRIMARY
        ),
        create_inline_button(
            "\U0001f50d Knowledge Base",
            callback_data="knowledge_base",
            style=ButtonStyle.PRIMARY,
        ),
    )
    # Row 2: Search Answer | Documents
    builder.add(
        create_inline_button(
            "\U0001f50d Search Answer",
            callback_data="search_kb",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            "\U0001f4c1 Documents",
            callback_data="documents_menu",
            style=ButtonStyle.PRIMARY,
        ),
    )
    # Row 3: My Mentor | Calendar
    builder.add(
        create_inline_button(
            "\U0001f468\u200d\U0001f3eb My Mentor",
            callback_data="my_mentor",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            "\U0001f4c5 Calendar",
            callback_data="calendar_menu",
            style=ButtonStyle.PRIMARY,
        ),
    )
    # Row 4: Meetings | Escalate
    builder.add(
        create_inline_button(
            "\U0001f4c5 Meetings",
            callback_data="meetings_menu",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            "\U0001f4de Escalate",
            callback_data="escalate_menu",
            style=ButtonStyle.PRIMARY,
        ),
    )
    # Row 5: Contact HR | Feedback
    builder.add(
        create_inline_button(
            "\U0001f4de Contact HR",
            callback_data="contact_hr",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            "\U0001f4ca Feedback",
            callback_data="feedback_menu",
            style=ButtonStyle.PRIMARY,
        ),
    )
    # Row 6: Progress (centered)
    builder.add(
        create_inline_button(
            "\U0001f4ca Progress", callback_data="progress", style=ButtonStyle.PRIMARY
        ),
        create_inline_button("\u2139\ufe0f Help", callback_data="help"),
    )

    builder.adjust(2)
    return builder.as_markup()
