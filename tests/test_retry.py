# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import pytest

from axios_python.retry.strategy import (
    ExponentialBackoff,
    FixedDelay,
    LinearBackoff,
)
from axios_python.retry.engine import RetryEngine
from axios_python.exceptions import RetryError, NetworkError


class TestFixedDelay:

    def test_constant_delay(self) -> None:
        s = FixedDelay(delay=2.0)
        assert s.get_delay(0) == 2.0
        assert s.get_delay(5) == 2.0
        assert s.get_delay(100) == 2.0


class TestExponentialBackoff:

    def test_growing_delay(self) -> None:
        s = ExponentialBackoff(base=1.0, multiplier=2.0, max_delay=16.0)
        assert s.get_delay(0) == 1.0
        assert s.get_delay(1) == 2.0
        assert s.get_delay(2) == 4.0
        assert s.get_delay(3) == 8.0

    def test_cap_at_max(self) -> None:
        s = ExponentialBackoff(base=1.0, multiplier=2.0, max_delay=5.0)
        assert s.get_delay(10) == 5.0


class TestLinearBackoff:

    def test_linear_growth(self) -> None:
        s = LinearBackoff(base=1.0, increment=0.5, max_delay=10.0)
        assert s.get_delay(0) == 1.0
        assert s.get_delay(1) == 1.5
        assert s.get_delay(2) == 2.0

    def test_cap_at_max(self) -> None:
        s = LinearBackoff(base=1.0, increment=1.0, max_delay=3.0)
        assert s.get_delay(100) == 3.0


class TestRetryEngine:

    def test_no_retry_succeeds(self) -> None:
        engine = RetryEngine(max_retries=0)
        assert engine.execute(lambda: 42) == 42

    def test_no_retry_raises(self) -> None:
        engine = RetryEngine(max_retries=0)
        with pytest.raises(NetworkError):
            engine.execute(self._raise_network_error)

    def test_retry_succeeds_after_failures(self) -> None:
        call_count = 0

        def flaky() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise NetworkError("fail")
            return "ok"

        engine = RetryEngine(
            max_retries=3,
            strategy=FixedDelay(delay=0),
        )
        assert engine.execute(flaky) == "ok"
        assert call_count == 3

    def test_retry_exhaustion_raises_retry_error(self) -> None:
        engine = RetryEngine(
            max_retries=2,
            strategy=FixedDelay(delay=0),
        )
        with pytest.raises(RetryError) as exc_info:
            engine.execute(self._raise_network_error)
        assert exc_info.value.last_exception is not None

    def test_non_retryable_exception_not_retried(self) -> None:
        call_count = 0

        def fail() -> None:
            nonlocal call_count
            call_count += 1
            raise ValueError("not retryable")

        engine = RetryEngine(max_retries=3, strategy=FixedDelay(delay=0))
        with pytest.raises(ValueError):
            engine.execute(fail)
        assert call_count == 1

    @staticmethod
    def _raise_network_error() -> None:
        raise NetworkError("connection failed")


class TestRetryEngineAsync:

    @pytest.mark.asyncio
    async def test_async_no_retry(self) -> None:
        engine = RetryEngine(max_retries=0)

        async def ok() -> int:
            return 99

        assert await engine.execute_async(ok) == 99

    @pytest.mark.asyncio
    async def test_async_retry_succeeds(self) -> None:
        call_count = 0

        async def flaky() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise NetworkError("fail")
            return "ok"

        engine = RetryEngine(max_retries=3, strategy=FixedDelay(delay=0))
        result = await engine.execute_async(flaky)
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_async_exhaustion(self) -> None:
        async def always_fail() -> None:
            raise NetworkError("fail")

        engine = RetryEngine(max_retries=1, strategy=FixedDelay(delay=0))
        with pytest.raises(RetryError):
            await engine.execute_async(always_fail)
