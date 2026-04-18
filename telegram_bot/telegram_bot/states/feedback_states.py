"""Feedback and survey FSM states."""

from aiogram.fsm.state import State, StatesGroup


class FeedbackStates(StatesGroup):
    """Feedback and survey states."""

    waiting_for_anonymity_choice = State()
    waiting_for_pulse_rating = State()
    waiting_for_experience_rating = State()
    waiting_for_comments = State()
    waiting_for_comment_anonymity = State()
