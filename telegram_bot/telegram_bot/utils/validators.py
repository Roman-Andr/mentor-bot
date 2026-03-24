"""Validation utilities for user input."""

import re

MIN_TOKEN_LENGTH = 8
MAX_TOKEN_LENGTH = 64


def validate_invitation_token(token: str) -> bool:
    """Validate invitation token format."""
    if not token or len(token) < MIN_TOKEN_LENGTH or len(token) > MAX_TOKEN_LENGTH:
        return False

    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, token))
