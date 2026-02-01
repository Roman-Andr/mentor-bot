"""Checklist and task management FSM states."""

from aiogram.fsm.state import State, StatesGroup


class ChecklistStates(StatesGroup):
    """States for checklist operations."""

    waiting_for_task_selection = State()
    waiting_for_completion_notes = State()
    waiting_for_feedback = State()
    waiting_for_attachment = State()
