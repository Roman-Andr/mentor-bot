"""Authentication and registration FSM states."""

from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """States for user registration process."""

    waiting_for_token = State()
    waiting_for_email = State()
    waiting_for_confirmation = State()
    waiting_for_phone = State()


class SearchStates(StatesGroup):
    """States for knowledge base search."""

    waiting_for_query = State()
    waiting_for_confirmation = State()
    waiting_for_feedback = State()
