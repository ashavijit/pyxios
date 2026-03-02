from __future__ import annotations

from typing import Any, Awaitable, Callable

from axiospy.middleware.pipeline import Pipeline

__all__ = [
    "MiddlewareManager",
]

MiddlewareFn = Callable[[dict[str, Any], Callable[..., Awaitable[Any]]], Awaitable[Any]]
FinalHandler = Callable[[dict[str, Any]], Awaitable[Any]]


class MiddlewareManager:
    """Manages the middleware pipeline for a client instance.

    Example::

        async def timing(ctx, next):
            import time
            start = time.monotonic()
            result = await next(ctx)
            ctx["elapsed"] = time.monotonic() - start
            return result

        api.use(timing)
    """

    def __init__(self) -> None:
        self._pipeline: Pipeline = Pipeline()

    def use(self, fn: MiddlewareFn) -> None:
        """Register a middleware function.

        Args:
            fn: An async callable with signature ``(ctx, next) -> Any``.
        """
        self._pipeline.use(fn)

    async def execute(self, ctx: dict[str, Any], final: FinalHandler) -> Any:
        """Execute the full middleware stack, terminating with *final*.

        Args:
            ctx: A mutable context dict.
            final: The terminal handler.

        Returns:
            The result produced by the pipeline.
        """
        return await self._pipeline.execute(ctx, final)

    def __len__(self) -> int:
        return len(self._pipeline)
