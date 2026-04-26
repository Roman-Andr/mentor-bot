"""Unit tests for ExperienceRating model."""

from datetime import datetime, timezone

from feedback_service.models.experience_rating import _now


def test_now_returns_naive_utc_datetime():
    """Test that _now returns a naive UTC datetime."""
    result = _now()
    assert isinstance(result, datetime)
    assert result.tzinfo is None  # Should be naive
    # Check that it's close to current time (within 1 second)
    expected = datetime.now(timezone.utc).replace(tzinfo=None)
    assert abs((result - expected).total_seconds()) < 1
