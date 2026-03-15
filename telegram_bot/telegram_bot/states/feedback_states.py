"""Feedback and survey FSM states."""

from aiogram.fsm.state import State, StatesGroup


class FeedbackStates(StatesGroup):
    """Feedback and survey states."""

    waiting_for_pulse_rating = State()
    waiting_for_comments = State()
