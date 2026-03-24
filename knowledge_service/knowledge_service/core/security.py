"""Security utilities for file validation and sanitization."""

import re
import time
from hashlib import sha256
from pathlib import Path

from knowledge_service.config import settings

MAX_FILENAME_LENGTH = 255


def validate_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal."""
    filename = Path(filename).name
    sanitized = re.sub(r"[^\w\s\.\-]", "", filename)
    sanitized = sanitized.replace(" ", "_")

    if len(sanitized) > MAX_FILENAME_LENGTH:
        path = Path(sanitized)
        sanitized = path.stem[: MAX_FILENAME_LENGTH - len(path.suffix)] + path.suffix

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
    timestamp = int(time.time())
    _name, ext = Path(filename).stem, Path(filename).suffix

    # Create hash for uniqueness
    hash_input = f"{filename}{user_id}{timestamp}"
    file_hash = sha256(hash_input.encode()).hexdigest()[:8]

    return f"{user_id}_{timestamp}_{file_hash}{ext}"
