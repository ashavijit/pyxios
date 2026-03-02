from __future__ import annotations

from typing import Any, Callable

from axios_python.exceptions import InterceptorError

__all__ = [
    "InterceptorChain",
]

HandlerFn = Callable[[Any], Any]
ErrorHandlerFn = Callable[[Exception], Any]


class InterceptorChain:
    """An ordered sequence of interceptor handler pairs.

    Each entry is a ``(fulfilled, rejected)`` tuple.  During execution the
    chain pipes the value through each *fulfilled* handler in order.  If any
    handler raises, the corresponding *rejected* handler (if provided) is
    called, otherwise the exception propagates.
    """

    def __init__(self) -> None:
        self._handlers: list[tuple[int, HandlerFn, ErrorHandlerFn | None]] = []
        self._next_id: int = 0

    def use(
        self,
        fulfilled: HandlerFn,
        rejected: ErrorHandlerFn | None = None,
    ) -> int:
        """Register a new interceptor handler pair.

        Args:
            fulfilled: Called with the current value when the chain succeeds.
            rejected: Called with the exception when a prior handler raises.

        Returns:
            An integer id that can be passed to :meth:`eject`.
        """
        handler_id = self._next_id
        self._next_id += 1
        self._handlers.append((handler_id, fulfilled, rejected))
        return handler_id

    def eject(self, handler_id: int) -> None:
        """Remove a previously registered interceptor by its id.

        Args:
            handler_id: The id returned by :meth:`use`.
        """
        self._handlers = [
            h for h in self._handlers if h[0] != handler_id
        ]

    def run(self, initial: Any) -> Any:
        """Execute the chain synchronously.

        Args:
            initial: The starting value passed to the first handler.

        Returns:
            The value produced by the final handler.

        Raises:
            InterceptorError: If a handler raises and no rejected handler
                catches the error.
        """
        value = initial
        for _, fulfilled, rejected in self._handlers:
            try:
                value = fulfilled(value)
            except Exception as exc:
                if rejected is not None:
                    value = rejected(exc)
                else:
                    raise InterceptorError(str(exc)) from exc
        return value

    async def run_async(self, initial: Any) -> Any:
        """Execute the chain asynchronously.

        Await handlers that return coroutines.

        Args:
            initial: The starting value passed to the first handler.

        Returns:
            The value produced by the final handler.

        Raises:
            InterceptorError: If a handler raises and no rejected handler
                catches the error.
        """
        import inspect

        value = initial
        for _, fulfilled, rejected in self._handlers:
            try:
                result = fulfilled(value)
                if inspect.isawaitable(result):
                    value = await result
                else:
                    value = result
            except Exception as exc:
                if rejected is not None:
                    result = rejected(exc)
                    if inspect.isawaitable(result):
                        value = await result
                    else:
                        value = result
                else:
                    raise InterceptorError(str(exc)) from exc
        return value

    def __len__(self) -> int:
        return len(self._handlers)
