"""Pytest configuration for telegram_bot tests."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import i18n  # type: ignore[import-untyped]
import pytest

# Set environment variables BEFORE any imports
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("SERVICE_API_KEY", "test-api-key")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456789:test_token")
os.environ.setdefault("TELEGRAM_API_KEY", "test-telegram-api-key")
os.environ.setdefault("AUTH_SERVICE_URL", "http://auth:8001")
os.environ.setdefault("CHECKLISTS_SERVICE_URL", "http://checklists:8002")
os.environ.setdefault("KNOWLEDGE_SERVICE_URL", "http://knowledge:8003")
os.environ.setdefault("NOTIFICATION_SERVICE_URL", "http://notification:8004")
os.environ.setdefault("ESCALATION_SERVICE_URL", "http://escalation:8005")
os.environ.setdefault("MEETING_SERVICE_URL", "http://meeting:8006")
os.environ.setdefault("FEEDBACK_SERVICE_URL", "http://feedback:8007")

# Patch service clients BEFORE any handler modules import them
# This prevents real HTTP requests during tests (SERVICE_TIMEOUT = 10s)
# Create AsyncMock with default return_value=None for async methods
_mock_knowledge_client = AsyncMock()
_mock_knowledge_client.get_article_details = AsyncMock(return_value=None)
_mock_auth_client = AsyncMock()
_mock_auth_client.authenticate_with_telegram = AsyncMock(return_value=None)
_mock_auth_client.get_current_user = AsyncMock(return_value=None)
patch("telegram_bot.services.knowledge_client.knowledge_client", _mock_knowledge_client).start()
patch("telegram_bot.services.auth_client.auth_client", _mock_auth_client).start()

# Configure i18n for tests with test translations that include key names
# This allows tests to verify translation keys while testing real i18n code
i18n.set("file_format", "json")
i18n.set("filename_format", "{locale}.{format}")
i18n.set("fallback", "en")
i18n.set("available_locales", ["en", "ru"])
i18n.set("skip_locale_root_data", True)

# Add test translations that include key names for verification
# Using add_translation(key, value, locale) for each key
_test_translations_flat = [
    # English translations - common namespace
    ("common.back_button", "Back [common.back_button]", "en"),
    ("common.loading", "Loading... [common.loading]", "en"),
    ("common.access_denied", "Access denied [common.access_denied]", "en"),
    ("common.error_generic", "Error [common.error_generic]", "en"),
    ("common.auth_required", "Auth required [common.auth_required]", "en"),
    # English translations - auth namespace
    ("auth.logged_out", "Logged out [auth.logged_out]", "en"),
    ("auth.logout_success", "Logout success [auth.logout_success]", "en"),
    ("auth.invalid_token", "Invalid token [auth.invalid_token]", "en"),
    # English translations - start namespace
    ("start.register_error", "Register error [start.register_error]", "en"),
    ("start.welcome_new", "Welcome new [start.welcome_new]", "en"),
    # English translations - feedback namespace
    ("feedback.pulse_thanks", "Thanks {rating} [feedback.pulse_thanks]", "en"),
    ("feedback.pulse_invalid", "Invalid {min}-{max} [feedback.pulse_invalid]", "en"),
    ("feedback.title", "Feedback [feedback.title]", "en"),
    ("feedback.description", "Feedback desc [feedback.description]", "en"),
    ("feedback.options", "Options [feedback.options]", "en"),
    # English translations - meetings namespace
    ("meetings.title_too_short", "Title too short {min} [meetings.title_too_short]", "en"),
    ("meetings.no_meetings_list", "No meetings [meetings.no_meetings_list]", "en"),
    # English translations - tasks namespace
    ("tasks.attach_file_prompt", "Attach file [tasks.attach_file_prompt]", "en"),
    ("tasks.attachment_failed", "Attachment failed [tasks.attachment_failed]", "en"),
    # English translations - checklists namespace
    ("checklists.no_tasks_general", "No tasks [checklists.no_tasks_general]", "en"),
    # English translations - escalation namespace
    ("escalation.no_escalations", "No escalations [escalation.no_escalations]", "en"),
    # Russian translations
    ("common.back_button", "Назад [common.back_button]", "ru"),
]

def _ensure_test_translations() -> None:
    """Ensure test translations are in the i18n container."""
    for key, value, locale in _test_translations_flat:
        i18n.add_translation(key, value, locale)


# Add translations at import time
_ensure_test_translations()


@pytest.fixture(autouse=True)
def _setup_i18n() -> None:
    """Ensure i18n test translations are always present before each test."""
    _ensure_test_translations()


@pytest.fixture
def mock_tg_user():
    """Create a mock Telegram User object."""
    user = MagicMock()
    user.first_name = "John"
    user.last_name = "Doe"
    user.id = 123456
    user.username = "johndoe"
    return user


@pytest.fixture
def mock_tg_user_no_last_name():
    """Create a mock Telegram User without last name."""
    user = MagicMock()
    user.first_name = "Jane"
    user.last_name = None
    user.id = 789012
    user.username = "jane"
    return user


@pytest.fixture
def mock_message():
    """Create a mock Telegram Message object."""
    message = MagicMock()
    message.message_id = 1
    message.chat = MagicMock()
    message.chat.id = 123456
    message.from_user = MagicMock()
    message.from_user.id = 123456
    message.from_user.first_name = "John"
    message.from_user.last_name = "Doe"
    message.from_user.username = "johndoe"
    message.text = "Test message"
    message.answer = AsyncMock()
    return message


@pytest.fixture
def mock_callback_query():
    """Create a mock Telegram CallbackQuery object."""
    callback = MagicMock()
    callback.id = "callback_123"
    callback.from_user = MagicMock()
    callback.from_user.id = 123456
    callback.from_user.first_name = "John"
    callback.from_user.last_name = "Doe"
    callback.data = "test_callback"
    callback.answer = AsyncMock()
    callback.message = MagicMock()
    callback.message.chat = MagicMock()
    callback.message.chat.id = 123456
    callback.message.edit_text = AsyncMock()
    callback.message.edit_reply_markup = AsyncMock()
    callback.message.answer_document = AsyncMock()
    return callback


@pytest.fixture
def mock_bot():
    """Create a mock Telegram Bot object."""
    bot = MagicMock()
    bot.get_file = AsyncMock()
    bot.get_file.return_value = MagicMock(file_path="test/path/file.txt")
    bot.download_file = AsyncMock(return_value=b"file content")
    return bot


@pytest.fixture
def mock_state():
    """Create a mock FSMContext object."""
    state = MagicMock()
    state.clear = AsyncMock()
    state.update_data = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    state.set_state = AsyncMock()
    return state


@pytest.fixture
def mock_user_data():
    """Create sample user data."""
    return {
        "id": 1,
        "employee_id": "EMP123",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "USER",
        "department": {"name": "Engineering"},
        "position": "Developer",
    }


@pytest.fixture
def mock_admin_user():
    """Create sample admin user data."""
    return {
        "id": 2,
        "employee_id": "ADM001",
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "role": "ADMIN",
        "department": {"name": "HR"},
        "position": "HR Manager",
    }


@pytest.fixture
def mock_checklist():
    """Create sample checklist data."""
    return {
        "id": 1,
        "name": "Onboarding Checklist",
        "status": "in_progress",
        "progress_percentage": 50,
        "total_tasks": 10,
        "completed_tasks": 5,
    }


@pytest.fixture
def mock_task():
    """Create sample task data."""
    return {
        "id": 1,
        "title": "Complete Profile",
        "description": "Fill in your profile information",
        "status": "pending",
        "category": "onboarding",
        "due_date": "2024-12-31",
        "checklist_id": 1,
    }


@pytest.fixture
def mock_fsm_context():
    """Create a mock FSM context with data."""
    context = MagicMock()
    context.get_data = AsyncMock(return_value={
        "attach_task_id": 1,
        "attach_checklist_id": 1,
        "attach_file_id": "file_123",
        "attach_filename": "document.pdf",
    })
    context.update_data = AsyncMock()
    context.set_state = AsyncMock()
    context.clear = AsyncMock()
    return context
