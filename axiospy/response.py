from __future__ import annotations

from typing import Any

from axiospy.request import PreparedRequest

__all__ = [
    "Response",
]


class Response:
    """Wraps a raw HTTP response with a convenient interface.

    Attributes:
        status_code: The HTTP status code.
        headers: Response headers as a dict.
        data: The decoded response body.
        request: The original PreparedRequest that produced this response.
    """

    def __init__(
        self,
        status_code: int,
        headers: dict[str, str],
        data: Any,
        request: PreparedRequest,
        raw: Any = None,
    ) -> None:
        self.status_code = status_code
        self.headers = headers
        self.data = data
        self.request = request
        self._raw = raw

    @property
    def ok(self) -> bool:
        """True if the status code indicates success (2xx)."""
        return 200 <= self.status_code < 300

    @property
    def text(self) -> str:
        """The response body as a string."""
        if isinstance(self.data, str):
            return self.data
        if isinstance(self.data, bytes):
            return self.data.decode("utf-8", errors="replace")
        return str(self.data)

    def json(self) -> Any:
        """Parse the response body as JSON.

        Returns:
            The parsed JSON data. If the body is already a dict or list,
            it is returned directly.
        """
        if isinstance(self.data, (dict, list)):
            return self.data
        import json as _json
        return _json.loads(self.text)

    def __repr__(self) -> str:
        return f"<Response [{self.status_code}]>"
