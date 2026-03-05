# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from axios_python.request import PreparedRequest
    from axios_python.response import Response

__all__ = [
    "BaseTransport",
]


class BaseTransport(abc.ABC):
    """Abstract base class for HTTP transport adapters.

    Subclasses must implement both :meth:`send` for synchronous requests
    and :meth:`send_async` for asynchronous requests.
    """

    @abc.abstractmethod
    def send(self, request: PreparedRequest) -> Response:
        """Send a request synchronously.

        Args:
            request: The fully prepared request to dispatch.

        Returns:
            A axios_python Response object.
        """
        ...

    @abc.abstractmethod
    async def send_async(self, request: PreparedRequest) -> Response:
        """Send a request asynchronously.

        Args:
            request: The fully prepared request to dispatch.

        Returns:
            A axios_python Response object.
        """
        ...

    def close(self) -> None:
        """Release resources held by the transport."""

    async def aclose(self) -> None:
        """Release resources held by the transport asynchronously."""
