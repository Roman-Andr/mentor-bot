"""Enum definitions for the Knowledge Service."""

from enum import StrEnum


class UserRole(StrEnum):
    """User role enumeration."""

    HR = "HR"
    ADMIN = "ADMIN"
    MENTOR = "MENTOR"
    EMPLOYEE = "EMPLOYEE"


class ArticleStatus(StrEnum):
    """Article status enumeration."""

    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class AttachmentType(StrEnum):
    """Attachment type enumeration."""

    FILE = "FILE"
    LINK = "LINK"
    EMBED = "EMBED"


class EmployeeLevel(StrEnum):
    """Employee level enumeration."""

    JUNIOR = "JUNIOR"
    MIDDLE = "MIDDLE"
    SENIOR = "SENIOR"
    LEAD = "LEAD"


class SearchSortBy(StrEnum):
    """Search result sorting options."""

    RELEVANCE = "RELEVANCE"
    DATE_NEWEST = "DATE_NEWEST"
    DATE_OLDEST = "DATE_OLDEST"
    VIEWS = "VIEWS"
    TITLE = "TITLE"


class DialogueCategory(StrEnum):
    """Dialogue scenario category."""

    VACATION = "VACATION"
    ACCESS = "ACCESS"
    BENEFITS = "BENEFITS"
    CONTACTS = "CONTACTS"
    WORKTIME = "WORKTIME"


class DialogueAnswerType(StrEnum):
    """Dialogue step answer type."""

    TEXT = "TEXT"
    CHOICE = "CHOICE"
    LINK = "LINK"
