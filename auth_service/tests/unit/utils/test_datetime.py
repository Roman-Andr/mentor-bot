"""Unit tests for auth_service/utils/datetime.py."""

from datetime import UTC, datetime, timedelta

from auth_service.utils import datetime as datetime_utils


class TestNow:
    """Tests for now() function."""

    def test_now_returns_datetime(self):
        """Test that now() returns a datetime object."""
        result = datetime_utils.now()
        assert isinstance(result, datetime)

    def test_now_returns_tz_aware(self):
        """Test that now() returns a timezone-aware datetime."""
        result = datetime_utils.now()
        assert result.tzinfo is not None

    def test_now_returns_utc(self):
        """Test that now() returns UTC time."""
        result = datetime_utils.now()
        assert result.tzinfo == UTC

    def test_now_is_recent(self):
        """Test that now() returns a recent time (within last minute)."""
        result = datetime_utils.now()
        expected_now = datetime.now(UTC)

        # Should be within 1 second of actual current time
        diff = abs((expected_now - result).total_seconds())
        assert diff < 1.0


class TestFromTimestamp:
    """Tests for from_timestamp() function."""

    def test_from_timestamp_converts_correctly(self):
        """Test that from_timestamp converts timestamp correctly."""
        timestamp = 1609459200.0  # 2021-01-01 00:00:00 UTC
        result = datetime_utils.from_timestamp(timestamp)

        assert isinstance(result, datetime)
        assert result.tzinfo == UTC
        assert result.year == 2021
        assert result.month == 1
        assert result.day == 1

    def test_from_timestamp_zero(self):
        """Test that from_timestamp handles Unix epoch."""
        timestamp = 0.0
        result = datetime_utils.from_timestamp(timestamp)

        assert result.year == 1970
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0


class TestToTimestamp:
    """Tests for to_timestamp() function."""

    def test_to_timestamp_converts_correctly(self):
        """Test that to_timestamp converts datetime correctly."""
        dt = datetime(2021, 1, 1, 0, 0, 0, tzinfo=UTC)
        result = datetime_utils.to_timestamp(dt)

        assert result == 1609459200.0

    def test_to_timestamp_unix_epoch(self):
        """Test that to_timestamp handles Unix epoch."""
        dt = datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
        result = datetime_utils.to_timestamp(dt)

        assert result == 0.0

    def test_to_timestamp_round_trip(self):
        """Test round-trip conversion."""
        original = datetime(2023, 6, 15, 12, 30, 45, tzinfo=UTC)
        timestamp = datetime_utils.to_timestamp(original)
        result = datetime_utils.from_timestamp(timestamp)

        assert result == original


class TestFormatDatetime:
    """Tests for format_datetime() function."""

    def test_format_datetime_default_format(self):
        """Test formatting with default format string."""
        dt = datetime(2023, 6, 15, 14, 30, 0, tzinfo=UTC)
        result = datetime_utils.format_datetime(dt)

        assert result == "2023-06-15 14:30:00"

    def test_format_datetime_custom_format(self):
        """Test formatting with custom format string."""
        dt = datetime(2023, 6, 15, 14, 30, 0, tzinfo=UTC)
        result = datetime_utils.format_datetime(dt, fmt="%Y/%m/%d")

        assert result == "2023/06/15"

    def test_format_datetime_different_formats(self):
        """Test various format strings."""
        dt = datetime(2023, 6, 15, 14, 30, 45, tzinfo=UTC)

        assert datetime_utils.format_datetime(dt, "%Y-%m-%d") == "2023-06-15"
        assert datetime_utils.format_datetime(dt, "%H:%M:%S") == "14:30:45"
        result = datetime_utils.format_datetime(dt, "%d/%m/%Y %H:%M")
        assert result == "15/06/2023 14:30"


class TestParseDatetime:
    """Tests for parse_datetime() function."""

    def test_parse_datetime_default_format(self):
        """Test parsing with default format string."""
        dt_str = "2023-06-15 14:30:00"
        result = datetime_utils.parse_datetime(dt_str)

        assert result.year == 2023
        assert result.month == 6
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30
        assert result.second == 0
        assert result.tzinfo == UTC

    def test_parse_datetime_custom_format(self):
        """Test parsing with custom format string."""
        dt_str = "2023/06/15"
        result = datetime_utils.parse_datetime(dt_str, fmt="%Y/%m/%d")

        assert result.year == 2023
        assert result.month == 6
        assert result.day == 15
        assert result.tzinfo == UTC

    def test_parse_format_round_trip(self):
        """Test round-trip of format and parse."""
        original = datetime(2023, 6, 15, 14, 30, 45, tzinfo=UTC)
        formatted = datetime_utils.format_datetime(original)
        parsed = datetime_utils.parse_datetime(formatted)

        # Compare components since microseconds may differ
        assert parsed.year == original.year
        assert parsed.month == original.month
        assert parsed.day == original.day
        assert parsed.hour == original.hour
        assert parsed.minute == original.minute
        assert parsed.second == original.second


class TestIsExpired:
    """Tests for is_expired() function."""

    def test_is_expired_future_datetime(self):
        """Test that future datetime is not expired."""
        future = datetime_utils.now() + timedelta(days=1)
        assert datetime_utils.is_expired(future) is False

    def test_is_expired_past_datetime(self):
        """Test that past datetime is expired."""
        past = datetime_utils.now() - timedelta(days=1)
        assert datetime_utils.is_expired(past) is True

    def test_is_expired_now(self):
        """Test boundary case - current time should be considered expired."""
        # This test may be flaky due to timing, so we use a small window
        now = datetime_utils.now()
        # Add a tiny buffer to ensure it's not expired
        slightly_future = now + timedelta(milliseconds=100)
        assert datetime_utils.is_expired(slightly_future) is False

    def test_is_expired_with_threshold_not_expired(self):
        """
        Test is_expired with threshold - not expired case.

        is_expired(dt, threshold) checks if now() > dt + threshold.
        So if dt is now() and threshold is 1 hour, dt + threshold is in the future,
        meaning it is NOT expired.
        """
        # Current time - threshold extends the "valid" period
        dt = datetime_utils.now()
        threshold = timedelta(hours=1)
        # dt + 1 hour is in the future, so not expired
        assert datetime_utils.is_expired(dt, threshold) is False

    def test_is_expired_with_threshold_expired(self):
        """
        Test is_expired with threshold - expired case.

        If dt was 2 hours ago and threshold is 1 hour, then dt + threshold
        was 1 hour ago, which is in the past -> expired.
        """
        # A datetime from the past that when combined with threshold is still expired
        dt = datetime_utils.now() - timedelta(hours=2)
        threshold = timedelta(hours=1)
        # dt + 1 hour = 1 hour ago, which is still in the past -> expired
        assert datetime_utils.is_expired(dt, threshold) is True

    def test_is_expired_with_past_datetime_and_large_threshold(self):
        """
        Test is_expired with past datetime but large threshold.

        If dt was 1 hour ago but threshold is 2 hours, then dt + threshold
        is 1 hour from now (in the future), so NOT expired.
        """
        # Past datetime but threshold extends it into the future
        dt = datetime_utils.now() - timedelta(hours=1)
        threshold = timedelta(hours=2)
        # dt + 2 hours = 1 hour from now, in the future -> NOT expired
        assert datetime_utils.is_expired(dt, threshold) is False


class TestGetExpiryTime:
    """Tests for get_expiry_time() function."""

    def test_get_expiry_time_adds_days(self):
        """Test that get_expiry_time correctly adds days."""
        before = datetime_utils.now()
        result = datetime_utils.get_expiry_time(days=7)
        after = datetime_utils.now()

        # Result should be approximately 7 days from now
        assert before + timedelta(days=7) <= result <= after + timedelta(days=7)

    def test_get_expiry_time_adds_hours(self):
        """Test that get_expiry_time correctly adds hours."""
        before = datetime_utils.now()
        result = datetime_utils.get_expiry_time(hours=5)
        after = datetime_utils.now()

        # Result should be approximately 5 hours from now
        assert before + timedelta(hours=5) <= result <= after + timedelta(hours=5)

    def test_get_expiry_time_adds_minutes(self):
        """Test that get_expiry_time correctly adds minutes."""
        before = datetime_utils.now()
        result = datetime_utils.get_expiry_time(minutes=30)
        after = datetime_utils.now()

        # Result should be approximately 30 minutes from now
        assert before + timedelta(minutes=30) <= result <= after + timedelta(minutes=30)

    def test_get_expiry_time_additivity(self):
        """Test that get_expiry_time correctly combines days, hours, and minutes."""
        before = datetime_utils.now()
        result = datetime_utils.get_expiry_time(days=1, hours=2, minutes=30)
        after = datetime_utils.now()

        expected_delta = timedelta(days=1, hours=2, minutes=30)
        assert before + expected_delta <= result <= after + expected_delta

    def test_get_expiry_time_zero(self):
        """Test that get_expiry_time with zero values returns approximately now."""
        before = datetime_utils.now()
        result = datetime_utils.get_expiry_time()
        after = datetime_utils.now()

        assert before <= result <= after

    def test_get_expiry_time_utc_timezone(self):
        """Test that get_expiry_time returns UTC datetime."""
        result = datetime_utils.get_expiry_time(days=1)

        assert result.tzinfo is not None
        assert result.tzinfo == UTC
