"""Security utilities for file validation and sanitization."""

import os
import re
import time
from hashlib import md5
from pathlib import Path

from knowledge_service.config import settings


def validate_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal."""
    # Remove any directory components
    filename = Path(filename).name

    # Remove any non-alphanumeric characters except dots and hyphens
    sanitized = re.sub(r"[^\w\s\.\-]", "", filename)

    # Replace spaces with underscores
    sanitized = sanitized.replace(" ", "_")

    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[: 255 - len(ext)] + ext

    return sanitized


def validate_file_size(file_size: int) -> bool:
    """Validate file size against maximum allowed."""
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes
    return file_size <= max_size


def validate_file_type(filename: str) -> bool:
    """Validate file extension against allowed types."""
    if not filename:
        return False

    ext = Path(filename).suffix.lower().lstrip(".")
    return ext in settings.ALLOWED_FILE_TYPES


def sanitize_html(content: str) -> str:
    """Sanitize HTML content to prevent XSS attacks."""
    # Basic sanitization - in production use a proper HTML sanitizer like bleach
    # For now, we'll just strip script tags and dangerous attributes
    content = re.sub(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", "", content, flags=re.IGNORECASE)
    content = re.sub(r"on\w+\s*=", "", content, flags=re.IGNORECASE)
    return re.sub(r"javascript:", "", content, flags=re.IGNORECASE)



def generate_secure_filename(filename: str, user_id: int) -> str:
    """Generate secure filename with timestamp and user ID."""
    _name, ext = os.path.splitext(filename)
    timestamp = int(time.time())

    # Create hash for uniqueness
    hash_input = f"{filename}{user_id}{timestamp}"
    file_hash = md5(hash_input.encode()).hexdigest()[:8]

    return f"{user_id}_{timestamp}_{file_hash}{ext}"
