"""Keyboards package for Telegram Bot."""

from telegram_bot.keyboards.admin import get_admin_keyboard
from telegram_bot.keyboards.admin_detail import (
    get_admin_checklists_keyboard,
    get_admin_stats_keyboard,
    get_admin_users_keyboard,
    get_back_to_admin_checklists_keyboard,
    get_back_to_admin_panel_keyboard,
    get_back_to_admin_stats_keyboard,
    get_back_to_admin_users_keyboard,
)
from telegram_bot.keyboards.calendar_kb import (
    get_calendar_connected_keyboard,
    get_calendar_connect_keyboard,
    get_calendar_not_connected_keyboard,
)
from telegram_bot.keyboards.checklist import (
    get_checklists_keyboard,
    get_task_detail_keyboard,
    get_tasks_keyboard,
)
from telegram_bot.keyboards.checklist_detail import (
    get_attach_task_keyboard,
    get_back_to_task_keyboard,
    get_no_checklists_keyboard,
    get_no_tasks_keyboard,
    get_skip_description_keyboard,
    get_task_completed_keyboard,
    get_task_info_keyboard,
)
from telegram_bot.keyboards.common_kb import (
    get_help_keyboard,
    get_mentor_tasks_keyboard,
    get_my_mentor_keyboard,
    get_my_mentor_no_mentor_keyboard,
    get_progress_keyboard,
    get_schedule_mentor_keyboard,
)
from telegram_bot.keyboards.documents_kb import (
    get_article_detail_keyboard,
    get_article_list_keyboard,
    get_documents_menu_keyboard,
)
from telegram_bot.keyboards.escalation_kb import (
    get_escalation_details_keyboard,
    get_escalation_menu_keyboard,
    get_my_escalations_keyboard,
    get_new_escalation_keyboard,
)
from telegram_bot.keyboards.feedback_kb import (
    get_experience_rating_keyboard,
    get_feedback_menu_keyboard,
)
from telegram_bot.keyboards.knowledge_kb import (
    get_admin_knowledge_keyboard,
    get_article_view_keyboard,
    get_faq_keyboard,
    get_kb_article_saved_keyboard,
    get_kb_categories_keyboard,
    get_kb_create_files_keyboard,
    get_kb_upload_complete_keyboard,
    get_kb_upload_files_keyboard,
    get_knowledge_base_menu_keyboard,
    get_search_no_results_keyboard,
    get_search_results_keyboard,
)
from telegram_bot.keyboards.language_kb import get_language_keyboard
from telegram_bot.keyboards.main_menu import (
    get_inline_main_menu,
    get_main_menu_keyboard,
)
from telegram_bot.keyboards.meetings_kb import (
    get_meeting_details_keyboard,
    get_meetings_menu_keyboard,
    get_my_meetings_keyboard,
)

__all__ = [
    # admin
    "get_admin_checklists_keyboard",
    "get_admin_keyboard",
    "get_admin_stats_keyboard",
    "get_admin_users_keyboard",
    "get_back_to_admin_checklists_keyboard",
    "get_back_to_admin_panel_keyboard",
    "get_back_to_admin_stats_keyboard",
    "get_back_to_admin_users_keyboard",
    # calendar
    "get_calendar_connected_keyboard",
    "get_calendar_connect_keyboard",
    "get_calendar_not_connected_keyboard",
    # checklists
    "get_attach_task_keyboard",
    "get_back_to_task_keyboard",
    "get_checklists_keyboard",
    "get_no_checklists_keyboard",
    "get_no_tasks_keyboard",
    "get_skip_description_keyboard",
    "get_task_completed_keyboard",
    "get_task_detail_keyboard",
    "get_task_info_keyboard",
    "get_tasks_keyboard",
    # common
    "get_help_keyboard",
    "get_inline_main_menu",
    "get_main_menu_keyboard",
    "get_mentor_tasks_keyboard",
    "get_my_mentor_keyboard",
    "get_my_mentor_no_mentor_keyboard",
    "get_progress_keyboard",
    "get_schedule_mentor_keyboard",
    # documents
    "get_article_detail_keyboard",
    "get_article_list_keyboard",
    "get_documents_menu_keyboard",
    # escalation
    "get_escalation_details_keyboard",
    "get_escalation_menu_keyboard",
    "get_my_escalations_keyboard",
    "get_new_escalation_keyboard",
    # feedback
    "get_experience_rating_keyboard",
    "get_feedback_menu_keyboard",
    # knowledge
    "get_admin_knowledge_keyboard",
    "get_article_view_keyboard",
    "get_faq_keyboard",
    "get_kb_article_saved_keyboard",
    "get_kb_categories_keyboard",
    "get_kb_create_files_keyboard",
    "get_kb_upload_complete_keyboard",
    "get_kb_upload_files_keyboard",
    "get_knowledge_base_menu_keyboard",
    "get_search_no_results_keyboard",
    "get_search_results_keyboard",
    # language
    "get_language_keyboard",
    # meetings
    "get_meeting_details_keyboard",
    "get_meetings_menu_keyboard",
    "get_my_meetings_keyboard",
]
