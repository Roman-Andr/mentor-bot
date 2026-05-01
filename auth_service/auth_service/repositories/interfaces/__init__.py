"""Repository interfaces following Interface Segregation Principle."""

from auth_service.repositories.interfaces.base import BaseRepository
from auth_service.repositories.interfaces.department import IDepartmentRepository
from auth_service.repositories.interfaces.invitation import IInvitationRepository
from auth_service.repositories.interfaces.invitation_status_history import IInvitationStatusHistoryRepository
from auth_service.repositories.interfaces.login_history import ILoginHistoryRepository
from auth_service.repositories.interfaces.mentor_assignment_history import IMentorAssignmentHistoryRepository
from auth_service.repositories.interfaces.password_change_history import IPasswordChangeHistoryRepository
from auth_service.repositories.interfaces.role_change_history import IRoleChangeHistoryRepository
from auth_service.repositories.interfaces.user import IUserRepository
from auth_service.repositories.interfaces.user_mentor import IUserMentorRepository

__all__ = [
    "BaseRepository",
    "IDepartmentRepository",
    "IInvitationRepository",
    "IInvitationStatusHistoryRepository",
    "ILoginHistoryRepository",
    "IMentorAssignmentHistoryRepository",
    "IPasswordChangeHistoryRepository",
    "IRoleChangeHistoryRepository",
    "IUserMentorRepository",
    "IUserRepository",
]
