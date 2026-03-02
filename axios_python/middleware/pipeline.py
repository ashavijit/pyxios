from __future__ import annotations

from typing import Any, Awaitable, Callable

__all__ = [
    "Pipeline",
]

MiddlewareFn = Callable[[dict[str, Any], Callable[..., Awaitable[Any]]], Awaitable[Any]]
FinalHandler = Callable[[dict[str, Any]], Awaitable[Any]]


class Pipeline:
    """Express-style middleware pipeline.

    Middleware functions have the signature::

        async def my_middleware(ctx: dict, next: Callable) -> Any:
            # pre-processing
            result = await next(ctx)
            # post-processing
            return result

    The pipeline composes all registered middleware into a single callable
    that terminates in a *final handler*.
    """

    def __init__(self) -> None:
        self._stack: list[MiddlewareFn] = []

    def use(self, fn: MiddlewareFn) -> None:
        """Add a middleware function to the pipeline.

        Args:
            fn: An async callable with signature ``(ctx, next) -> Any``.
        """
        self._stack.append(fn)

    async def execute(self, ctx: dict[str, Any], final: FinalHandler) -> Any:
        """Run the pipeline and terminate with *final*.

        Args:
            ctx: A mutable context dict shared across all middleware.
            final: The terminal handler invoked after all middleware.

        Returns:
            The result produced by the pipeline.
        """
        index = -1

        async def dispatch(i: int, c: dict[str, Any]) -> Any:
            nonlocal index
            if i <= index:
                raise RuntimeError("next() called multiple times")
            index = i
            if i < len(self._stack):
                mw = self._stack[i]

                async def next_fn(updated_ctx: dict[str, Any] | None = None) -> Any:
                    return await dispatch(i + 1, updated_ctx if updated_ctx is not None else c)

                return await mw(c, next_fn)
            return await final(c)

        return await dispatch(0, ctx)

    def __len__(self) -> int:
        return len(self._stack)
