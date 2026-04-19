"""Enum definitions for the Auth Service."""

from enum import StrEnum


class UserRole(StrEnum):
    """User role enumeration."""

    NEWBIE = "NEWBIE"
    MENTOR = "MENTOR"
    HR = "HR"
    ADMIN = "ADMIN"


class InvitationStatus(StrEnum):
    """Invitation status enumeration."""

    PENDING = "PENDING"
    USED = "USED"
    REVOKED = "REVOKED"


class EmployeeLevel(StrEnum):
    """Employee level enumeration."""

    JUNIOR = "JUNIOR"
    MIDDLE = "MIDDLE"
    SENIOR = "SENIOR"
    LEAD = "LEAD"
