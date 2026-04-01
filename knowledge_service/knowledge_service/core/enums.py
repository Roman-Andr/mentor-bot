"""Enum definitions for the Knowledge Service."""

from enum import Enum


class ArticleStatus(str, Enum):
    """Article status enumeration."""

    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class AttachmentType(str, Enum):
    """Attachment type enumeration."""

    FILE = "FILE"
    LINK = "LINK"
    EMBED = "EMBED"


class EmployeeLevel(str, Enum):
    """Employee level enumeration."""

    JUNIOR = "JUNIOR"
    MIDDLE = "MIDDLE"
    SENIOR = "SENIOR"
    LEAD = "LEAD"


class SearchSortBy(str, Enum):
    """Search result sorting options."""

    RELEVANCE = "RELEVANCE"
    DATE_NEWEST = "DATE_NEWEST"
    DATE_OLDEST = "DATE_OLDEST"
    VIEWS = "VIEWS"
    TITLE = "TITLE"


class DialogueCategory(str, Enum):
    """Dialogue scenario category."""

    VACATION = "VACATION"
    ACCESS = "ACCESS"
    BENEFITS = "BENEFITS"
    CONTACTS = "CONTACTS"
    WORKTIME = "WORKTIME"


class DialogueAnswerType(str, Enum):
    """Dialogue step answer type."""

    TEXT = "TEXT"
    CHOICE = "CHOICE"
    LINK = "LINK"
