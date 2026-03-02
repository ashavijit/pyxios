from __future__ import annotations

__all__ = [
    "AxiospyError",
    "TimeoutError",
    "NetworkError",
    "CancelError",
    "RetryError",
    "InterceptorError",
]


class AxiospyError(Exception):
    """Base exception for all axiospy errors."""


class TimeoutError(AxiospyError):
    """Raised when a request exceeds the configured timeout."""


class NetworkError(AxiospyError):
    """Raised when a network-level failure occurs."""


class CancelError(AxiospyError):
    """Raised when a request is cancelled via a CancelToken."""


class RetryError(AxiospyError):
    """Raised when all retry attempts have been exhausted."""

    def __init__(self, message: str, last_exception: Exception | None = None) -> None:
        super().__init__(message)
        self.last_exception = last_exception


class InterceptorError(AxiospyError):
    """Raised when an interceptor fails during execution."""
