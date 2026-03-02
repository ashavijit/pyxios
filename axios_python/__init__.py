"""axios_python - A developer-experience-first HTTP client for Python.

Provides an Axios-inspired interface with interceptors, middleware,
retry, cancellation tokens, and a plugin system on top of httpx.

Quick start::

    import axios_python

    api = axios_python.create({"base_url": "https://api.example.com"})
    response = api.get("/users")
    print(response.data)
"""

from __future__ import annotations

from typing import Any

from axios_python.cancel.token import CancelToken
from axios_python.client import AxiosPython
from axios_python.config import RequestConfig, merge_config
from axios_python.exceptions import (
    CancelError,
    InterceptorError,
    NetworkError,
    AxiosPythonError,
    RetryError,
    TimeoutError,
    HTTPStatusError,
)
from axios_python.plugins.auth import AuthPlugin
from axios_python.plugins.base import Plugin
from axios_python.plugins.cache import CachePlugin
from axios_python.plugins.logger import LoggerPlugin
from axios_python.request import PreparedRequest
from axios_python.response import Response
from axios_python.retry.strategy import (
    ExponentialBackoff,
    FixedDelay,
    LinearBackoff,
    RetryStrategy,
)
from axios_python.transport.base import BaseTransport
from axios_python.transport.httpx_adapter import HttpxTransport

__all__ = [
    "create",
    "AxiosPython",
    "CancelToken",
    "Response",
    "PreparedRequest",
    "RequestConfig",
    "merge_config",
    "AxiosPythonError",
    "TimeoutError",
    "NetworkError",
    "CancelError",
    "RetryError",
    "InterceptorError",
    "HTTPStatusError",
    "Plugin",
    "LoggerPlugin",
    "CachePlugin",
    "AuthPlugin",
    "BaseTransport",
    "HttpxTransport",
    "RetryStrategy",
    "FixedDelay",
    "ExponentialBackoff",
    "LinearBackoff",
    "request",
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "async_request",
    "async_get",
    "async_post",
    "async_put",
    "async_patch",
    "async_delete",
]


def create(config: dict[str, Any] | None = None, **kwargs: Any) -> AxiosPython:
    """Create a new axios_python client instance.

    This is the primary entry point for the library.

    Args:
        config: A configuration dict with keys like ``base_url``,
            ``timeout``, ``headers``, ``params``, ``max_retries``, etc.
        **kwargs: Additional config keys merged into *config*.

    Returns:
        A configured :class:`AxiosPython` client instance.

    Example::

        api = axios_python.create({
            "base_url": "https://api.example.com",
            "timeout": 10,
        })
        response = api.get("/users")
    """
    merged = dict(config or {})
    merged.update(kwargs)
    return AxiosPython(config=merged)


_default_instance = create()

def request(method: str, url: str, **kwargs: Any) -> Response:
    return _default_instance.request(method, url, **kwargs)

def get(url: str, **kwargs: Any) -> Response:
    return _default_instance.get(url, **kwargs)

def post(url: str, **kwargs: Any) -> Response:
    return _default_instance.post(url, **kwargs)

def put(url: str, **kwargs: Any) -> Response:
    return _default_instance.put(url, **kwargs)

def patch(url: str, **kwargs: Any) -> Response:
    return _default_instance.patch(url, **kwargs)

def delete(url: str, **kwargs: Any) -> Response:
    return _default_instance.delete(url, **kwargs)

async def async_request(method: str, url: str, **kwargs: Any) -> Response:
    return await _default_instance.async_request(method, url, **kwargs)

async def async_get(url: str, **kwargs: Any) -> Response:
    return await _default_instance.async_get(url, **kwargs)

async def async_post(url: str, **kwargs: Any) -> Response:
    return await _default_instance.async_post(url, **kwargs)

async def async_put(url: str, **kwargs: Any) -> Response:
    return await _default_instance.async_put(url, **kwargs)

async def async_patch(url: str, **kwargs: Any) -> Response:
    return await _default_instance.async_patch(url, **kwargs)

async def async_delete(url: str, **kwargs: Any) -> Response:
    return await _default_instance.async_delete(url, **kwargs)
