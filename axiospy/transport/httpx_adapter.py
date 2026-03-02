from __future__ import annotations

import httpx

from axiospy.exceptions import NetworkError, TimeoutError
from axiospy.request import PreparedRequest
from axiospy.response import Response
from axiospy.transport.base import BaseTransport

__all__ = [
    "HttpxTransport",
]


class HttpxTransport(BaseTransport):
    """Transport adapter backed by httpx.

    Uses ``httpx.Client`` for synchronous calls and ``httpx.AsyncClient``
    for asynchronous calls.
    """

    def __init__(self) -> None:
        self._sync_client: httpx.Client | None = None
        self._async_client: httpx.AsyncClient | None = None

    def _get_sync_client(self) -> httpx.Client:
        if self._sync_client is None:
            self._sync_client = httpx.Client()
        return self._sync_client

    def _get_async_client(self) -> httpx.AsyncClient:
        if self._async_client is None:
            self._async_client = httpx.AsyncClient()
        return self._async_client

    def _build_response(self, raw: httpx.Response, request: PreparedRequest) -> Response:
        try:
            data = raw.json()
        except Exception:
            data = raw.text
        return Response(
            status_code=raw.status_code,
            headers=dict(raw.headers),
            data=data,
            request=request,
            raw=raw,
        )

    def send(self, request: PreparedRequest) -> Response:
        """Send a synchronous HTTP request via httpx.

        Args:
            request: The prepared request to dispatch.

        Returns:
            A axiospy Response wrapping the httpx response.

        Raises:
            TimeoutError: If the request exceeds the configured timeout.
            NetworkError: If a connection-level error occurs.
        """
        client = self._get_sync_client()
        try:
            raw = client.request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                params=request.params,
                content=request.data,
                json=request.json,
                timeout=request.timeout,
            )
            return self._build_response(raw, request)
        except httpx.TimeoutException as exc:
            raise TimeoutError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise NetworkError(str(exc)) from exc

    async def send_async(self, request: PreparedRequest) -> Response:
        """Send an asynchronous HTTP request via httpx.

        Args:
            request: The prepared request to dispatch.

        Returns:
            A axiospy Response wrapping the httpx response.

        Raises:
            TimeoutError: If the request exceeds the configured timeout.
            NetworkError: If a connection-level error occurs.
        """
        client = self._get_async_client()
        try:
            raw = await client.request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                params=request.params,
                content=request.data,
                json=request.json,
                timeout=request.timeout,
            )
            return self._build_response(raw, request)
        except httpx.TimeoutException as exc:
            raise TimeoutError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise NetworkError(str(exc)) from exc

    def close(self) -> None:
        """Close the synchronous httpx client."""
        if self._sync_client is not None:
            self._sync_client.close()
            self._sync_client = None

    async def aclose(self) -> None:
        """Close the asynchronous httpx client."""
        if self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None
