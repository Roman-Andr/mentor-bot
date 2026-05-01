"""Enum definitions for the Meeting Service."""

from enum import StrEnum


class MeetingType(StrEnum):
    """Type of meeting."""

    HR = "HR"
    SECURITY = "SECURITY"
    TEAM = "TEAM"
    MANAGER = "MANAGER"
    OTHER = "OTHER"


class MeetingStatus(StrEnum):
    """Status of a user meeting."""

    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    MISSED = "MISSED"
    CANCELLED = "CANCELLED"


class MaterialType(StrEnum):
    """Type of meeting material."""

    PDF = "PDF"
    LINK = "LINK"
    DOC = "DOC"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


class EmployeeLevel(StrEnum):
    """Employee level enumeration (copied from auth for consistency)."""

    JUNIOR = "JUNIOR"
    MIDDLE = "MIDDLE"
    SENIOR = "SENIOR"
    LEAD = "LEAD"


class UserRole(StrEnum):
    """User role enumeration (copied from auth for consistency)."""

    EMPLOYEE = "EMPLOYEE"
    HR = "HR"
    ADMIN = "ADMIN"
