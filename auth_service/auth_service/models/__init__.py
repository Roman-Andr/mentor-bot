"""Models package for the Auth Service."""

from auth_service.models.department import Department
from auth_service.models.invitation import Invitation
from auth_service.models.user import User
from auth_service.models.user_mentor import UserMentor

__all__ = [
    "Department",
    "Invitation",
    "User",
    "UserMentor",
]
