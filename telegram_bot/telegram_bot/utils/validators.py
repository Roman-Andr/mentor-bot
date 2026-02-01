"""Validation utilities for user input."""

import re


def validate_invitation_token(token: str) -> bool:
    """Validate invitation token format."""
    if not token or len(token) < 8 or len(token) > 64:
        return False

    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, token))
