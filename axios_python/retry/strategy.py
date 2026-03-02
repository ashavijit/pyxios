from __future__ import annotations

import abc

__all__ = [
    "RetryStrategy",
    "FixedDelay",
    "ExponentialBackoff",
    "LinearBackoff",
]


class RetryStrategy(abc.ABC):
    """Abstract base for retry delay strategies."""

    @abc.abstractmethod
    def get_delay(self, attempt: int) -> float:
        """Return the delay in seconds before the next retry.

        Args:
            attempt: The current attempt number (0-based).

        Returns:
            Delay in seconds.
        """
        ...


class FixedDelay(RetryStrategy):
    """Retry with a constant delay between attempts.

    Args:
        delay: Seconds to wait between retries.
    """

    def __init__(self, delay: float = 1.0) -> None:
        self._delay = delay

    def get_delay(self, attempt: int) -> float:
        """Return the fixed delay regardless of attempt number.

        Args:
            attempt: The current attempt number (0-based).

        Returns:
            The configured fixed delay.
        """
        return self._delay


class ExponentialBackoff(RetryStrategy):
    """Retry with exponentially increasing delays.

    Delay is ``base * (multiplier ** attempt)``, capped at *max_delay*.

    Args:
        base: Initial delay in seconds.
        multiplier: Factor by which delay grows each attempt.
        max_delay: Maximum delay cap in seconds.
    """

    def __init__(
        self,
        base: float = 0.5,
        multiplier: float = 2.0,
        max_delay: float = 30.0,
    ) -> None:
        self._base = base
        self._multiplier = multiplier
        self._max_delay = max_delay

    def get_delay(self, attempt: int) -> float:
        """Return an exponentially increasing delay.

        Args:
            attempt: The current attempt number (0-based).

        Returns:
            The computed delay, capped at max_delay.
        """
        delay = self._base * (self._multiplier ** attempt)
        return min(delay, self._max_delay)


class LinearBackoff(RetryStrategy):
    """Retry with linearly increasing delays.

    Delay is ``base + (increment * attempt)``, capped at *max_delay*.

    Args:
        base: Initial delay in seconds.
        increment: Seconds to add per attempt.
        max_delay: Maximum delay cap in seconds.
    """

    def __init__(
        self,
        base: float = 0.5,
        increment: float = 0.5,
        max_delay: float = 30.0,
    ) -> None:
        self._base = base
        self._increment = increment
        self._max_delay = max_delay

    def get_delay(self, attempt: int) -> float:
        """Return a linearly increasing delay.

        Args:
            attempt: The current attempt number (0-based).

        Returns:
            The computed delay, capped at max_delay.
        """
        delay = self._base + (self._increment * attempt)
        return min(delay, self._max_delay)
