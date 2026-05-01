"""Enum definitions for the Feedback Service."""

from enum import StrEnum


class UserRole(StrEnum):
    """User role enumeration."""

    NEWBIE = "NEWBIE"
    MENTOR = "MENTOR"
    HR = "HR"
    ADMIN = "ADMIN"
