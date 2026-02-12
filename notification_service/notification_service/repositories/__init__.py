"""Repository pattern implementation for data access layer."""

from notification_service.repositories.implementations import NotificationRepository, ScheduledNotificationRepository
from notification_service.repositories.interfaces import (
    BaseRepository,
    INotificationRepository,
    IScheduledNotificationRepository,
)
from notification_service.repositories.unit_of_work import IUnitOfWork, SqlAlchemyUnitOfWork, sqlalchemy_uow

__all__ = [
    "BaseRepository",
    "INotificationRepository",
    "IScheduledNotificationRepository",
    "IUnitOfWork",
    "NotificationRepository",
    "ScheduledNotificationRepository",
    "SqlAlchemyUnitOfWork",
    "sqlalchemy_uow",
]
