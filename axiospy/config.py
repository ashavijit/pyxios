from __future__ import annotations

from typing import Any, TypedDict

from axiospy.defaults import DEFAULT_CONFIG
from axiospy.utils.merge import deep_merge

__all__ = [
    "RequestConfig",
    "merge_config",
]


class RequestConfig(TypedDict, total=False):
    """Configuration options for a single request."""

    method: str
    url: str
    base_url: str
    headers: dict[str, str]
    params: dict[str, Any]
    data: Any
    json: Any
    timeout: int | float
    max_retries: int
    retry_strategy: Any
    retry_on: Any
    cancel_token: Any


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
