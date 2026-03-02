from __future__ import annotations

from typing import Any, Callable

from axios_python.interceptors.chain import InterceptorChain

__all__ = [
    "InterceptorManager",
]

HandlerFn = Callable[[Any], Any]
ErrorHandlerFn = Callable[[Exception], Any]


class InterceptorManager:
    """Manages request and response interceptor chains.

    Access via ``client.interceptors.request`` and
    ``client.interceptors.response``.

    Example::

        api.interceptors.request.use(lambda cfg: cfg)
        api.interceptors.response.use(lambda res: res)
    """

    def __init__(self) -> None:
        self.request: InterceptorChain = InterceptorChain()
        self.response: InterceptorChain = InterceptorChain()
