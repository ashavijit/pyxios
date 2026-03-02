from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from axiospy.client import Axiospy

__all__ = [
    "Plugin",
]


@runtime_checkable
class Plugin(Protocol):
    """Protocol that all axiospy plugins must implement.

    A plugin receives the client instance during installation and may
    register interceptors, middleware, or perform other setup.
    """

    def install(self, client: Axiospy) -> None:
        """Install this plugin onto a client instance.

        Args:
            client: The Axiospy client to extend.
        """
        ...
