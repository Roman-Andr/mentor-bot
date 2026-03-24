"""Repository interfaces following Interface Segregation Principle."""

from auth_service.repositories.interfaces.base import BaseRepository
from auth_service.repositories.interfaces.department import IDepartmentRepository
from auth_service.repositories.interfaces.invitation import IInvitationRepository
from auth_service.repositories.interfaces.user import IUserRepository

__all__ = [
    "BaseRepository",
    "IDepartmentRepository",
    "IInvitationRepository",
    "IUserRepository",
]
