"""Unit tests for telegram_bot/middlewares/throttling.py."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telegram_bot.middlewares.throttling import ThrottlingMiddleware


class TestThrottlingMiddlewareInit:
    """Test cases for ThrottlingMiddleware initialization."""

    def test_init_creates_user_limiters(self):
        """Test that initialization creates empty user_limiters dict."""
        middleware = ThrottlingMiddleware()

        assert hasattr(middleware, 'user_limiters')
        assert middleware.user_limiters == {}


class TestThrottlingMiddlewareCall:
    """Test cases for ThrottlingMiddleware.__call__ method."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.middleware = ThrottlingMiddleware()
        self.mock_handler = AsyncMock(return_value="handler_result")

    async def test_no_rate_limit_uses_default(self):
        """Test that default rate limit is used when no flag set."""
        mock_event = MagicMock()
        mock_event.message = MagicMock()
        mock_event.message.from_user = MagicMock()
        mock_event.message.from_user.id = 123456
        mock_event.callback_query = None

        data = {}

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = None  # No rate limit flag

            result = await self.middleware.__call__(self.mock_handler, mock_event, data)

            # Should call handler
            self.mock_handler.assert_called_once()
            assert result == "handler_result"

    async def test_rate_limit_not_exceeded(self):
        """Test handler is called when rate limit not exceeded."""
        mock_event = MagicMock()
        mock_event.message = MagicMock()
        mock_event.message.from_user = MagicMock()
        mock_event.message.from_user.id = 123456
        mock_event.callback_query = None

        data = {}

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 5, "period": 60}

            result = await self.middleware.__call__(self.mock_handler, mock_event, data)

            # User should be tracked
            assert 123456 in self.middleware.user_limiters

            # Handler should be called
            self.mock_handler.assert_called_once()
            assert result == "handler_result"

    async def test_rate_limit_exceeded(self):
        """Test throttling when rate limit exceeded."""
        mock_event = MagicMock()
        mock_event.message = MagicMock()
        mock_event.message.from_user = MagicMock()
        mock_event.message.from_user.id = 123456
        mock_event.callback_query = None
        mock_event.answer = AsyncMock()

        data = {}

        # Pre-populate user limiters with max calls
        now = datetime.now(UTC)
        self.middleware.user_limiters[123456] = [now, 5]  # 5 calls already made

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 5, "period": 60}

            result = await self.middleware.__call__(self.mock_handler, mock_event, data)

            # Handler should NOT be called
            self.mock_handler.assert_not_called()

            # Event.answer should be called with throttling message
            mock_event.answer.assert_called_once()
            call_args = mock_event.answer.call_args
            assert "Too many requests" in call_args[0][0]

            # Result should be None
            assert result is None

    async def test_rate_limit_exceeded_callback_query(self):
        """Test throttling for callback query events."""
        mock_event = MagicMock()
        mock_event.message = None
        mock_event.callback_query = MagicMock()
        mock_event.callback_query.from_user = MagicMock()
        mock_event.callback_query.from_user.id = 123456
        mock_event.answer = AsyncMock()

        data = {}

        # Pre-populate user limiters with max calls
        now = datetime.now(UTC)
        self.middleware.user_limiters[123456] = [now, 5]

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 5, "period": 60}

            result = await self.middleware.__call__(self.mock_handler, mock_event, data)

            self.mock_handler.assert_not_called()
            mock_event.answer.assert_called_once()

    async def test_rate_limit_reset_after_period(self):
        """Test rate limit resets after period expires."""
        mock_event = MagicMock()
        mock_event.message = MagicMock()
        mock_event.message.from_user = MagicMock()
        mock_event.message.from_user.id = 123456
        mock_event.callback_query = None

        data = {}

        # Pre-populate with old call (outside period)
        old_time = datetime.now(UTC) - timedelta(seconds=70)
        self.middleware.user_limiters[123456] = [old_time, 5]

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 5, "period": 60}

            result = await self.middleware.__call__(self.mock_handler, mock_event, data)

            # Handler should be called because period expired
            self.mock_handler.assert_called_once()

            # Counter should be reset to 1
            assert self.middleware.user_limiters[123456][1] == 1

    async def test_increment_call_count_within_period(self):
        """Test call count increments within rate limit period."""
        mock_event = MagicMock()
        mock_event.message = MagicMock()
        mock_event.message.from_user = MagicMock()
        mock_event.message.from_user.id = 123456
        mock_event.callback_query = None

        data = {}

        # Pre-populate with recent call
        now = datetime.now(UTC)
        self.middleware.user_limiters[123456] = [now, 2]

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 5, "period": 60}

            await self.middleware.__call__(self.mock_handler, mock_event, data)

            # Counter should be incremented
            assert self.middleware.user_limiters[123456][1] == 3

    async def test_no_user_in_event(self):
        """Test handling when event has no user."""
        mock_event = MagicMock()
        mock_event.message = None
        mock_event.callback_query = None

        data = {}

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 5, "period": 60}

            result = await self.middleware.__call__(self.mock_handler, mock_event, data)

            # Handler should be called even without user
            self.mock_handler.assert_called_once()
            assert result == "handler_result"

    async def test_custom_rate_limit(self):
        """Test custom rate limit from flag."""
        mock_event = MagicMock()
        mock_event.message = MagicMock()
        mock_event.message.from_user = MagicMock()
        mock_event.message.from_user.id = 123456
        mock_event.callback_query = None

        data = {}

        # Pre-populate with calls that would exceed default but not custom
        now = datetime.now(UTC)
        self.middleware.user_limiters[123456] = [now, 3]

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 10, "period": 120}

            result = await self.middleware.__call__(self.mock_handler, mock_event, data)

            # Handler should be called because 3 < 10
            self.mock_handler.assert_called_once()

    async def test_event_without_answer_method(self):
        """Test throttling when event has no answer method."""
        mock_event = MagicMock()
        mock_event.message = MagicMock()
        mock_event.message.from_user = MagicMock()
        mock_event.message.from_user.id = 123456
        mock_event.callback_query = None
        # Remove answer method
        del mock_event.answer

        data = {}

        # Pre-populate with max calls
        now = datetime.now(UTC)
        self.middleware.user_limiters[123456] = [now, 5]

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 5, "period": 60}

            # Should not raise AttributeError
            result = await self.middleware.__call__(self.mock_handler, mock_event, data)

            # Handler not called, but no answer sent
            self.mock_handler.assert_not_called()
            assert result is None


class TestCleanupOldLimiters:
    """Test cases for cleanup_old_limiters method."""

    def test_cleanup_removes_old_entries(self):
        """Test that old limiter entries are removed."""
        middleware = ThrottlingMiddleware()

        now = datetime.now(UTC)

        # Add entries
        middleware.user_limiters[1] = [now - timedelta(minutes=10), 5]  # Old
        middleware.user_limiters[2] = [now - timedelta(minutes=3), 3]    # Recent
        middleware.user_limiters[3] = [now - timedelta(minutes=1), 1]  # Very recent

        middleware.cleanup_old_limiters()

        # Only entry 1 should be removed (older than 5 minutes)
        assert 1 not in middleware.user_limiters
        assert 2 in middleware.user_limiters
        assert 3 in middleware.user_limiters

    def test_cleanup_empty_limiters(self):
        """Test cleanup with empty user_limiters."""
        middleware = ThrottlingMiddleware()

        # Should not raise
        middleware.cleanup_old_limiters()

        assert middleware.user_limiters == {}

    def test_cleanup_all_old_entries(self):
        """Test cleanup when all entries are old."""
        middleware = ThrottlingMiddleware()

        now = datetime.now(UTC)

        middleware.user_limiters[1] = [now - timedelta(minutes=6), 5]
        middleware.user_limiters[2] = [now - timedelta(minutes=7), 3]

        middleware.cleanup_old_limiters()

        assert middleware.user_limiters == {}

    def test_cleanup_no_old_entries(self):
        """Test cleanup when no entries are old."""
        middleware = ThrottlingMiddleware()

        now = datetime.now(UTC)

        middleware.user_limiters[1] = [now - timedelta(minutes=1), 5]
        middleware.user_limiters[2] = [now - timedelta(seconds=30), 3]

        middleware.cleanup_old_limiters()

        assert 1 in middleware.user_limiters
        assert 2 in middleware.user_limiters


class TestThrottlingIntegration:
    """Integration tests for throttling middleware."""

    async def test_multiple_users_tracked_separately(self):
        """Test that different users are tracked separately."""
        middleware = ThrottlingMiddleware()
        mock_handler = AsyncMock(return_value="result")

        # First user at limit
        middleware.user_limiters[1] = [datetime.now(UTC), 5]

        # Create events for different users
        event_user1 = MagicMock()
        event_user1.message = MagicMock()
        event_user1.message.from_user = MagicMock()
        event_user1.message.from_user.id = 1
        event_user1.callback_query = None
        event_user1.answer = AsyncMock()

        event_user2 = MagicMock()
        event_user2.message = MagicMock()
        event_user2.message.from_user = MagicMock()
        event_user2.message.from_user.id = 2
        event_user2.callback_query = None

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 5, "period": 60}

            # User 1 should be throttled
            result1 = await middleware.__call__(mock_handler, event_user1, {})
            assert result1 is None

            # User 2 should not be throttled
            result2 = await middleware.__call__(mock_handler, event_user2, {})
            assert result2 == "result"

    async def test_inline_query_user_extraction(self):
        """Test user extraction from inline query (though not explicitly handled)."""
        middleware = ThrottlingMiddleware()
        mock_handler = AsyncMock(return_value="result")

        # Event with only inline_query
        mock_event = MagicMock()
        mock_event.message = None
        mock_event.callback_query = None
        mock_event.inline_query = MagicMock()
        mock_event.inline_query.from_user = MagicMock()
        mock_event.inline_query.from_user.id = 123456

        with patch("telegram_bot.middlewares.throttling.get_flag") as mock_get_flag:
            mock_get_flag.return_value = {"calls": 5, "period": 60}

            result = await middleware.__call__(mock_handler, mock_event, {})

            # Handler should be called (no user extracted from inline_query)
            self.mock_handler = mock_handler
            self.mock_handler.assert_called_once()
