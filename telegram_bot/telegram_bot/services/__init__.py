"""Service clients for external API integration."""

from telegram_bot.services.auth_client import AuthServiceClient, auth_client
from telegram_bot.services.cache import UserCache, user_cache
from telegram_bot.services.checklists_client import (
    ChecklistsServiceClient,
    checklists_client,
)
from telegram_bot.services.escalation_client import EscalationServiceClient, escalation_client
from telegram_bot.services.knowledge_client import KnowledgeServiceClient, knowledge_client
from telegram_bot.services.meeting_client import MeetingServiceClient, meeting_client
from telegram_bot.services.notification_client import NotificationServiceClient, notification_client

__all__ = [
    "AuthServiceClient",
    "ChecklistsServiceClient",
    "EscalationServiceClient",
    "KnowledgeServiceClient",
    "MeetingServiceClient",
    "NotificationServiceClient",
    "UserCache",
    "auth_client",
    "checklists_client",
    "escalation_client",
    "knowledge_client",
    "meeting_client",
    "notification_client",
    "user_cache",
]
