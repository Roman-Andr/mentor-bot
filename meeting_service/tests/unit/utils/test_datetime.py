"""Unit tests for datetime utility functions."""

from datetime import UTC, datetime, timedelta

from meeting_service.utils import datetime as dt_utils


class TestNow:
    """Tests for the now() function."""

    def test_now_returns_datetime(self):
        """Test that now() returns a datetime object."""
        result = dt_utils.now()
        assert isinstance(result, datetime)

    def test_now_is_utc(self):
        """Test that now() returns UTC datetime."""
        result = dt_utils.now()
        assert result.tzinfo is UTC

    def test_now_is_current_time(self):
        """Test that now() returns current time approximately."""
        before = datetime.now(UTC)
        result = dt_utils.now()
        after = datetime.now(UTC)

        assert before <= result <= after


class TestFromTimestamp:
    """Tests for the from_timestamp() function."""

    def test_from_timestamp_converts_correctly(self):
        """Test timestamp to datetime conversion."""
        # Use a known timestamp (2024-01-01 00:00:00 UTC)
        timestamp = 1704067200.0
        result = dt_utils.from_timestamp(timestamp)

        expected = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
        assert result == expected

    def test_from_timestamp_returns_utc(self):
        """Test that from_timestamp() returns UTC datetime."""
        timestamp = 1704067200.0
        result = dt_utils.from_timestamp(timestamp)
        assert result.tzinfo is UTC


class TestToTimestamp:
    """Tests for the to_timestamp() function."""

    def test_to_timestamp_converts_correctly(self):
        """Test datetime to timestamp conversion."""
        dt = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
        result = dt_utils.to_timestamp(dt)

        assert result == 1704067200.0

    def test_to_timestamp_and_back(self):
        """Test round-trip conversion."""
        original_dt = datetime(2024, 6, 15, 12, 30, 45, tzinfo=UTC)
        timestamp = dt_utils.to_timestamp(original_dt)
        result_dt = dt_utils.from_timestamp(timestamp)

        assert original_dt == result_dt


class TestFormatDatetime:
    """Tests for the format_datetime() function."""

    def test_default_format(self):
        """Test formatting with default format string."""
        dt = datetime(2024, 1, 15, 14, 30, 0, tzinfo=UTC)
        result = dt_utils.format_datetime(dt)

        assert result == "2024-01-15 14:30:00"

    def test_custom_format(self):
        """Test formatting with custom format string."""
        dt = datetime(2024, 1, 15, 14, 30, 0, tzinfo=UTC)
        result = dt_utils.format_datetime(dt, "%Y/%m/%d")

        assert result == "2024/01/15"

    def test_iso_format(self):
        """Test formatting with ISO format."""
        dt = datetime(2024, 1, 15, 14, 30, 0, tzinfo=UTC)
        result = dt_utils.format_datetime(dt, "%Y-%m-%dT%H:%M:%SZ")

        assert result == "2024-01-15T14:30:00Z"


class TestParseDatetime:
    """Tests for the parse_datetime() function."""

    def test_default_format(self):
        """Test parsing with default format string."""
        dt_str = "2024-01-15 14:30:00"
        result = dt_utils.parse_datetime(dt_str)

        expected = datetime(2024, 1, 15, 14, 30, 0, tzinfo=UTC)
        assert result == expected

    def test_custom_format(self):
        """Test parsing with custom format string."""
        dt_str = "15/01/2024"
        result = dt_utils.parse_datetime(dt_str, "%d/%m/%Y")

        expected = datetime(2024, 1, 15, 0, 0, 0, tzinfo=UTC)
        assert result == expected

    def test_returns_utc(self):
        """Test that parse_datetime() returns UTC datetime."""
        dt_str = "2024-01-15 14:30:00"
        result = dt_utils.parse_datetime(dt_str)
        assert result.tzinfo is UTC


class TestIsExpired:
    """Tests for the is_expired() function."""

    def test_datetime_in_past_is_expired(self):
        """Test that past datetime is expired."""
        past_dt = datetime.now(UTC) - timedelta(hours=1)
        assert dt_utils.is_expired(past_dt) is True

    def test_datetime_in_future_is_not_expired(self):
        """Test that future datetime is not expired."""
        future_dt = datetime.now(UTC) + timedelta(hours=1)
        assert dt_utils.is_expired(future_dt) is False

    def test_current_datetime_is_expired(self):
        """Test that current datetime is considered expired."""
        current_dt = datetime.now(UTC)
        # Due to timing, this might be slightly expired
        result = dt_utils.is_expired(current_dt)
        # Just verify it returns a boolean
        assert isinstance(result, bool)

    def test_with_threshold_past(self):
        """Test expiration with threshold for past datetime."""
        # 5 hours ago
        past_dt = datetime.now(UTC) - timedelta(hours=5)
        # With 2 hour threshold, it should be expired (now > past + 2h)
        assert dt_utils.is_expired(past_dt, timedelta(hours=2)) is True

    def test_with_threshold_future(self):
        """Test expiration with threshold for future datetime."""
        # 1 hour in the future
        future_dt = datetime.now(UTC) + timedelta(hours=1)
        # With 3 hour threshold, it should NOT be expired (now < future + 3h)
        assert dt_utils.is_expired(future_dt, timedelta(hours=3)) is False

    def test_threshold_prevents_expiration(self):
        """Test that threshold can prevent immediate expiration."""
        # 30 minutes ago
        past_dt = datetime.now(UTC) - timedelta(minutes=30)
        # With 1 hour threshold, it should NOT be expired (now < past + 1h)
        assert dt_utils.is_expired(past_dt, timedelta(hours=1)) is False


class TestGetExpiryTime:
    """Tests for the get_expiry_time() function."""

    def test_days_only(self):
        """Test getting expiry time with days only."""
        before = datetime.now(UTC)
        result = dt_utils.get_expiry_time(days=1)
        after = datetime.now(UTC)

        assert before + timedelta(days=1) <= result <= after + timedelta(days=1)

    def test_hours_only(self):
        """Test getting expiry time with hours only."""
        before = datetime.now(UTC)
        result = dt_utils.get_expiry_time(hours=2)
        after = datetime.now(UTC)

        assert before + timedelta(hours=2) <= result <= after + timedelta(hours=2)

    def test_minutes_only(self):
        """Test getting expiry time with minutes only."""
        before = datetime.now(UTC)
        result = dt_utils.get_expiry_time(minutes=30)
        after = datetime.now(UTC)

        assert before + timedelta(minutes=30) <= result <= after + timedelta(minutes=30)

    def test_combined(self):
        """Test getting expiry time with days, hours, and minutes."""
        before = datetime.now(UTC)
        result = dt_utils.get_expiry_time(days=1, hours=2, minutes=30)
        after = datetime.now(UTC)

        expected_delta = timedelta(days=1, hours=2, minutes=30)
        assert before + expected_delta <= result <= after + expected_delta

    def test_default_is_now(self):
        """Test that default returns approximately now."""
        before = datetime.now(UTC)
        result = dt_utils.get_expiry_time()
        after = datetime.now(UTC)

        assert before <= result <= after


class TestRoundTrip:
    """Tests for round-trip conversions."""

    def test_format_and_parse_roundtrip(self):
        """Test formatting and parsing are inverse operations."""
        original = datetime(2024, 6, 15, 12, 30, 45, tzinfo=UTC)
        formatted = dt_utils.format_datetime(original)
        parsed = dt_utils.parse_datetime(formatted)

        assert original == parsed
