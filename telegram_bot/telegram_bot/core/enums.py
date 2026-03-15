"""Enum definitions for the Telegram Bot."""

from enum import Enum


class ButtonStyle(str, Enum):
    """Button style enumeration for inline and reply keyboards."""

    DANGER = "danger"  # Red
    SUCCESS = "success"  # Green
    PRIMARY = "primary"  # Blue
