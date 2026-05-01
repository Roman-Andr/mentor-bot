"""Template rendering service using Jinja2 for notification templates."""

import logging
from dataclasses import dataclass
from typing import Any

from jinja2 import BaseLoader, Environment, TemplateError

from notification_service.models import NotificationTemplate
from notification_service.repositories.unit_of_work import IUnitOfWork

logger = logging.getLogger(__name__)


@dataclass
class RenderedNotification:
    """Result of rendering a notification template."""

    subject: str | None
    body: str
    channel: str
    variables_used: list[str]


class TemplateNotFoundError(Exception):
    """Raised when a template is not found."""

    def __init__(self, template_name: str, channel: str, language: str) -> None:
        """Initialize with template lookup details."""
        self.template_name = template_name
        self.channel = channel
        self.language = language
        super().__init__(f"Template '{template_name}' not found for channel '{channel}' and language '{language}'")


class MissingTemplateVariablesError(Exception):
    """Raised when required template variables are missing."""

    def __init__(self, missing_variables: set[str]) -> None:
        """Initialize with set of missing variable names."""
        self.missing_variables = missing_variables
        super().__init__(f"Missing required template variables: {', '.join(missing_variables)}")


class TemplateRenderError(Exception):
    """Raised when template rendering fails."""

    def __init__(self, message: str) -> None:
        """Initialize with error message."""
        super().__init__(f"Template rendering failed: {message}")


class TemplateService:
    """Service for rendering notification templates using Jinja2."""

    # Default templates used as fallback when no database template exists
    DEFAULT_TEMPLATES: dict[tuple[str, str, str], dict[str, Any]] = {
        # Welcome templates
        ("welcome", "telegram", "en"): {
            "subject": None,
            "body_text": "Welcome, {{ user_name }}! 🎉\n\nYour onboarding journey starts today. We're excited to have you on board!",
            "variables": ["user_name"],
        },
        ("welcome", "telegram", "ru"): {
            "subject": None,
            "body_text": "Привет, {{ user_name }}! 🎉\n\nТвой онбординг начинается сегодня. Рады видеть тебя в команде!",
            "variables": ["user_name"],
        },
        ("welcome", "email", "en"): {
            "subject": "Welcome to Mentor Bot, {{ user_name }}!",
            "body_text": "Hi {{ user_name }},\n\nWelcome to Mentor Bot! Your onboarding journey starts today.\n\nWe're here to help you succeed.",
            "body_html": "<h1>Welcome, {{ user_name }}!</h1><p>Your onboarding journey starts today. We're here to help you succeed.</p>",
            "variables": ["user_name"],
        },
        # Task reminder templates
        ("task_reminder", "telegram", "en"): {
            "subject": None,
            "body_text": "⏰ Task Reminder: {{ task_title }}\n\nDue: {{ due_date }}\n\nDon't forget to complete this task!",
            "variables": ["task_title", "due_date"],
        },
        ("task_reminder", "telegram", "ru"): {
            "subject": None,
            "body_text": "⏰ Напоминание о задаче: {{ task_title }}\n\nСрок: {{ due_date }}\n\nНе забудь выполнить задачу!",
            "variables": ["task_title", "due_date"],
        },
        ("task_reminder", "email", "en"): {
            "subject": "Task Due: {{ task_title }}",
            "body_text": """Hi {{ user_name }},

This is a reminder that your task '{{ task_title }}' is due on {{ due_date }}.

Please complete it on time.""",
            "body_html": "<h1>Task Reminder</h1><p>Hi {{ user_name }},</p><p>Your task <strong>{{ task_title }}</strong> is due on <strong>{{ due_date }}</strong>.</p><p>Please complete it on time.</p>",
            "variables": ["user_name", "task_title", "due_date"],
        },
        # Meeting reminder templates
        ("meeting_scheduled", "telegram", "en"): {
            "subject": None,
            "body_text": "📅 Meeting: {{ meeting_title }}\n\nScheduled for: {{ meeting_time }}\n\nWith: {{ mentor_name }}",
            "variables": ["meeting_title", "meeting_time", "mentor_name"],
        },
        ("meeting_scheduled", "telegram", "ru"): {
            "subject": None,
            "body_text": "📅 Встреча: {{ meeting_title }}\n\nНазначена на: {{ meeting_time }}\n\nС: {{ mentor_name }}",
            "variables": ["meeting_title", "meeting_time", "mentor_name"],
        },
        ("meeting_scheduled", "email", "en"): {
            "subject": "Meeting Scheduled: {{ meeting_title }}",
            "body_text": """Hi {{ user_name }},

A meeting has been scheduled:

Title: {{ meeting_title }}
Time: {{ meeting_time }}
With: {{ mentor_name }}

See you there!""",
            "body_html": "<h1>Meeting Scheduled</h1><p>Hi {{ user_name }},</p><p>A meeting has been scheduled:</p><ul><li><strong>Title:</strong> {{ meeting_title }}</li><li><strong>Time:</strong> {{ meeting_time }}</li><li><strong>With:</strong> {{ mentor_name }}</li></ul><p>See you there!</p>",
            "variables": ["user_name", "meeting_title", "meeting_time", "mentor_name"],
        },
        # Meeting reminder (before meeting)
        ("meeting_reminder", "telegram", "en"): {
            "subject": None,
            "body_text": "⏰ Reminder: {{ meeting_title }} starts in {{ minutes_until }} minutes!",
            "variables": ["meeting_title", "minutes_until"],
        },
        ("meeting_reminder", "telegram", "ru"): {
            "subject": None,
            "body_text": "⏰ Напоминание: {{ meeting_title }} начнется через {{ minutes_until }} минут!",
            "variables": ["meeting_title", "minutes_until"],
        },
        # Escalation templates
        ("escalation_assigned", "telegram", "en"): {
            "subject": None,
            "body_text": "🔔 New escalation assigned to you!\n\nID: #{{ escalation_id }}\nPriority: {{ priority }}\nReason: {{ reason_preview }}\n\n[View Details]({{ link }})",
            "variables": ["escalation_id", "priority", "reason_preview", "link"],
        },
        ("escalation_created_confirmation", "telegram", "en"): {
            "subject": None,
            "body_text": "✅ Your escalation #{{ escalation_id }} has been created.\n\nWe'll get back to you soon.\n\n[Track Status]({{ link }})",
            "variables": ["escalation_id", "link"],
        },
        ("escalation_assigned_to_you", "telegram", "en"): {
            "subject": None,
            "body_text": "📋 Escalation assigned to you\n\nID: #{{ escalation_id }}\nReason: {{ reason_preview }}\n\n[View Details]({{ link }})",
            "variables": ["escalation_id", "reason_preview", "link"],
        },
        ("escalation_reassigned", "telegram", "en"): {
            "subject": None,
            "body_text": "🔄 Escalation reassigned\n\nID: #{{ escalation_id }} has been reassigned to another team member.\n\n[View Details]({{ link }})",
            "variables": ["escalation_id", "link"],
        },
        ("escalation_resolved", "telegram", "en"): {
            "subject": None,
            "body_text": "✅ Your escalation #{{ escalation_id }} has been RESOLVED!\n\nComment: {{ comment }}\n\n[View Details]({{ link }})",
            "variables": ["escalation_id", "comment", "link"],
        },
        ("escalation_in_progress", "telegram", "en"): {
            "subject": None,
            "body_text": "🔄 Your escalation #{{ escalation_id }} is now IN PROGRESS.\n\nSomeone is working on it!\n\n[View Details]({{ link }})",
            "variables": ["escalation_id", "link"],
        },
        ("escalation_rejected", "telegram", "en"): {
            "subject": None,
            "body_text": "❌ Your escalation #{{ escalation_id }} has been rejected.\n\nComment: {{ comment }}\n\n[View Details]({{ link }})",
            "variables": ["escalation_id", "comment", "link"],
        },
        ("escalation_closed", "telegram", "en"): {
            "subject": None,
            "body_text": "🔒 Your escalation #{{ escalation_id }} has been CLOSED.\n\nComment: {{ comment }}\n\n[View Details]({{ link }})",
            "variables": ["escalation_id", "comment", "link"],
        },
        ("escalation_updated", "telegram", "en"): {
            "subject": None,
            "body_text": "📝 Your escalation #{{ escalation_id }} has been updated.\n\nStatus changed from {{ old_status }} to {{ new_status }}.\n\nComment: {{ comment }}\n\n[View Details]({{ link }})",
            "variables": ["escalation_id", "old_status", "new_status", "comment", "link"],
        },
        # Feedback templates
        ("feedback_request", "telegram", "en"): {
            "subject": None,
            "body_text": "📝 Feedback Request\n\nHi {{ user_name }}, please share your feedback about {{ topic }}.",
            "variables": ["user_name", "topic"],
        },
        ("comment_reply", "telegram", "en"): {
            "subject": None,
            "body_text": "💬 Reply to your comment\n\nYour comment: \"{{ original_comment_preview }}\"\n\nReply from {{ replied_by_name }}:\n{{ reply_text }}",
            "variables": ["original_comment_preview", "reply_text", "replied_by_name"],
        },
        ("comment_reply", "telegram", "ru"): {
            "subject": None,
            "body_text": "💬 Ответ на ваш комментарий\n\nВаш комментарий: \"{{ original_comment_preview }}\"\n\nОтвет от {{ replied_by_name }}:\n{{ reply_text }}",
            "variables": ["original_comment_preview", "reply_text", "replied_by_name"],
        },
        ("comment_reply", "email", "en"): {
            "subject": "Reply to your comment",
            "body_text": """Hi,

You received a reply to your comment:

Your comment: "{{ original_comment_preview }}"

Reply from {{ replied_by_name }}:
{{ reply_text }}

---
This is an automated message from Mentor Bot.""",
            "body_html": "<h1>Reply to your comment</h1><p>You received a reply to your comment:</p><p><strong>Your comment:</strong> "{{ original_comment_preview }}"</p><p><strong>Reply from {{ replied_by_name }}:</strong></p><p>{{ reply_text }}</p><hr><p><em>This is an automated message from Mentor Bot.</em></p>",
            "variables": ["original_comment_preview", "reply_text", "replied_by_name"],
        },
        ("comment_reply", "email", "ru"): {
            "subject": "Ответ на ваш комментарий",
            "body_text": """Здравствуйте,

Вы получили ответ на ваш комментарий:

Ваш комментарий: "{{ original_comment_preview }}"

Ответ от {{ replied_by_name }}:
{{ reply_text }}

---
Это автоматическое сообщение от Mentor Bot.""",
            "body_html": "<h1>Ответ на ваш комментарий</h1><p>Вы получили ответ на ваш комментарий:</p><p><strong>Ваш комментарий:</strong> "{{ original_comment_preview }}"</p><p><strong>Ответ от {{ replied_by_name }}:</strong></p><p>{{ reply_text }}</p><hr><p><em>Это автоматическое сообщение от Mentor Bot.</em></p>",
            "variables": ["original_comment_preview", "reply_text", "replied_by_name"],
        },
        # Onboarding templates
        ("onboarding_day1", "telegram", "en"): {
            "subject": None,
            "body_text": "👋 Day 1 Check-in\n\nHi {{ user_name }}! How was your first day? Complete your Day 1 checklist to track your progress.",
            "variables": ["user_name"],
        },
        ("onboarding_week1", "telegram", "en"): {
            "subject": None,
            "body_text": "📊 Week 1 Progress\n\nHi {{ user_name }}! You've completed {{ completed_tasks }} of {{ total_tasks }} tasks. Keep it up!",
            "variables": ["user_name", "completed_tasks", "total_tasks"],
        },
        # Certificate templates
        ("certificate_issued", "telegram", "en"): {
            "subject": None,
            "body_text": "🎉 Congratulations, {{ employee_name }}!\n\nYou have been issued a certificate for completing the onboarding program \"{{ program_name }}\".\n\nCertificate ID: {{ cert_uid }}\n\nDownload your certificate: /certificate",
            "variables": ["employee_name", "program_name", "cert_uid"],
        },
        ("certificate_issued", "telegram", "ru"): {
            "subject": None,
            "body_text": "🎉 Поздравляем, {{ employee_name }}!\n\nВам выдан сертификат за завершение программы онбординга \"{{ program_name }}\".\n\nID сертификата: {{ cert_uid }}\n\nСкачать сертификат: /certificate",
            "variables": ["employee_name", "program_name", "cert_uid"],
        },
        # Password reset
        ("password_reset", "email", "en"): {
            "subject": "Password Reset Request",
            "body_text": "Hi {{ user_name }},\n\nYou requested a password reset. Click the link below to reset your password:\n\n{{ reset_link }}\n\nIf you didn't request this, please ignore this email.",
            "body_html": "<h1>Password Reset</h1><p>Hi {{ user_name }},</p><p>You requested a password reset. Click the link below:</p><p><a href='{{ reset_link }}'>Reset Password</a></p><p>If you didn't request this, please ignore this email.</p>",
            "variables": ["user_name", "reset_link"],
        },
        # General notification
        ("general", "telegram", "en"): {
            "subject": None,
            "body_text": "{{ message }}",
            "variables": ["message"],
        },
        ("general", "email", "en"): {
            "subject": "{{ subject }}",
            "body_text": "{{ message }}",
            "body_html": "<p>{{ message }}</p>",
            "variables": ["subject", "message"],
        },
    }

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize the template service with Unit of Work."""
        self._uow = uow
        self._env = Environment(loader=BaseLoader(), autoescape=True)

    async def get_template(
        self, name: str, channel: str, language: str = "en"
    ) -> NotificationTemplate | None:
        """
        Get template by name, channel, and language.

        First tries to get from database, falls back to defaults if not found.
        """
        # Try database first
        db_template = await self._uow.templates.get_by_name_channel_language(name, channel, language)
        if db_template:
            return db_template

        # Fall back to defaults
        return self._get_default_template(name, channel, language)

    def _get_default_template(self, name: str, channel: str, language: str) -> NotificationTemplate | None:
        """Get default template from built-in defaults."""
        # Try exact match first
        key = (name, channel, language)
        if key in self.DEFAULT_TEMPLATES:
            data = self.DEFAULT_TEMPLATES[key]
            return self._create_template_from_defaults(name, channel, language, data)

        # Fall back to English if language not found
        if language != "en":
            key_en = (name, channel, "en")
            if key_en in self.DEFAULT_TEMPLATES:
                data = self.DEFAULT_TEMPLATES[key_en]
                return self._create_template_from_defaults(name, channel, language, data)

        return None

    def _create_template_from_defaults(
        self, name: str, channel: str, language: str, data: dict[str, Any]
    ) -> NotificationTemplate:
        """Create a NotificationTemplate instance from default data."""
        return NotificationTemplate(
            id=0,  # Default templates don't have DB IDs
            name=name,
            channel=channel,
            language=language,
            subject=data.get("subject"),
            body_html=data.get("body_html"),
            body_text=data.get("body_text"),
            version=1,
            is_active=True,
            is_default=True,
            variables=data.get("variables", []),
            created_by=None,
        )

    def validate_variables(self, template: NotificationTemplate, variables: dict[str, Any]) -> set[str]:
        """
        Validate that all required template variables are provided.

        Returns set of missing variable names.
        """
        required = set(template.variables or [])
        provided = set(variables.keys())
        return required - provided

    async def render(
        self,
        template_name: str,
        channel: str,
        language: str,
        variables: dict[str, Any],
        validate: bool = True,
    ) -> RenderedNotification:
        """
        Render a template with the given variables.

        Args:
            template_name: Name of the template to render
            channel: Channel type (telegram, email, etc.)
            language: Language code (e.g., 'en', 'ru')
            variables: Dictionary of variables to substitute in the template
            validate: Whether to validate that all required variables are present

        Returns:
            RenderedNotification with rendered subject and body

        Raises:
            TemplateNotFoundError: If template is not found
            MissingTemplateVariablesError: If required variables are missing
            TemplateRenderError: If rendering fails

        """
        # Get template
        template = await self.get_template(template_name, channel, language)
        if not template:
            raise TemplateNotFoundError(template_name, channel, language)

        # Validate variables if requested
        if validate:
            missing = self.validate_variables(template, variables)
            if missing:
                raise MissingTemplateVariablesError(missing)

        # Determine which body to use based on channel and available formats
        body_template = template.body_text
        if channel == "email" and template.body_html:
            body_template = template.body_html

        if not body_template:
            msg = f"Template '{template_name}' has no content for channel '{channel}'"
            raise TemplateRenderError(msg)

        # Render templates
        try:
            # Render subject if present
            rendered_subject = None
            if template.subject:
                subject_template = self._env.from_string(template.subject)
                rendered_subject = subject_template.render(**variables)

            # Render body
            body_jinja = self._env.from_string(body_template)
            rendered_body = body_jinja.render(**variables)

        except TemplateError as e:
            raise TemplateRenderError(str(e)) from e

        return RenderedNotification(
            subject=rendered_subject,
            body=rendered_body,
            channel=channel,
            variables_used=list(variables.keys()),
        )

    async def render_for_user(
        self,
        template_name: str,
        user: Any,  # User model with first_name, language attributes
        variables: dict[str, Any],
        channel: str | None = None,
    ) -> RenderedNotification:
        """
        Render a template for a specific user, using their preferences.

        Automatically adds user variables and uses user's preferred language.
        """
        # Determine channel from user preferences or default
        user_channel = channel or getattr(user, "preferred_channel", "telegram")
        user_language = getattr(user, "language", "en")
        user_name = getattr(user, "first_name", "User")

        # Merge variables with user context
        merged_variables = {
            "user_name": user_name,
            **variables,
        }

        return await self.render(
            template_name=template_name,
            channel=user_channel,
            language=user_language,
            variables=merged_variables,
        )
