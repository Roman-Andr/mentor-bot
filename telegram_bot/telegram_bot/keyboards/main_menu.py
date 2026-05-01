"""Main menu keyboard factory."""

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.i18n import t
from telegram_bot.keyboards.utils import create_inline_button, create_keyboard_button


def _is_admin(user: dict | None) -> bool:
    """Check if user has admin role (HR or ADMIN)."""
    if not user:
        return False
    return user.get("role") in ("HR", "ADMIN")


def get_main_menu_keyboard(
    *, is_authenticated: bool = False, user: dict | None = None, locale: str = "en"
) -> ReplyKeyboardMarkup:
    """Create main menu keyboard."""
    builder = ReplyKeyboardBuilder()

    if is_authenticated:
        builder.add(
            create_keyboard_button(
                f"\U0001f4cb {t('buttons.my_tasks', locale=locale)}",
                style=ButtonStyle.PRIMARY,
            )
        )
        builder.add(
            create_keyboard_button(
                f"\U0001f50d {t('buttons.knowledge_base', locale=locale)}",
                style=ButtonStyle.PRIMARY,
            )
        )
        builder.add(
            create_keyboard_button(
                f"\U0001f4c1 {t('buttons.documents', locale=locale)}",
                style=ButtonStyle.PRIMARY,
            )
        )
        builder.add(
            create_keyboard_button(
                f"\U0001f4c5 {t('buttons.meetings', locale=locale)}",
                style=ButtonStyle.PRIMARY,
            )
        )
        builder.add(
            create_keyboard_button(
                f"\U0001f4c5 {t('buttons.calendar', locale=locale)}",
                style=ButtonStyle.PRIMARY,
            )
        )
        builder.add(
            create_keyboard_button(
                f"\U0001f468\u200d\U0001f3eb {t('buttons.my_mentor', locale=locale)}",
                style=ButtonStyle.PRIMARY,
            )
        )
        builder.add(
            create_keyboard_button(
                f"🚨 {t('buttons.escalate', locale=locale)}",
                style=ButtonStyle.DANGER,
            )
        )
        builder.add(
            create_keyboard_button(
                f"\U0001f4ca {t('buttons.feedback', locale=locale)}",
                style=ButtonStyle.PRIMARY,
            )
        )
        builder.add(create_keyboard_button(f"\u2139\ufe0f {t('buttons.help', locale=locale)}"))
        builder.add(create_keyboard_button(f"\u2699\ufe0f {t('buttons.settings', locale=locale)}"))

        # Add admin button if user has admin role
        if _is_admin(user):
            builder.add(
                create_keyboard_button(
                    f"\U0001f451 {t('buttons.admin', locale=locale)}",
                    style=ButtonStyle.PRIMARY,
                )
            )
    else:
        builder.add(create_keyboard_button("/start", style=ButtonStyle.PRIMARY))
        builder.add(create_keyboard_button("/help"))

    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_inline_main_menu(user: dict | None = None, locale: str = "en") -> InlineKeyboardMarkup:
    """Create inline main menu matching TZ layout: 2 columns."""
    builder = InlineKeyboardBuilder()

    # Row 1: My Tasks | Knowledge Base
    builder.add(
        create_inline_button(
            f"\U0001f4cb {t('buttons.my_tasks', locale=locale)}",
            callback_data="my_tasks",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f50d {t('buttons.knowledge_base', locale=locale)}",
            callback_data="knowledge_base",
            style=ButtonStyle.PRIMARY,
        ),
    )
    # Row 2: Search Answer | Documents
    builder.add(
        create_inline_button(
            f"\U0001f50d {t('buttons.search_answer', locale=locale)}",
            callback_data="search_kb",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f4c1 {t('buttons.documents', locale=locale)}",
            callback_data="documents_menu",
            style=ButtonStyle.PRIMARY,
        ),
    )
    # Row 3: My Mentor
    builder.add(
        create_inline_button(
            f"\U0001f468\u200d\U0001f3eb {t('buttons.my_mentor', locale=locale)}",
            callback_data="my_mentor",
            style=ButtonStyle.PRIMARY,
        ),
    )
    # Row 4: Calendar | Meetings
    builder.add(
        create_inline_button(
            f"\U0001f4c5 {t('buttons.calendar', locale=locale)}",
            callback_data="calendar_menu",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f4c5 {t('buttons.meetings', locale=locale)}",
            callback_data="meetings_menu",
            style=ButtonStyle.PRIMARY,
        ),
    )
    # Row 5: Escalate (red/danger style, separate row for visibility)
    builder.add(
        create_inline_button(
            f"🚨 {t('buttons.escalate', locale=locale)}",
            callback_data="escalate_menu",
            style=ButtonStyle.DANGER,
        ),
    )
    # Row 6: Feedback | Progress
    builder.add(
        create_inline_button(
            f"\U0001f4ca {t('buttons.feedback', locale=locale)}",
            callback_data="feedback_menu",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(
            f"\U0001f4ca {t('buttons.progress', locale=locale)}",
            callback_data="progress",
            style=ButtonStyle.PRIMARY,
        ),
    )

    # Row 7: Settings | Help
    builder.add(
        create_inline_button(
            f"\u2699\ufe0f {t('buttons.settings', locale=locale)}",
            callback_data="settings_menu",
            style=ButtonStyle.PRIMARY,
        ),
        create_inline_button(f"\u2139\ufe0f {t('buttons.help', locale=locale)}", callback_data="help"),
    )

    # Row 8: Admin (if applicable)
    if _is_admin(user):
        builder.add(
            create_inline_button(
                f"\U0001f451 {t('buttons.admin', locale=locale)}",
                callback_data="admin_panel",
                style=ButtonStyle.DANGER,
            ),
        )
        builder.adjust(2, 2, 2, 2, 1, 2, 2, 1)
    else:
        builder.adjust(2, 2, 2, 2, 1, 2, 2)

    return builder.as_markup()
