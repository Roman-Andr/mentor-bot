"""Enum definitions for the Auth Service."""

from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""

    NEWBIE = "NEWBIE"
    MENTOR = "MENTOR"
    HR = "HR"
    ADMIN = "ADMIN"


class InvitationStatus(str, Enum):
    """Invitation status enumeration."""

    PENDING = "PENDING"
    USED = "USED"
    REVOKED = "REVOKED"


class EmployeeLevel(str, Enum):
    """Employee level enumeration."""

    JUNIOR = "JUNIOR"
    MIDDLE = "MIDDLE"
    SENIOR = "SENIOR"
    LEAD = "LEAD"
