# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import pytest

from axios_python.interceptors.chain import InterceptorChain
from axios_python.interceptors.manager import InterceptorManager
from axios_python.exceptions import InterceptorError


class TestInterceptorChain:

    def test_run_single_handler(self) -> None:
        chain = InterceptorChain()
        chain.use(lambda v: v + 1)
        assert chain.run(0) == 1

    def test_run_multiple_handlers(self) -> None:
        chain = InterceptorChain()
        chain.use(lambda v: v + 1)
        chain.use(lambda v: v * 2)
        assert chain.run(5) == 12

    def test_eject_removes_handler(self) -> None:
        chain = InterceptorChain()
        hid = chain.use(lambda v: v + 100)
        chain.use(lambda v: v * 2)
        chain.eject(hid)
        assert chain.run(5) == 10

    def test_rejected_handler_catches_error(self) -> None:
        chain = InterceptorChain()

        def fail(v: int) -> int:
            raise ValueError("boom")

        chain.use(fail, lambda exc: 42)
        assert chain.run(0) == 42

    def test_unhandled_error_raises_interceptor_error(self) -> None:
        chain = InterceptorChain()
        chain.use(lambda v: 1 / 0)
        with pytest.raises(InterceptorError):
            chain.run(0)

    def test_len(self) -> None:
        chain = InterceptorChain()
        assert len(chain) == 0
        chain.use(lambda v: v)
        assert len(chain) == 1


class TestInterceptorChainAsync:

    @pytest.mark.asyncio
    async def test_run_async_single(self) -> None:
        chain = InterceptorChain()
        chain.use(lambda v: v + 10)
        result = await chain.run_async(5)
        assert result == 15

    @pytest.mark.asyncio
    async def test_run_async_with_async_handler(self) -> None:
        chain = InterceptorChain()

        async def double(v: int) -> int:
            return v * 2

        chain.use(double)
        result = await chain.run_async(7)
        assert result == 14

    @pytest.mark.asyncio
    async def test_run_async_error_with_rejected(self) -> None:
        chain = InterceptorChain()

        def fail(v: int) -> int:
            raise ValueError("err")

        chain.use(fail, lambda exc: -1)
        result = await chain.run_async(0)
        assert result == -1


class TestInterceptorManager:

    def test_has_request_and_response_chains(self) -> None:
        mgr = InterceptorManager()
        assert isinstance(mgr.request, InterceptorChain)
        assert isinstance(mgr.response, InterceptorChain)
