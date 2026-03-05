# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import asyncio
import time
from typing import Any, Awaitable, Callable, TypeVar

from axios_python.exceptions import RetryError
from axios_python.retry.strategy import ExponentialBackoff, RetryStrategy

__all__ = [
    "RetryEngine",
]

T = TypeVar("T")

RetryPredicate = Callable[[Exception], bool]


def _default_retry_on(exc: Exception) -> bool:
    from axios_python.exceptions import NetworkError, TimeoutError as AxiosPythonTimeoutError
    return isinstance(exc, (NetworkError, AxiosPythonTimeoutError))


class RetryEngine:
    """Executes a callable with configurable retry logic.

    Args:
        max_retries: Maximum number of retry attempts (0 = no retries).
        strategy: The delay strategy between attempts.
        retry_on: A predicate that returns True for retryable exceptions.
    """

    def __init__(
        self,
        max_retries: int = 0,
        strategy: RetryStrategy | None = None,
        retry_on: RetryPredicate | None = None,
    ) -> None:
        self._max_retries = max_retries
        self._strategy = strategy or ExponentialBackoff()
        self._retry_on = retry_on or _default_retry_on

    def execute(self, fn: Callable[[], T]) -> T:
        """Execute *fn* synchronously with retries.

        Args:
            fn: A zero-argument callable to execute.

        Returns:
            The return value of *fn* on success.

        Raises:
            RetryError: If all retry attempts are exhausted.
        """
        if self._max_retries <= 0:
            return fn()

        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                return fn()
            except Exception as exc:
                last_exc = exc
                if not self._retry_on(exc):
                    raise
                if attempt < self._max_retries:
                    delay = self._strategy.get_delay(attempt)
                    time.sleep(delay)

        raise RetryError(
            f"All {self._max_retries} retries exhausted",
            last_exception=last_exc,
        )

    async def execute_async(self, fn: Callable[[], Awaitable[T]]) -> T:
        """Execute *fn* asynchronously with retries.

        Args:
            fn: A zero-argument async callable to execute.

        Returns:
            The return value of *fn* on success.

        Raises:
            RetryError: If all retry attempts are exhausted.
        """
        if self._max_retries <= 0:
            return await fn()

        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                return await fn()
            except Exception as exc:
                last_exc = exc
                if not self._retry_on(exc):
                    raise
                if attempt < self._max_retries:
                    delay = self._strategy.get_delay(attempt)
                    await asyncio.sleep(delay)

        raise RetryError(
            f"All {self._max_retries} retries exhausted",
            last_exception=last_exc,
        )
