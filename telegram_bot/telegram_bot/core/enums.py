"""Enum definitions for the Telegram Bot."""

from enum import StrEnum


class ButtonStyle(StrEnum):
    """Button style enumeration for inline and reply keyboards."""

    DANGER = "danger"  # Red
    SUCCESS = "success"  # Green
    PRIMARY = "primary"  # Blue
    SECONDARY = "secondary"  # Gray
