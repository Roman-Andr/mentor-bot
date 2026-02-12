"""Repository pattern implementation for data access layer."""

from meeting_service.repositories.implementations import MaterialRepository, MeetingRepository, UserMeetingRepository
from meeting_service.repositories.interfaces import (
    BaseRepository,
    IMaterialRepository,
    IMeetingRepository,
    IUserMeetingRepository,
)
from meeting_service.repositories.unit_of_work import IUnitOfWork, SqlAlchemyUnitOfWork, sqlalchemy_uow

__all__ = [
    "BaseRepository",
    "IMaterialRepository",
    "IMeetingRepository",
    "IUnitOfWork",
    "IUserMeetingRepository",
    "MaterialRepository",
    "MeetingRepository",
    "SqlAlchemyUnitOfWork",
    "UserMeetingRepository",
    "sqlalchemy_uow",
]
