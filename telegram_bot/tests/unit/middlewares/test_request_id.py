"""Unit tests for telegram_bot RequestIDMiddleware."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from telegram_bot.middlewares.request_id import RequestIDMiddleware
from telegram_bot.utils.logging import request_id_var


class TestRequestIDMiddleware:
    """Tests for RequestIDMiddleware.__call__."""

    @pytest.mark.asyncio
    async def test_sets_request_id_var_for_message_event(self) -> None:
        """Sets request_id_var for the duration of the handler call."""
        middleware = RequestIDMiddleware()
        captured: dict[str, str | None] = {}

        event = MagicMock()
        event.message_id = 42

        async def handler(evt: object, data: dict) -> str:
            captured["rid"] = request_id_var.get()
            return "ok"

        result = await middleware(handler, event, {})

        assert result == "ok"
        assert captured["rid"] is not None
        assert len(captured["rid"]) == 32
        assert request_id_var.get() is None

    @pytest.mark.asyncio
    async def test_uses_callback_id_when_no_message_id(self) -> None:
        """Uses event.id (CallbackQuery) when message_id is missing."""
        middleware = RequestIDMiddleware()

        event = MagicMock(spec=["id"])  # no message_id attribute
        event.id = "cb-id"

        handler = AsyncMock(return_value="handled")

        result = await middleware(handler, event, {})

        assert result == "handled"
        handler.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_resets_context_var_when_handler_raises(self) -> None:
        """request_id_var is reset even if handler raises."""
        middleware = RequestIDMiddleware()
        event = MagicMock()
        event.message_id = 1

        async def boom(_evt: object, _data: dict) -> str:
            raise RuntimeError("boom")

        with pytest.raises(RuntimeError):
            await middleware(boom, event, {})

        assert request_id_var.get() is None
