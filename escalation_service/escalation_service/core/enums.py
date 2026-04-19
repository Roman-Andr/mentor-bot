"""Enum definitions for the Escalation Service."""

from enum import StrEnum


class EscalationType(StrEnum):
    """Type of escalation request."""

    HR = "HR"
    MENTOR = "MENTOR"
    IT = "IT"
    GENERAL = "GENERAL"  # fallback if no specific assignee


class EscalationStatus(StrEnum):
    """Status of an escalation request."""

    PENDING = "PENDING"  # not yet assigned
    ASSIGNED = "ASSIGNED"  # assigned to someone, not started
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"


class EscalationSource(StrEnum):
    """How the escalation was triggered."""

    MANUAL = "MANUAL"  # user explicitly asked for help
    AUTO_OVERDUE = "AUTO_OVERDUE"  # task overdue > 3 days
    AUTO_SEARCH_FAILED = "AUTO_SEARCH_FAILED"  # two consecutive failed searches
    AUTO_NO_ANSWER = "AUTO_NO_ANSWER"  # "answer not found" clicked
