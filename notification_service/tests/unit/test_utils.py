"""Unit tests for notification_service/utils/ modules."""

from datetime import UTC, datetime, timedelta, timezone

import pytest

from notification_service.utils import (
    format_datetime,
    from_timestamp,
    get_expiry_time,
    is_expired,
    now,
    parse_datetime,
    to_timestamp,
)


class TestNow:
    """Tests for now() function."""

    def test_returns_datetime(self) -> None:
        """Returns a datetime object."""
        result = now()
        assert isinstance(result, datetime)

    def test_returns_utc_timezone(self) -> None:
        """Returns datetime with UTC timezone."""
        result = now()
        assert result.tzinfo is UTC

    def test_returns_current_time(self) -> None:
        """Returns time close to current time."""
        before = datetime.now(UTC)
        result = now()
        after = datetime.now(UTC)

        assert before <= result <= after


class TestFromTimestamp:
    """Tests for from_timestamp() function."""

    def test_converts_timestamp_to_datetime(self) -> None:
        """Converts timestamp to datetime."""
        timestamp = 1609459200.0  # 2021-01-01 00:00:00 UTC
        result = from_timestamp(timestamp)

        assert isinstance(result, datetime)
        assert result.year == 2021
        assert result.month == 1
        assert result.day == 1

    def test_returns_utc_timezone(self) -> None:
        """Returns datetime with UTC timezone."""
        result = from_timestamp(1609459200.0)
        assert result.tzinfo is UTC

    def test_handles_zero_timestamp(self) -> None:
        """Handles Unix epoch (0)."""
        result = from_timestamp(0.0)

        assert result.year == 1970
        assert result.month == 1
        assert result.day == 1

    def test_handles_negative_timestamp(self) -> None:
        """Handles timestamps before Unix epoch."""
        result = from_timestamp(-86400.0)  # 1969-12-31

        assert result.year == 1969
        assert result.month == 12
        assert result.day == 31


class TestToTimestamp:
    """Tests for to_timestamp() function."""

    def test_converts_datetime_to_timestamp(self) -> None:
        """Converts datetime to timestamp."""
        dt = datetime(2021, 1, 1, 0, 0, 0, tzinfo=UTC)
        result = to_timestamp(dt)

        assert result == 1609459200.0

    def test_handles_utc_datetime(self) -> None:
        """Handles UTC timezone correctly."""
        dt = datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
        result = to_timestamp(dt)

        assert result == 0.0

    def test_handles_different_timezones(self) -> None:
        """Converts different timezones correctly."""
        # Same moment in different timezone - 7pm EST on Jan 1 is midnight UTC on Jan 2
        est = timezone(timedelta(hours=-5))
        dt_est = datetime(2021, 1, 1, 19, 0, 0, tzinfo=est)  # 7pm EST = midnight UTC on Jan 2
        result = to_timestamp(dt_est)

        # Should equal the UTC timestamp for the same moment
        dt_utc = datetime(2021, 1, 2, 0, 0, 0, tzinfo=UTC)
        expected = to_timestamp(dt_utc)
        assert result == expected


class TestFormatDatetime:
    """Tests for format_datetime() function."""

    def test_formats_with_default_format(self) -> None:
        """Formats datetime with default format."""
        dt = datetime(2021, 6, 15, 14, 30, 45, tzinfo=UTC)
        result = format_datetime(dt)

        assert result == "2021-06-15 14:30:45"

    def test_formats_with_custom_format(self) -> None:
        """Formats datetime with custom format."""
        dt = datetime(2021, 6, 15, 14, 30, 45, tzinfo=UTC)
        result = format_datetime(dt, fmt="%Y/%m/%d")

        assert result == "2021/06/15"

    def test_formats_date_only(self) -> None:
        """Formats date only."""
        dt = datetime(2021, 12, 25, 0, 0, 0, tzinfo=UTC)
        result = format_datetime(dt, fmt="%Y-%m-%d")

        assert result == "2021-12-25"

    def test_formats_time_only(self) -> None:
        """Formats time only."""
        dt = datetime(2021, 1, 1, 23, 59, 59, tzinfo=UTC)
        result = format_datetime(dt, fmt="%H:%M:%S")

        assert result == "23:59:59"


class TestParseDatetime:
    """Tests for parse_datetime() function."""

    def test_parses_default_format(self) -> None:
        """Parses datetime with default format."""
        result = parse_datetime("2021-06-15 14:30:45")

        assert isinstance(result, datetime)
        assert result.year == 2021
        assert result.month == 6
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30
        assert result.second == 45

    def test_returns_utc_timezone(self) -> None:
        """Returns datetime with UTC timezone."""
        result = parse_datetime("2021-06-15 14:30:45")

        assert result.tzinfo is UTC

    def test_parses_custom_format(self) -> None:
        """Parses datetime with custom format."""
        result = parse_datetime("15/06/2021", fmt="%d/%m/%Y")

        assert result.year == 2021
        assert result.month == 6
        assert result.day == 15

    def test_parses_iso_format(self) -> None:
        """Parses ISO format datetime."""
        result = parse_datetime("2021-06-15T14:30:45", fmt="%Y-%m-%dT%H:%M:%S")

        assert result.year == 2021
        assert result.hour == 14


class TestIsExpired:
    """Tests for is_expired() function."""

    def test_returns_true_for_past_datetime(self) -> None:
        """Returns True for datetime in the past."""
        past_dt = datetime.now(UTC) - timedelta(hours=1)
        result = is_expired(past_dt)

        assert result is True

    def test_returns_false_for_future_datetime(self) -> None:
        """Returns False for datetime in the future."""
        future_dt = datetime.now(UTC) + timedelta(hours=1)
        result = is_expired(future_dt)

        assert result is False

    def test_with_threshold_expired(self) -> None:
        """Returns True when now > dt + threshold."""
        dt = datetime.now(UTC) - timedelta(hours=2)
        threshold = timedelta(hours=1)
        result = is_expired(dt, threshold)

        assert result is True

    def test_with_threshold_not_expired(self) -> None:
        """Returns False when now < dt + threshold."""
        dt = datetime.now(UTC) - timedelta(minutes=30)
        threshold = timedelta(hours=1)
        result = is_expired(dt, threshold)

        assert result is False

    def test_without_threshold_expired(self) -> None:
        """Returns True when now > dt without threshold."""
        past_dt = datetime.now(UTC) - timedelta(seconds=1)
        result = is_expired(past_dt)

        assert result is True


class TestGetExpiryTime:
    """Tests for get_expiry_time() function."""

    def test_returns_future_datetime(self) -> None:
        """Returns datetime in the future."""
        before = datetime.now(UTC)
        result = get_expiry_time()
        after = datetime.now(UTC)

        assert before <= result

    def test_with_days(self) -> None:
        """Returns datetime days in the future."""
        now_dt = datetime.now(UTC)
        result = get_expiry_time(days=1)

        # Should be approximately 1 day in the future
        diff = result - now_dt
        assert timedelta(hours=23) < diff < timedelta(hours=25)

    def test_with_hours(self) -> None:
        """Returns datetime hours in the future."""
        now_dt = datetime.now(UTC)
        result = get_expiry_time(hours=2)

        diff = result - now_dt
        assert timedelta(hours=1, minutes=59) < diff < timedelta(hours=2, minutes=1)

    def test_with_minutes(self) -> None:
        """Returns datetime minutes in the future."""
        now_dt = datetime.now(UTC)
        result = get_expiry_time(minutes=30)

        diff = result - now_dt
        assert timedelta(minutes=29, seconds=59) < diff < timedelta(minutes=30, seconds=1)

    def test_with_combined_parameters(self) -> None:
        """Returns datetime with combined days, hours, minutes."""
        now_dt = datetime.now(UTC)
        result = get_expiry_time(days=1, hours=2, minutes=30)

        diff = result - now_dt
        expected = timedelta(days=1, hours=2, minutes=30)
        # Allow 1 second tolerance
        assert expected - timedelta(seconds=1) < diff < expected + timedelta(seconds=1)

    def test_returns_utc_timezone(self) -> None:
        """Returns datetime with UTC timezone."""
        result = get_expiry_time()

        assert result.tzinfo is UTC


class TestUtilsExports:
    """Tests for utils/__init__.py exports."""

    def test_all_functions_exported(self) -> None:
        """All utility functions are exported from utils package."""
        # These should all be importable from utils
        assert callable(now)
        assert callable(from_timestamp)
        assert callable(to_timestamp)
        assert callable(format_datetime)
        assert callable(parse_datetime)
        assert callable(is_expired)
        assert callable(get_expiry_time)
