# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from axios_python.client import AxiosPython

__all__ = [
    "AuthPlugin",
]


class AuthPlugin:
    """Plugin that injects an Authorization header into every request.

    Supports static tokens and dynamic token providers.

    Args:
        token: A static bearer token string.
        token_provider: A callable that returns a token string at call
            time (takes precedence over *token* if both are provided).
        scheme: The authorization scheme (default: ``"Bearer"``).
    """

    def __init__(
        self,
        token: str | None = None,
        token_provider: Callable[[], str] | None = None,
        scheme: str = "Bearer",
    ) -> None:
        self._token = token
        self._token_provider = token_provider
        self._scheme = scheme

    def install(self, client: AxiosPython) -> None:
        """Register a request interceptor that sets the Authorization header.

        Args:
            client: The AxiosPython client to extend.
        """
        client.interceptors.request.use(self._inject_auth)

    def _inject_auth(self, config: dict[str, Any]) -> dict[str, Any]:
        token = self._token_provider() if self._token_provider else self._token
        if token:
            headers = dict(config.get("headers", {}))
            headers["Authorization"] = f"{self._scheme} {token}"
            config["headers"] = headers
        return config
