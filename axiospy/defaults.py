from __future__ import annotations

from typing import Any

__all__ = [
    "DEFAULT_TIMEOUT",
    "DEFAULT_HEADERS",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_CONFIG",
]

DEFAULT_TIMEOUT: int | float = 30

DEFAULT_HEADERS: dict[str, str] = {
    "Accept": "application/json, text/plain, */*",
}

DEFAULT_MAX_RETRIES: int = 0

DEFAULT_CONFIG: dict[str, Any] = {
    "base_url": "",
    "timeout": DEFAULT_TIMEOUT,
    "headers": dict(DEFAULT_HEADERS),
    "params": {},
    "max_retries": DEFAULT_MAX_RETRIES,
}
