"""Pydantic schemas for request/response validation."""

from notification_service.schemas.notification import (
    NotificationBase,
    NotificationCreate,
    NotificationListResponse,
    NotificationResponse,
    ScheduledNotificationCreate,
    ScheduledNotificationResponse,
)
from notification_service.schemas.responses import HealthCheck, MessageResponse, ServiceStatus
from notification_service.schemas.template import (
    TemplateCreate,
    TemplateListResponse,
    TemplatePreviewRequest,
    TemplateRenderRequest,
    TemplateRenderResponse,
    TemplateResponse,
    TemplateUpdate,
)

__all__ = [
    "HealthCheck",
    "MessageResponse",
    "NotificationBase",
    "NotificationCreate",
    "NotificationListResponse",
    "NotificationResponse",
    "ScheduledNotificationCreate",
    "ScheduledNotificationResponse",
    "ServiceStatus",
    "TemplateCreate",
    "TemplateListResponse",
    "TemplatePreviewRequest",
    "TemplateRenderRequest",
    "TemplateRenderResponse",
    "TemplateResponse",
    "TemplateUpdate",
]
