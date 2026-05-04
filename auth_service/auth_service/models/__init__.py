"""Models package for the Auth Service."""

from auth_service.models.department import Department
from auth_service.models.invitation import Invitation
from auth_service.models.invitation_status_history import InvitationStatusHistory
from auth_service.models.login_history import LoginHistory
from auth_service.models.logout_history import LogoutHistory
from auth_service.models.mentor_assignment_history import MentorAssignmentHistory
from auth_service.models.password_change_history import PasswordChangeHistory
from auth_service.models.password_reset import PasswordResetToken
from auth_service.models.role_change_history import RoleChangeHistory
from auth_service.models.user import User
from auth_service.models.user_mentor import UserMentor

__all__ = [
    "Department",
    "Invitation",
    "InvitationStatusHistory",
    "LoginHistory",
    "LogoutHistory",
    "MentorAssignmentHistory",
    "PasswordChangeHistory",
    "PasswordResetToken",
    "RoleChangeHistory",
    "User",
    "UserMentor",
]
