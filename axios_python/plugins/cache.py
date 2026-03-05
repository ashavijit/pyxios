# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Awaitable, Callable

if TYPE_CHECKING:
    from axios_python.client import AxiosPython

__all__ = [
    "CachePlugin",
]


class CachePlugin:
    """In-memory TTL cache plugin for GET requests.

    Caches responses in memory keyed by full URL.  Only GET requests
    are cached.

    Args:
        ttl: Time-to-live in seconds for cached entries.
        max_size: Maximum number of cached entries.
    """

    def __init__(self, ttl: float = 60.0, max_size: int = 128) -> None:
        self._ttl = ttl
        self._max_size = max_size
        self._store: dict[str, tuple[float, Any]] = {}

    def install(self, client: AxiosPython) -> None:
        """Register a cache middleware on the client.

        Args:
            client: The AxiosPython client to extend.
        """
        plugin = self

        async def cache_middleware(
            ctx: dict[str, Any],
            next_fn: Callable[..., Awaitable[Any]],
        ) -> Any:
            method = ctx.get("method", "GET").upper()
            if method != "GET":
                return await next_fn(ctx)

            url = ctx.get("url", "")
            cached = plugin._get(url)
            if cached is not None:
                return cached

            result = await next_fn(ctx)
            plugin._set(url, result)
            return result

        client.use(cache_middleware)

    def _get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        ts, value = entry
        if time.monotonic() - ts > self._ttl:
            del self._store[key]
            return None
        return value

    def _set(self, key: str, value: Any) -> None:
        if len(self._store) >= self._max_size:
            oldest_key = next(iter(self._store))
            del self._store[oldest_key]
        self._store[key] = (time.monotonic(), value)

    def clear(self) -> None:
        """Remove all entries from the cache."""
        self._store.clear()
