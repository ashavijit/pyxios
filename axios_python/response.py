# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

from typing import Any, AsyncIterator, Iterator

from axios_python.request import PreparedRequest

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
        if self.data is None:
            try:
                self.read()
            except Exception:
                pass
        if isinstance(self.data, str):
            return self.data
        if isinstance(self.data, bytes):
            return self.data.decode("utf-8", errors="replace")
        return str(self.data) if self.data is not None else ""

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

    def raise_for_status(self) -> Response:
        """Raises HTTPStatusError if one occurred.
        
        Returns:
            The response object.
        """
        if not self.ok:
            from axios_python.exceptions import HTTPStatusError
            reason = getattr(self._raw, "reason_phrase", "Unknown Reason")
            message = f"{self.status_code} {reason} for url: {self.request.url}"
            raise HTTPStatusError(message, response=self)
        return self

    def iter_bytes(self, chunk_size: int | None = None) -> Iterator[bytes]:
        """Iterate over the response body in bytes."""
        return self._raw.iter_bytes(chunk_size=chunk_size)  # type: ignore[no-any-return]

    def iter_text(self, chunk_size: int | None = None) -> Iterator[str]:
        """Iterate over the response body in text."""
        return self._raw.iter_text(chunk_size=chunk_size)  # type: ignore[no-any-return]

    def iter_lines(self) -> Iterator[str]:
        """Iterate over the response body line by line."""
        return self._raw.iter_lines()  # type: ignore[no-any-return]

    def aiter_bytes(self, chunk_size: int | None = None) -> AsyncIterator[bytes]:
        """Asynchronously iterate over the response body in bytes."""
        return self._raw.aiter_bytes(chunk_size=chunk_size)  # type: ignore[no-any-return]

    def aiter_text(self, chunk_size: int | None = None) -> AsyncIterator[str]:
        """Asynchronously iterate over the response body in text."""
        return self._raw.aiter_text(chunk_size=chunk_size)  # type: ignore[no-any-return]

    def aiter_lines(self) -> AsyncIterator[str]:
        """Asynchronously iterate over the response body line by line."""
        return self._raw.aiter_lines()  # type: ignore[no-any-return]

    def read(self) -> bytes:
        """Read the entire response body in bytes."""
        self.data = self._raw.read()
        return self.data  # type: ignore[no-any-return]

    async def aread(self) -> bytes:
        """Asynchronously read the entire response body in bytes."""
        self.data = await self._raw.aread()
        return self.data  # type: ignore[no-any-return]

    def close(self) -> None:
        """Close the underlying HTTP response stream."""
        if self._raw is not None:
            self._raw.close()

    async def aclose(self) -> None:
        """Asynchronously close the underlying HTTP response stream."""
        if self._raw is not None:
            await self._raw.aclose()
            
    def __enter__(self) -> Response:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    async def __aenter__(self) -> Response:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

    def __repr__(self) -> str:
        return f"<Response [{self.status_code}]>"
