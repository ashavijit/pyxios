# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, TypeVar

from axios_python.response import Response

T = TypeVar("T")

__all__ = [
    "all",
    "spread",
]

async def all(requests: list[Awaitable[Response]]) -> list[Response]:
    """
    Run multiple awaitable requests concurrently.

    @param requests: A list of asynchronous request coroutines.
    @returns: A list of responses in the same order as the requests.
    """
    return list(await asyncio.gather(*requests))


def spread(callback: Callable[..., T]) -> Callable[[list[Any]], T]:
    """
    Unpack an array of results into positional arguments for a callback function.

    @param callback: The function to call with the unpacked results.
    @returns: A wrapper function that accepts an array of results.
    """
    def wrapper(results: list[Any]) -> T:
        return callback(*results)
    return wrapper
