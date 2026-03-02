from __future__ import annotations

from typing import Any, Awaitable, Callable

from axios_python.cancel.token import CancelToken
from axios_python.config import merge_config
from axios_python.interceptors.manager import InterceptorManager
from axios_python.middleware.manager import MiddlewareManager
from axios_python.plugins.base import Plugin
from axios_python.request import PreparedRequest
from axios_python.response import Response
from axios_python.retry.engine import RetryEngine
from axios_python.retry.strategy import RetryStrategy
from axios_python.transport.base import BaseTransport
from axios_python.transport.httpx_adapter import HttpxTransport
from axios_python.utils.async_utils import run_sync

__all__ = [
    "AxiosPython",
]

MiddlewareFn = Callable[[dict[str, Any], Callable[..., Awaitable[Any]]], Awaitable[Any]]


class AxiosPython:
    """The main axios_python HTTP client.

    Each instance maintains its own configuration, interceptors, middleware
    stack, and transport.  Create instances via :func:`axios_python.create`.

    Args:
        config: Base configuration dict applied to every request made
            through this instance.
        transport: An optional custom transport adapter.  Defaults to
            :class:`~axios_python.transport.httpx_adapter.HttpxTransport`.
    """

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        transport: BaseTransport | None = None,
    ) -> None:
        self._config: dict[str, Any] = config or {}
        self._transport: BaseTransport = transport or HttpxTransport()
        self._interceptors: InterceptorManager = InterceptorManager()
        self._middleware: MiddlewareManager = MiddlewareManager()
        self._plugins: list[Plugin] = []

    @property
    def interceptors(self) -> InterceptorManager:
        """Access request and response interceptor chains."""
        return self._interceptors

    @property
    def defaults(self) -> dict[str, Any]:
        """The base configuration for this client instance."""
        return self._config

    def use(self, middleware: MiddlewareFn) -> AxiosPython:
        """Register a middleware function.

        Args:
            middleware: An async callable with signature
                ``(ctx, next) -> Any``.

        Returns:
            This client instance for chaining.
        """
        self._middleware.use(middleware)
        return self

    def plugin(self, p: Plugin) -> AxiosPython:
        """Install a plugin onto this client.

        Args:
            p: A plugin implementing the :class:`~axios_python.plugins.base.Plugin`
                protocol.

        Returns:
            This client instance for chaining.
        """
        p.install(self)
        self._plugins.append(p)
        return self

    def _build_request_config(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        per_request: dict[str, Any] = {"method": method, "url": url}
        per_request.update(kwargs)
        return merge_config(self._config, per_request)

    def _resolve_url(self, config: dict[str, Any]) -> str:
        base = config.get("base_url", "").rstrip("/")
        path = config.get("url", "")
        if path.startswith(("http://", "https://")):
            return path
        return f"{base}/{path.lstrip('/')}" if base else path

    def _prepare_request(self, config: dict[str, Any]) -> PreparedRequest:
        return PreparedRequest(
            method=config.get("method", "GET").upper(),
            url=self._resolve_url(config),
            headers=dict(config.get("headers", {})),
            params=dict(config.get("params", {})),
            data=config.get("data"),
            json=config.get("json"),
            files=config.get("files"),
            stream=config.get("stream", False),
            timeout=config.get("timeout", 30),
        )

    def _build_retry_engine(self, config: dict[str, Any]) -> RetryEngine:
        return RetryEngine(
            max_retries=config.get("max_retries", 0),
            strategy=config.get("retry_strategy"),
            retry_on=config.get("retry_on"),
        )

    def _execute_sync(self, config: dict[str, Any]) -> Response:
        cancel_token: CancelToken | None = config.get("cancel_token")

        if cancel_token is not None:
            cancel_token.raise_if_cancelled()

        config = self._interceptors.request.run(config)

        prepared = self._prepare_request(config)
        retry = self._build_retry_engine(config)

        def transport_call() -> Response:
            if cancel_token is not None:
                cancel_token.raise_if_cancelled()
            return self._transport.send(prepared)

        response = retry.execute(transport_call)
        response = self._interceptors.response.run(response)
        return response

    async def _execute_async(self, config: dict[str, Any]) -> Response:
        cancel_token: CancelToken | None = config.get("cancel_token")

        if cancel_token is not None:
            cancel_token.raise_if_cancelled()

        config = await self._interceptors.request.run_async(config)

        prepared = self._prepare_request(config)
        retry = self._build_retry_engine(config)

        async def transport_call() -> Response:
            if cancel_token is not None:
                cancel_token.raise_if_cancelled()
            return await self._transport.send_async(prepared)

        response = await retry.execute_async(transport_call)
        response = await self._interceptors.response.run_async(response)
        return response

    async def _dispatch_async(self, config: dict[str, Any]) -> Response:
        if len(self._middleware) > 0:
            async def final(ctx: dict[str, Any]) -> Response:
                return await self._execute_async(ctx)
            return await self._middleware.execute(config, final)
        return await self._execute_async(config)

    def _dispatch_sync(self, config: dict[str, Any]) -> Response:
        if config.get("stream"):
            if len(self._middleware) > 0:
                raise RuntimeError("Async middleware cannot be used with synchronous stream=True requests. Use async_get() instead.")
            return self._execute_sync(config)
        return run_sync(self._dispatch_async(config))

    def request(self, method: str, url: str, **kwargs: Any) -> Response:
        """Send a synchronous HTTP request.

        Args:
            method: The HTTP method (GET, POST, PUT, etc.).
            url: The URL path or full URL.
            **kwargs: Additional config overrides (headers, params, data,
                json, timeout, cancel_token, etc.).

        Returns:
            A :class:`~axios_python.response.Response` object.
        """
        config = self._build_request_config(method, url, **kwargs)
        return self._dispatch_sync(config)

    async def async_request(self, method: str, url: str, **kwargs: Any) -> Response:
        """Send an asynchronous HTTP request.

        Args:
            method: The HTTP method (GET, POST, PUT, etc.).
            url: The URL path or full URL.
            **kwargs: Additional config overrides (headers, params, data,
                json, timeout, cancel_token, etc.).

        Returns:
            A :class:`~axios_python.response.Response` object.
        """
        config = self._build_request_config(method, url, **kwargs)
        return await self._dispatch_async(config)

    def get(self, url: str, **kwargs: Any) -> Response:
        """Send a synchronous GET request.

        Args:
            url: The URL path or full URL.
            **kwargs: Additional config overrides.

        Returns:
            A :class:`~axios_python.response.Response` object.
        """
        return self.request("GET", url, **kwargs)

    async def async_get(self, url: str, **kwargs: Any) -> Response:
        """Send an asynchronous GET request.

        Args:
            url: The URL path or full URL.
            **kwargs: Additional config overrides.

        Returns:
            A :class:`~axios_python.response.Response` object.
        """
        return await self.async_request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Response:
        """Send a synchronous POST request.

        Args:
            url: The URL path or full URL.
            **kwargs: Additional config overrides.

        Returns:
            A :class:`~axios_python.response.Response` object.
        """
        return self.request("POST", url, **kwargs)

    async def async_post(self, url: str, **kwargs: Any) -> Response:
        """Send an asynchronous POST request.

        Args:
            url: The URL path or full URL.
            **kwargs: Additional config overrides.

        Returns:
            A :class:`~axios_python.response.Response` object.
        """
        return await self.async_request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> Response:
        """Send a synchronous PUT request.

        Args:
            url: The URL path or full URL.
            **kwargs: Additional config overrides.

        Returns:
            A :class:`~axios_python.response.Response` object.
        """
        return self.request("PUT", url, **kwargs)

    async def async_put(self, url: str, **kwargs: Any) -> Response:
        """Send an asynchronous PUT request.

        Args:
            url: The URL path or full URL.
            **kwargs: Additional config overrides.

        Returns:
            A :class:`~axios_python.response.Response` object.
        """
        return await self.async_request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> Response:
        """Send a synchronous PATCH request.

        Args:
            url: The URL path or full URL.
            **kwargs: Additional config overrides.

        Returns:
            A :class:`~axios_python.response.Response` object.
        """
        return self.request("PATCH", url, **kwargs)

    async def async_patch(self, url: str, **kwargs: Any) -> Response:
        """Send an asynchronous PATCH request.

        Args:
            url: The URL path or full URL.
            **kwargs: Additional config overrides.

        Returns:
            A :class:`~axios_python.response.Response` object.
        """
        return await self.async_request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Response:
        """Send a synchronous DELETE request.

        Args:
            url: The URL path or full URL.
            **kwargs: Additional config overrides.

        Returns:
            A :class:`~axios_python.response.Response` object.
        """
        return self.request("DELETE", url, **kwargs)

    async def async_delete(self, url: str, **kwargs: Any) -> Response:
        """Send an asynchronous DELETE request.

        Args:
            url: The URL path or full URL.
            **kwargs: Additional config overrides.

        Returns:
            A :class:`~axios_python.response.Response` object.
        """
        return await self.async_request("DELETE", url, **kwargs)

    def close(self) -> None:
        """Release all resources held by this client."""
        self._transport.close()

    async def aclose(self) -> None:
        """Release all resources held by this client asynchronously."""
        await self._transport.aclose()

    def __repr__(self) -> str:
        base = self._config.get("base_url", "")
        return f"<AxiosPython base_url={base!r}>"

    def __enter__(self) -> AxiosPython:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    async def __aenter__(self) -> AxiosPython:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()
