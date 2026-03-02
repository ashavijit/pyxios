"""axiospy - A developer-experience-first HTTP client for Python.

Provides an Axios-inspired interface with interceptors, middleware,
retry, cancellation tokens, and a plugin system on top of httpx.

Quick start::

    import axiospy

    api = axiospy.create({"base_url": "https://api.example.com"})
    response = api.get("/users")
    print(response.data)
"""

from __future__ import annotations

from typing import Any

from axiospy.cancel.token import CancelToken
from axiospy.client import Axiospy
from axiospy.config import RequestConfig, merge_config
from axiospy.exceptions import (
    CancelError,
    InterceptorError,
    NetworkError,
    AxiospyError,
    RetryError,
    TimeoutError,
    HTTPStatusError,
)
from axiospy.plugins.auth import AuthPlugin
from axiospy.plugins.base import Plugin
from axiospy.plugins.cache import CachePlugin
from axiospy.plugins.logger import LoggerPlugin
from axiospy.request import PreparedRequest
from axiospy.response import Response
from axiospy.retry.strategy import (
    ExponentialBackoff,
    FixedDelay,
    LinearBackoff,
    RetryStrategy,
)
from axiospy.transport.base import BaseTransport
from axiospy.transport.httpx_adapter import HttpxTransport

__all__ = [
    "create",
    "Axiospy",
    "CancelToken",
    "Response",
    "PreparedRequest",
    "RequestConfig",
    "merge_config",
    "AxiospyError",
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


def create(config: dict[str, Any] | None = None, **kwargs: Any) -> Axiospy:
    """Create a new axiospy client instance.

    This is the primary entry point for the library.

    Args:
        config: A configuration dict with keys like ``base_url``,
            ``timeout``, ``headers``, ``params``, ``max_retries``, etc.
        **kwargs: Additional config keys merged into *config*.

    Returns:
        A configured :class:`Axiospy` client instance.

    Example::

        api = axiospy.create({
            "base_url": "https://api.example.com",
            "timeout": 10,
        })
        response = api.get("/users")
    """
    merged = dict(config or {})
    merged.update(kwargs)
    return Axiospy(config=merged)


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
