"""Checklist and task management FSM states."""

from aiogram.fsm.state import State, StatesGroup


class ChecklistStates(StatesGroup):
    """States for checklist operations."""

    waiting_for_task_selection = State()


class TaskAttachmentStates(StatesGroup):
    """States for task attachment upload."""

    waiting_for_file = State()
    waiting_for_description = State()
    confirm_upload = State()
