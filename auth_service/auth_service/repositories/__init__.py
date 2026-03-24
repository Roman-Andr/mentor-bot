"""Repository pattern implementation for data access layer."""

from auth_service.repositories.implementations import DepartmentRepository, InvitationRepository, UserRepository
from auth_service.repositories.interfaces import (
    BaseRepository,
    IDepartmentRepository,
    IInvitationRepository,
    IUserRepository,
)
from auth_service.repositories.unit_of_work import IUnitOfWork, SqlAlchemyUnitOfWork, sqlalchemy_uow

__all__ = [
    "BaseRepository",
    "DepartmentRepository",
    "IDepartmentRepository",
    "IInvitationRepository",
    "IUnitOfWork",
    "IUserRepository",
    "InvitationRepository",
    "SqlAlchemyUnitOfWork",
    "UserRepository",
    "sqlalchemy_uow",
]
