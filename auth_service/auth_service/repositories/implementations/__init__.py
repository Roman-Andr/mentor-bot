"""SQLAlchemy implementations of repository interfaces."""

from auth_service.repositories.implementations.department import DepartmentRepository
from auth_service.repositories.implementations.invitation import InvitationRepository
from auth_service.repositories.implementations.invitation_status_history import InvitationStatusHistoryRepository
from auth_service.repositories.implementations.login_history import LoginHistoryRepository
from auth_service.repositories.implementations.mentor_assignment_history import MentorAssignmentHistoryRepository
from auth_service.repositories.implementations.password_change_history import PasswordChangeHistoryRepository
from auth_service.repositories.implementations.role_change_history import RoleChangeHistoryRepository
from auth_service.repositories.implementations.user import UserRepository

__all__ = [
    "DepartmentRepository",
    "InvitationRepository",
    "InvitationStatusHistoryRepository",
    "LoginHistoryRepository",
    "MentorAssignmentHistoryRepository",
    "PasswordChangeHistoryRepository",
    "RoleChangeHistoryRepository",
    "UserRepository",
]
