"""Enum definitions for the Checklists Service."""

from enum import StrEnum


class TaskCategory(StrEnum):
    """Task category enumeration."""

    DOCUMENTATION = "DOCUMENTATION"
    INTRODUCTION = "INTRODUCTION"
    TECHNICAL = "TECHNICAL"
    TRAINING = "TRAINING"
    MEETING = "MEETING"
    PAPERWORK = "PAPERWORK"
    SECURITY = "SECURITY"
    HR = "HR"
    OTHER = "OTHER"


class Status(StrEnum):
    """Base status enumeration."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"


TaskStatus = Status
ChecklistStatus = Status


class TemplateStatus(StrEnum):
    """Template status enumeration."""

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DEPRECATED = "DEPRECATED"


class EmployeeLevel(StrEnum):
    """Employee level enumeration."""

    JUNIOR = "JUNIOR"
    MIDDLE = "MIDDLE"
    SENIOR = "SENIOR"
    LEAD = "LEAD"
