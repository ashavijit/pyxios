# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

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
from axios_python.utils.pydantic import parse_model

__all__ = [
    "AxiosPython",
]

MiddlewareFn = Callable[[dict[str, Any], Callable[..., Awaitable[Any]]], Awaitable[Any]]


class AxiosPython:

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
        return self._interceptors

    @property
    def defaults(self) -> dict[str, Any]:
        return self._config

    def use(self, middleware: MiddlewareFn) -> AxiosPython:
        self._middleware.use(middleware)
        return self

    def plugin(self, p: Plugin) -> AxiosPython:
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

    def _apply_request_transforms(self, config: dict[str, Any]) -> dict[str, Any]:
        transforms = config.get("transform_request")
        if not transforms:
            return config
        data = config.get("data")
        headers = dict(config.get("headers", {}))
        for fn in transforms:
            data = fn(data, headers)
        config["data"] = data
        config["headers"] = headers
        return config

    def _apply_response_transforms(self, response: Response, config: dict[str, Any]) -> Response:
        transforms = config.get("transform_response")
        if transforms:
            data = response.data
            for fn in transforms:
                data = fn(data)
            response.data = data

        model_cls = config.get("response_model")
        if model_cls is not None and response.data is not None:
            response.data = parse_model(model_cls, response.data)

        return response

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
            follow_redirects=config.get("follow_redirects", True),
            on_upload_progress=config.get("on_upload_progress"),
            on_download_progress=config.get("on_download_progress"),
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
        config = self._apply_request_transforms(config)

        prepared = self._prepare_request(config)
        retry = self._build_retry_engine(config)

        def transport_call() -> Response:
            if cancel_token is not None:
                cancel_token.raise_if_cancelled()
            return self._transport.send(prepared)

        response = retry.execute(transport_call)
        response = self._apply_response_transforms(response, config)
        response = self._interceptors.response.run(response)
        return response

    async def _execute_async(self, config: dict[str, Any]) -> Response:
        cancel_token: CancelToken | None = config.get("cancel_token")

        if cancel_token is not None:
            cancel_token.raise_if_cancelled()

        config = await self._interceptors.request.run_async(config)
        config = self._apply_request_transforms(config)

        prepared = self._prepare_request(config)
        retry = self._build_retry_engine(config)

        async def transport_call() -> Response:
            if cancel_token is not None:
                cancel_token.raise_if_cancelled()
            return await self._transport.send_async(prepared)

        response = await retry.execute_async(transport_call)
        response = self._apply_response_transforms(response, config)
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
                raise RuntimeError(
                    "Async middleware cannot be used with synchronous "
                    "stream=True requests. Use async_get() instead."
                )
            return self._execute_sync(config)
        return run_sync(self._dispatch_async(config))

    def request(self, method: str, url: str, **kwargs: Any) -> Response:
        """
        Send an HTTP request.

        @param method: The HTTP method (GET, POST, etc.).
        @param url: The URL to request.
        @param kwargs: Additional request configuration overrides.
        @returns: The HTTP response.
        """
        config = self._build_request_config(method, url, **kwargs)
        return self._dispatch_sync(config)

    async def async_request(self, method: str, url: str, **kwargs: Any) -> Response:
        """
        Send an asynchronous HTTP request.

        @param method: The HTTP method (GET, POST, etc.).
        @param url: The URL to request.
        @param kwargs: Additional request configuration overrides.
        @returns: The HTTP response.
        """
        config = self._build_request_config(method, url, **kwargs)
        return await self._dispatch_async(config)

    def get(self, url: str, **kwargs: Any) -> Response:
        """
        Send a GET request.

        @param url: The URL to request.
        @param kwargs: Additional request configuration overrides.
        @returns: The HTTP response.
        """
        return self.request("GET", url, **kwargs)

    async def async_get(self, url: str, **kwargs: Any) -> Response:
        """
        Send an asynchronous GET request.

        @param url: The URL to request.
        @param kwargs: Additional request configuration overrides.
        @returns: The HTTP response.
        """
        return await self.async_request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Response:
        """
        Send a POST request.

        @param url: The URL to request.
        @param kwargs: Additional request configuration overrides.
        @returns: The HTTP response.
        """
        return self.request("POST", url, **kwargs)

    async def async_post(self, url: str, **kwargs: Any) -> Response:
        """
        Send an asynchronous POST request.

        @param url: The URL to request.
        @param kwargs: Additional request configuration overrides.
        @returns: The HTTP response.
        """
        return await self.async_request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> Response:
        """
        Send a PUT request.

        @param url: The URL to request.
        @param kwargs: Additional request configuration overrides.
        @returns: The HTTP response.
        """
        return self.request("PUT", url, **kwargs)

    async def async_put(self, url: str, **kwargs: Any) -> Response:
        """
        Send an asynchronous PUT request.

        @param url: The URL to request.
        @param kwargs: Additional request configuration overrides.
        @returns: The HTTP response.
        """
        return await self.async_request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> Response:
        """
        Send a PATCH request.

        @param url: The URL to request.
        @param kwargs: Additional request configuration overrides.
        @returns: The HTTP response.
        """
        return self.request("PATCH", url, **kwargs)

    async def async_patch(self, url: str, **kwargs: Any) -> Response:
        """
        Send an asynchronous PATCH request.

        @param url: The URL to request.
        @param kwargs: Additional request configuration overrides.
        @returns: The HTTP response.
        """
        return await self.async_request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Response:
        """
        Send a DELETE request.

        @param url: The URL to request.
        @param kwargs: Additional request configuration overrides.
        @returns: The HTTP response.
        """
        return self.request("DELETE", url, **kwargs)

    async def async_delete(self, url: str, **kwargs: Any) -> Response:
        """
        Send an asynchronous DELETE request.

        @param url: The URL to request.
        @param kwargs: Additional request configuration overrides.
        @returns: The HTTP response.
        """
        return await self.async_request("DELETE", url, **kwargs)

    def head(self, url: str, **kwargs: Any) -> Response:
        """
        Send a HEAD request.

        @param url: The URL to request.
        @param kwargs: Additional request configuration overrides.
        @returns: The HTTP response.
        """
        return self.request("HEAD", url, **kwargs)

    async def async_head(self, url: str, **kwargs: Any) -> Response:
        """
        Send an asynchronous HEAD request.

        @param url: The URL to request.
        @param kwargs: Additional request configuration overrides.
        @returns: The HTTP response.
        """
        return await self.async_request("HEAD", url, **kwargs)

    def options(self, url: str, **kwargs: Any) -> Response:
        """
        Send an OPTIONS request.

        @param url: The URL to request.
        @param kwargs: Additional request configuration overrides.
        @returns: The HTTP response.
        """
        return self.request("OPTIONS", url, **kwargs)

    async def async_options(self, url: str, **kwargs: Any) -> Response:
        """
        Send an asynchronous OPTIONS request.

        @param url: The URL to request.
        @param kwargs: Additional request configuration overrides.
        @returns: The HTTP response.
        """
        return await self.async_request("OPTIONS", url, **kwargs)

    def close(self) -> None:
        self._transport.close()

    async def aclose(self) -> None:
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
