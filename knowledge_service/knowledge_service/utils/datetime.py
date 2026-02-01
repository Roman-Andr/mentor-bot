"""Date and time utility functions."""

from datetime import UTC, datetime, timedelta


def now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(UTC)


def from_timestamp(timestamp: float) -> datetime:
    """Convert timestamp to datetime."""
    return datetime.fromtimestamp(timestamp, UTC)


def to_timestamp(dt: datetime) -> float:
    """Convert datetime to timestamp."""
    return dt.timestamp()


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    return dt.strftime(fmt)


def parse_datetime(dt_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse string to datetime."""
    return datetime.strptime(dt_str, fmt).replace(tzinfo=UTC)


def is_expired(dt: datetime, threshold: timedelta | None = None) -> bool:
    """Check if datetime is expired."""
    if threshold:
        return now() > dt + threshold
    return now() > dt


def get_expiry_time(days: int = 0, hours: int = 0, minutes: int = 0) -> datetime:
    """Get expiry datetime from now."""
    return now() + timedelta(days=days, hours=hours, minutes=minutes)
