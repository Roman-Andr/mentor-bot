"""Tests for datetime utilities."""

from datetime import UTC, datetime, timedelta

from checklists_service.utils.datetime import (
    format_datetime,
    from_timestamp,
    get_expiry_time,
    is_expired,
    now,
    parse_datetime,
    to_timestamp,
)
from freezegun import freeze_time

YEAR_2024 = 2024
MONTH_6 = 6
DAY_15 = 15
HOUR_12 = 12
MINUTE_30 = 30
SECOND_45 = 45
TS_1718454645 = 1718454645
DAYS_7 = 7
HOURS_5 = 5
MINUTES_30 = 30
DAYS_1 = 1
HOURS_2 = 2
MINUTES_30_2 = 30


class TestNow:
    """Tests for now() function."""

    @freeze_time("2024-06-15 12:30:45")
    def test_now_returns_utc_datetime(self) -> None:
        """now() returns tz-aware UTC datetime."""
        result = now()

        assert result.tzinfo == UTC
        assert result.year == YEAR_2024
        assert result.month == MONTH_6
        assert result.day == DAY_15
        assert result.hour == HOUR_12
        assert result.minute == MINUTE_30
        assert result.second == SECOND_45


class TestTimestampConversion:
    """Tests for timestamp conversion functions."""

    def test_from_timestamp(self) -> None:
        """from_timestamp() converts timestamp to UTC datetime."""
        # Unix epoch
        result = from_timestamp(0)
        assert result == datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)

        # Known timestamp: 2024-06-15 12:30:45 UTC
        ts = TS_1718454645
        result = from_timestamp(ts)
        assert result == datetime(YEAR_2024, MONTH_6, DAY_15, HOUR_12, MINUTE_30, SECOND_45, tzinfo=UTC)

    def test_to_timestamp(self) -> None:
        """to_timestamp() converts UTC datetime to timestamp."""
        dt = datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
        result = to_timestamp(dt)
        assert result == 0

        dt = datetime(YEAR_2024, MONTH_6, DAY_15, HOUR_12, MINUTE_30, SECOND_45, tzinfo=UTC)
        result = to_timestamp(dt)
        assert result == TS_1718454645

    def test_round_trip(self) -> None:
        """from_timestamp and to_timestamp are inverse operations."""
        original_ts = TS_1718454645
        dt = from_timestamp(original_ts)
        recovered_ts = to_timestamp(dt)
        assert recovered_ts == original_ts

    def test_round_trip_datetime(self) -> None:
        """to_timestamp and from_timestamp are inverse operations for datetime."""
        original_dt = datetime(YEAR_2024, MONTH_6, DAY_15, HOUR_12, MINUTE_30, SECOND_45, tzinfo=UTC)
        ts = to_timestamp(original_dt)
        recovered_dt = from_timestamp(ts)
        assert recovered_dt == original_dt


class TestFormatAndParse:
    """Tests for format_datetime and parse_datetime."""

    def test_format_datetime_default_format(self) -> None:
        """format_datetime() uses default format YYYY-MM-DD HH:MM:SS."""
        dt = datetime(YEAR_2024, MONTH_6, DAY_15, HOUR_12, MINUTE_30, SECOND_45, tzinfo=UTC)
        result = format_datetime(dt)
        assert result == "2024-06-15 12:30:45"

    def test_format_datetime_custom_format(self) -> None:
        """format_datetime() accepts custom format string."""
        dt = datetime(YEAR_2024, MONTH_6, DAY_15, HOUR_12, MINUTE_30, SECOND_45, tzinfo=UTC)
        result = format_datetime(dt, fmt="%d/%m/%Y")
        assert result == "15/06/2024"

    def test_parse_datetime_default_format(self) -> None:
        """parse_datetime() uses default format YYYY-MM-DD HH:MM:SS."""
        result = parse_datetime("2024-06-15 12:30:45")
        assert result == datetime(YEAR_2024, MONTH_6, DAY_15, HOUR_12, MINUTE_30, SECOND_45, tzinfo=UTC)

    def test_parse_datetime_custom_format(self) -> None:
        """parse_datetime() accepts custom format string."""
        result = parse_datetime("15/06/2024", fmt="%d/%m/%Y")
        assert result == datetime(YEAR_2024, MONTH_6, DAY_15, 0, 0, 0, tzinfo=UTC)

    def test_round_trip(self) -> None:
        """format_datetime and parse_datetime are inverse operations."""
        original_dt = datetime(YEAR_2024, MONTH_6, DAY_15, HOUR_12, MINUTE_30, SECOND_45, tzinfo=UTC)
        formatted = format_datetime(original_dt)
        recovered_dt = parse_datetime(formatted)
        assert recovered_dt == original_dt


class TestIsExpired:
    """Tests for is_expired function."""

    @freeze_time("2024-06-15 12:00:00")
    def test_is_expired_without_threshold_true(self) -> None:
        """is_expired() returns True when dt is in the past."""
        past_dt = datetime(YEAR_2024, MONTH_6, DAY_15, 11, 59, 59, tzinfo=UTC)
        assert is_expired(past_dt) is True

    @freeze_time("2024-06-15 12:00:00")
    def test_is_expired_without_threshold_false(self) -> None:
        """is_expired() returns False when dt is in the future."""
        future_dt = datetime(YEAR_2024, MONTH_6, DAY_15, 12, 0, 1, tzinfo=UTC)
        assert is_expired(future_dt) is False

    @freeze_time("2024-06-15 12:00:00")
    def test_is_expired_at_boundary(self) -> None:
        """is_expired() returns False when dt equals now()."""
        current_dt = datetime(YEAR_2024, MONTH_6, DAY_15, HOUR_12, 0, 0, tzinfo=UTC)
        assert is_expired(current_dt) is False

    @freeze_time("2024-06-15 12:00:00")
    def test_is_expired_with_threshold_true(self) -> None:
        """is_expired() with threshold returns True when now > dt + threshold."""
        dt = datetime(YEAR_2024, MONTH_6, DAY_15, 11, 55, 0, tzinfo=UTC)
        threshold = timedelta(minutes=4)  # Expires at 11:59:00
        assert is_expired(dt, threshold) is True

    @freeze_time("2024-06-15 12:00:00")
    def test_is_expired_with_threshold_false(self) -> None:
        """is_expired() with threshold returns False when now < dt + threshold."""
        dt = datetime(YEAR_2024, MONTH_6, DAY_15, 11, 55, 0, tzinfo=UTC)
        threshold = timedelta(minutes=6)  # Expires at 12:01:00
        assert is_expired(dt, threshold) is False


class TestGetExpiryTime:
    """Tests for get_expiry_time function."""

    @freeze_time("2024-06-15 12:00:00")
    def test_get_expiry_time_days(self) -> None:
        """get_expiry_time() adds days correctly."""
        result = get_expiry_time(days=DAYS_7)
        assert result == datetime(YEAR_2024, 6, 22, HOUR_12, 0, 0, tzinfo=UTC)

    @freeze_time("2024-06-15 12:00:00")
    def test_get_expiry_time_hours(self) -> None:
        """get_expiry_time() adds hours correctly."""
        result = get_expiry_time(hours=HOURS_5)
        assert result == datetime(YEAR_2024, MONTH_6, DAY_15, 17, 0, 0, tzinfo=UTC)

    @freeze_time("2024-06-15 12:00:00")
    def test_get_expiry_time_minutes(self) -> None:
        """get_expiry_time() adds minutes correctly."""
        result = get_expiry_time(minutes=MINUTES_30)
        assert result == datetime(YEAR_2024, MONTH_6, DAY_15, HOUR_12, MINUTE_30, 0, tzinfo=UTC)

    @freeze_time("2024-06-15 12:00:00")
    def test_get_expiry_time_combined(self) -> None:
        """get_expiry_time() adds days, hours, and minutes together."""
        result = get_expiry_time(days=DAYS_1, hours=HOURS_2, minutes=MINUTES_30_2)
        assert result == datetime(YEAR_2024, 6, 16, 14, MINUTE_30, 0, tzinfo=UTC)

    @freeze_time("2024-06-15 12:00:00")
    def test_get_expiry_time_zero(self) -> None:
        """get_expiry_time() with zero values returns now()."""
        result = get_expiry_time()
        assert result == datetime(YEAR_2024, MONTH_6, DAY_15, HOUR_12, 0, 0, tzinfo=UTC)
