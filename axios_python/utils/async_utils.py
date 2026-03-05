# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import asyncio
import inspect
from typing import Any, Callable, Coroutine, TypeVar

__all__ = [
    "run_sync",
    "is_async_callable",
]

T = TypeVar("T")


def run_sync(coro: Coroutine[Any, Any, T]) -> T:
    """Execute an async coroutine from a synchronous context.

    If an event loop is already running, a new loop is created in a
    background thread. Otherwise the coroutine is run directly.

    Args:
        coro: The coroutine to execute.

    Returns:
        The result of the coroutine.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()

    return asyncio.run(coro)


def is_async_callable(obj: Callable[..., Any]) -> bool:
    """Return True if *obj* is an async callable.

    Handles plain coroutine functions and objects with an async ``__call__``.

    Args:
        obj: The callable to inspect.

    Returns:
        True if calling *obj* would produce a coroutine.
    """
    if inspect.iscoroutinefunction(obj):
        return True
    if hasattr(obj, "__call__"):
        return inspect.iscoroutinefunction(obj.__call__)
    return False
