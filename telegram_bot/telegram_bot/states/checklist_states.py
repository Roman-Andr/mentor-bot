"""Checklist and task management FSM states."""

from aiogram.fsm.state import State, StatesGroup


class ChecklistStates(StatesGroup):
    """States for checklist operations."""

    waiting_for_task_selection = State()
