"""Enum definitions for the Meeting Service."""

from enum import Enum


class MeetingType(str, Enum):
    """Type of meeting."""

    HR = "HR"
    SECURITY = "SECURITY"
    TEAM = "TEAM"
    MANAGER = "MANAGER"
    OTHER = "OTHER"


class MeetingStatus(str, Enum):
    """Status of a user meeting."""

    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    MISSED = "MISSED"
    CANCELLED = "CANCELLED"


class MaterialType(str, Enum):
    """Type of meeting material."""

    PDF = "PDF"
    LINK = "LINK"
    DOC = "DOC"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


class EmployeeLevel(str, Enum):
    """Employee level enumeration (copied from auth for consistency)."""

    JUNIOR = "JUNIOR"
    MIDDLE = "MIDDLE"
    SENIOR = "SENIOR"
    LEAD = "LEAD"
