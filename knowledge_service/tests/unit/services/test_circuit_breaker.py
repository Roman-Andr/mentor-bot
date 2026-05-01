"""Tests for circuit breaker implementation."""

import time
from unittest.mock import AsyncMock

import httpx
import pytest
from knowledge_service.services.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
    auth_service_circuit_breaker,
)


class TestCircuitBreakerClosedToOpen:
    """Test CLOSED -> OPEN transition after N failures."""

    async def test_closed_state_allows_calls(self) -> None:
        """Circuit breaker starts in CLOSED state and allows calls."""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        assert cb.state == CircuitState.CLOSED

        mock_func = AsyncMock(return_value="success")
        result = await cb.call(mock_func, "arg1", kwarg1="value1")

        assert result == "success"
        mock_func.assert_called_once_with("arg1", kwarg1="value1")

    async def test_closed_to_open_after_failure_threshold(self) -> None:
        """CLOSED -> OPEN after failure_threshold failures."""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60, expected_exceptions=(ValueError,))

        mock_func = AsyncMock(side_effect=ValueError("failure"))

        # First 2 failures - should stay CLOSED
        for _ in range(2):
            with pytest.raises(ValueError, match="failure"):
                await cb.call(mock_func)
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 2

        # 3rd failure - should transition to OPEN
        with pytest.raises(ValueError, match="failure"):
            await cb.call(mock_func)
        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 3

    async def test_open_rejects_calls_immediately(self) -> None:
        """OPEN state rejects calls with CircuitBreakerOpenError."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60, expected_exceptions=(ValueError,))

        # Trigger the circuit breaker to OPEN
        mock_func = AsyncMock(side_effect=ValueError("failure"))
        with pytest.raises(ValueError, match="failure"):
            await cb.call(mock_func)

        assert cb.state == CircuitState.OPEN

        # Next call should be rejected immediately
        mock_func2 = AsyncMock(return_value="success")
        with pytest.raises(CircuitBreakerOpenError, match="Circuit breaker is OPEN"):
            await cb.call(mock_func2)

        mock_func2.assert_not_called()


class TestCircuitBreakerOpenRecovery:
    """Test OPEN -> HALF_OPEN transition after recovery_timeout."""

    async def test_open_transitions_to_half_open_after_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """OPEN -> HALF_OPEN -> CLOSED after recovery_timeout and successful call."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=30, expected_exceptions=(ValueError,))

        # Open the circuit
        mock_func = AsyncMock(side_effect=ValueError("failure"))
        with pytest.raises(ValueError, match="failure"):
            await cb.call(mock_func)
        assert cb.state == CircuitState.OPEN

        # Monkeypatch time.time to simulate timeout elapsed
        current_time = time.time()
        monkeypatch.setattr(time, "time", lambda: current_time + 31)

        # Call should proceed (transitions through HALF_OPEN), then success resets to CLOSED
        success_func = AsyncMock(return_value="success")
        result = await cb.call(success_func)

        assert result == "success"
        assert cb.state == CircuitState.CLOSED

    async def test_open_rejects_calls_before_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """OPEN state rejects calls if recovery_timeout has not elapsed."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=30, expected_exceptions=(ValueError,))

        # Open the circuit and record the time
        mock_func = AsyncMock(side_effect=ValueError("failure"))
        with pytest.raises(ValueError, match="failure"):
            await cb.call(mock_func)

        # Monkeypatch time to be just before timeout
        current_time = time.time()
        monkeypatch.setattr(time, "time", lambda: current_time + 29)

        # Call should still be rejected
        success_func = AsyncMock(return_value="success")
        with pytest.raises(CircuitBreakerOpenError, match="Circuit breaker is OPEN"):
            await cb.call(success_func)

        success_func.assert_not_called()


class TestCircuitBreakerHalfOpen:
    """Test HALF_OPEN state transitions."""

    async def test_half_open_success_resets_to_closed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """HALF_OPEN -> CLOSED on success, resets failure_count to 0."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=30, expected_exceptions=(ValueError,))

        # Open the circuit and accumulate some failures
        mock_func = AsyncMock(side_effect=ValueError("failure"))
        with pytest.raises(ValueError, match="failure"):
            await cb.call(mock_func)
        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 1

        # Transition to HALF_OPEN
        current_time = time.time()
        monkeypatch.setattr(time, "time", lambda: current_time + 31)

        # Success should reset to CLOSED
        success_func = AsyncMock(return_value="success")
        result = await cb.call(success_func)

        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    async def test_half_open_failure_reopens_immediately(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """HALF_OPEN -> OPEN immediately on failure (no threshold check)."""
        cb = CircuitBreaker(failure_threshold=5, recovery_timeout=30, expected_exceptions=(ValueError,))

        # Manually set to OPEN first (simulate already triggered)
        cb.state = CircuitState.OPEN
        cb.failure_count = 3  # Less than threshold

        # Transition to HALF_OPEN
        current_time = time.time()
        monkeypatch.setattr(time, "time", lambda: current_time + 31)

        # Failure in HALF_OPEN should reopen immediately
        fail_func = AsyncMock(side_effect=ValueError("failure"))
        with pytest.raises(ValueError, match="failure"):
            await cb.call(fail_func)

        assert cb.state == CircuitState.OPEN


class TestCircuitBreakerUnexpectedExceptions:
    """Test that unexpected exception types pass through without tripping the breaker."""

    async def test_unexpected_exception_passes_through(self) -> None:
        """Unexpected exception types should pass through and not trip the breaker."""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60, expected_exceptions=(ValueError,))

        # Raise an unexpected exception type
        mock_func = AsyncMock(side_effect=TypeError("unexpected"))

        with pytest.raises(TypeError, match="unexpected"):
            await cb.call(mock_func)

        # Circuit should still be CLOSED, failure_count unchanged
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    async def test_expected_exception_trips_breaker(self) -> None:
        """Expected exception types should trip the breaker."""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60, expected_exceptions=(ValueError,))

        mock_func = AsyncMock(side_effect=ValueError("expected"))

        with pytest.raises(ValueError, match="expected"):
            await cb.call(mock_func)

        # Failure count should increment
        assert cb.failure_count == 1

    async def test_multiple_unexpected_exceptions(self) -> None:
        """Multiple unexpected exceptions don't affect breaker state."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=60, expected_exceptions=(ValueError,))

        # Multiple unexpected exceptions
        for _ in range(5):
            mock_func = AsyncMock(side_effect=KeyError("unexpected"))
            with pytest.raises(KeyError, match="unexpected"):
                await cb.call(mock_func)

        # Circuit should still be CLOSED with no failures recorded
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0


class TestCircuitBreakerIntegration:
    """Integration tests for circuit breaker behavior."""

    async def test_full_cycle_closed_open_half_open_closed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Full cycle: CLOSED -> OPEN -> HALF_OPEN -> CLOSED."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=30, expected_exceptions=(ValueError,))

        assert cb.state == CircuitState.CLOSED

        # Fail twice to open the circuit
        fail_func = AsyncMock(side_effect=ValueError("failure"))
        for _ in range(2):
            with pytest.raises(ValueError, match="failure"):
                await cb.call(fail_func)

        assert cb.state == CircuitState.OPEN

        # Wait for recovery timeout
        current_time = time.time()
        monkeypatch.setattr(time, "time", lambda: current_time + 31)

        # Success in HALF_OPEN should close the circuit
        success_func = AsyncMock(return_value="success")
        result = await cb.call(success_func)

        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    async def test_full_cycle_closed_open_half_open_open(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Full cycle: CLOSED -> OPEN -> HALF_OPEN -> OPEN."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=30, expected_exceptions=(ValueError,))

        # Fail twice to open the circuit
        fail_func = AsyncMock(side_effect=ValueError("failure"))
        for _ in range(2):
            with pytest.raises(ValueError, match="failure"):
                await cb.call(fail_func)

        assert cb.state == CircuitState.OPEN

        # Wait for recovery timeout
        current_time = time.time()
        monkeypatch.setattr(time, "time", lambda: current_time + 31)

        # Failure in HALF_OPEN should reopen the circuit
        with pytest.raises(ValueError, match="failure"):
            await cb.call(fail_func)

        assert cb.state == CircuitState.OPEN

    async def test_httpx_request_error_trips_breaker(self) -> None:
        """Verify that httpx.RequestError is handled by default circuit breaker."""
        assert auth_service_circuit_breaker.expected_exceptions == (httpx.RequestError, httpx.HTTPStatusError)

        mock_func = AsyncMock(side_effect=httpx.RequestError("connection error"))

        with pytest.raises(httpx.RequestError, match="connection error"):
            await auth_service_circuit_breaker.call(mock_func)

        assert auth_service_circuit_breaker.failure_count == 1

    async def test_httpx_http_status_error_trips_breaker(self) -> None:
        """Verify that httpx.HTTPStatusError (5xx errors) trips the circuit breaker."""
        # Reset circuit breaker state since it's a singleton shared across tests
        auth_service_circuit_breaker.state = CircuitState.CLOSED
        auth_service_circuit_breaker.failure_count = 0
        auth_service_circuit_breaker.last_failure_time = 0

        # Create a mock response for HTTPStatusError
        mock_response = httpx.Response(500, text="Internal Server Error")
        mock_func = AsyncMock(
            side_effect=httpx.HTTPStatusError("Server error", request=httpx.Request("GET", "/"), response=mock_response)
        )

        with pytest.raises(httpx.HTTPStatusError, match="Server error"):
            await auth_service_circuit_breaker.call(mock_func)

        assert auth_service_circuit_breaker.failure_count == 1
