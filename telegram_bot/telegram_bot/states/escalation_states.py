"""Escalation FSM states."""

from aiogram.fsm.state import State, StatesGroup


class EscalationStates(StatesGroup):
    """Escalation states."""

    waiting_for_description = State()
    waiting_for_title = State()
