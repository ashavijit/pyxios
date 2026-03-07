# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations
from typing import Any

__all__ = [
    "AxiosPythonError",
    "TimeoutError",
    "NetworkError",
    "CancelError",
    "RetryError",
    "InterceptorError",
    "HTTPStatusError",
]


class AxiosPythonError(Exception):
    """Base exception for all axios_python errors."""


class TimeoutError(AxiosPythonError):
    """Raised when a request exceeds the configured timeout."""


class NetworkError(AxiosPythonError):
    """Raised when a network-level failure occurs."""


class CancelError(AxiosPythonError):
    """Raised when a request is cancelled via a CancelToken."""


class RetryError(AxiosPythonError):
    """Raised when all retry attempts have been exhausted."""

    def __init__(self, message: str, last_exception: Exception | None = None) -> None:
        super().__init__(message)
        self.last_exception = last_exception


class InterceptorError(AxiosPythonError):
    """Raised when an interceptor fails during execution."""


class HTTPStatusError(AxiosPythonError):
    """Raised when a response indicates an HTTP error (4xx or 5xx)."""

    def __init__(self, message: str, response: Any) -> None:
        super().__init__(message)
        self.response = response
