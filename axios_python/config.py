# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

from typing import Any, Callable, TypedDict

from axios_python.defaults import DEFAULT_CONFIG
from axios_python.utils.merge import deep_merge

__all__ = [
    "RequestConfig",
    "merge_config",
]


class RequestConfig(TypedDict, total=False):

    method: str
    url: str
    base_url: str
    headers: dict[str, str]
    params: dict[str, Any]
    data: Any
    json: Any
    files: Any
    stream: bool
    timeout: int | float
    max_retries: int
    retry_strategy: Any
    retry_on: Any
    cancel_token: Any
    follow_redirects: bool
    transform_request: list[Callable[..., Any]]
    transform_response: list[Callable[..., Any]]


def merge_config(*configs: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple configuration dicts with later values taking precedence.

    Args:
        *configs: Configuration dictionaries to merge, ordered from lowest
            to highest priority.

    Returns:
        A new merged configuration dictionary.
    """
    result: dict[str, Any] = deep_merge({}, DEFAULT_CONFIG)
    for cfg in configs:
        if cfg:
            result = deep_merge(result, cfg)
    return result
