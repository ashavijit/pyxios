# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

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
from axios_python.helpers import all, spread
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
    "all",
    "spread",
    "request",
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "head",
    "options",
    "async_request",
    "async_get",
    "async_post",
    "async_put",
    "async_patch",
    "async_delete",
    "async_head",
    "async_options",
]


def create(config: dict[str, Any] | None = None, **kwargs: Any) -> AxiosPython:
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

def head(url: str, **kwargs: Any) -> Response:
    return _default_instance.head(url, **kwargs)

def options(url: str, **kwargs: Any) -> Response:
    return _default_instance.options(url, **kwargs)

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

async def async_head(url: str, **kwargs: Any) -> Response:
    return await _default_instance.async_head(url, **kwargs)

async def async_options(url: str, **kwargs: Any) -> Response:
    return await _default_instance.async_options(url, **kwargs)
