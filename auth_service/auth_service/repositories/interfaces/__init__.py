"""Repository interfaces following Interface Segregation Principle."""

from auth_service.repositories.interfaces.base import BaseRepository
from auth_service.repositories.interfaces.invitation import IInvitationRepository
from auth_service.repositories.interfaces.user import IUserRepository

__all__ = [
    "BaseRepository",
    "IInvitationRepository",
    "IUserRepository",
]
