"""Meeting FSM states."""

from aiogram.fsm.state import State, StatesGroup


class MeetingStates(StatesGroup):
    """Meeting states."""

    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_datetime = State()
    waiting_for_duration = State()
