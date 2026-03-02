from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from axiospy.client import Axiospy

__all__ = [
    "LoggerPlugin",
]

_logger = logging.getLogger("axiospy")


class LoggerPlugin:
    """Plugin that logs outgoing requests and incoming responses.

    Args:
        level: The logging level to use (default: ``logging.DEBUG``).
        logger: An optional custom logger instance.
    """

    def __init__(
        self,
        level: int = logging.DEBUG,
        logger: logging.Logger | None = None,
    ) -> None:
        self._level = level
        self._logger = logger or _logger

    def install(self, client: Axiospy) -> None:
        """Register request and response interceptors for logging.

        Args:
            client: The Axiospy client to extend.
        """
        client.interceptors.request.use(self._log_request)
        client.interceptors.response.use(self._log_response)

    def _log_request(self, config: dict[str, Any]) -> dict[str, Any]:
        self._logger.log(
            self._level,
            "%s %s",
            config.get("method", "GET").upper(),
            config.get("url", ""),
        )
        return config

    def _log_response(self, response: Any) -> Any:
        self._logger.log(
            self._level,
            "Response %s %s",
            getattr(response, "status_code", "?"),
            getattr(response, "request", None),
        )
        return response
