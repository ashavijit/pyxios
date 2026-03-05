# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from axios_python.client import AxiosPython

__all__ = [
    "Plugin",
]


@runtime_checkable
class Plugin(Protocol):
    """Protocol that all axios_python plugins must implement.

    A plugin receives the client instance during installation and may
    register interceptors, middleware, or perform other setup.
    """

    def install(self, client: AxiosPython) -> None:
        """Install this plugin onto a client instance.

        Args:
            client: The AxiosPython client to extend.
        """
        ...
