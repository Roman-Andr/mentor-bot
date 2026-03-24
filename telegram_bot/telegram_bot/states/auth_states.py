"""Authentication and registration FSM states."""

from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """States for user registration process."""

    waiting_for_token = State()


class SearchStates(StatesGroup):
    """States for knowledge base search."""

    waiting_for_query = State()


class ArticleCreateStates(StatesGroup):
    """States for creating an article via the bot."""

    waiting_for_title = State()
    waiting_for_content = State()
    waiting_for_files = State()


class FileUploadStates(StatesGroup):
    """States for uploading files to an existing article."""

    waiting_for_article_id = State()
    waiting_for_files = State()
