# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

from typing import Callable

from axios_python.exceptions import CancelError

__all__ = [
    "CancelToken",
]


class CancelToken:
    """A token used to signal request cancellation.

    Create a token and pass it to a request via the ``cancel_token``
    config key.  Call :meth:`cancel` at any time to abort the associated
    request.

    Example::

        token = CancelToken()
        api.get("/slow", cancel_token=token)
        token.cancel()
    """

    def __init__(self) -> None:
        self._cancelled: bool = False
        self._reason: str = "Request cancelled"
        self._callbacks: list[Callable[[], None]] = []

    @property
    def is_cancelled(self) -> bool:
        """Return True if the token has been cancelled."""
        return self._cancelled

    @property
    def reason(self) -> str:
        """Return the cancellation reason string."""
        return self._reason

    def cancel(self, reason: str = "Request cancelled") -> None:
        """Cancel the token, firing all registered callbacks.

        Args:
            reason: A human-readable reason for the cancellation.
        """
        if self._cancelled:
            return
        self._cancelled = True
        self._reason = reason
        for cb in self._callbacks:
            cb()

    def on_cancel(self, callback: Callable[[], None]) -> None:
        """Register a callback to fire when the token is cancelled.

        If the token is already cancelled, the callback fires immediately.

        Args:
            callback: A zero-argument callable.
        """
        if self._cancelled:
            callback()
            return
        self._callbacks.append(callback)

    def raise_if_cancelled(self) -> None:
        """Raise ``CancelError`` if the token has been cancelled.

        Raises:
            CancelError: If the token was previously cancelled.
        """
        if self._cancelled:
            raise CancelError(self._reason)
