# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import pytest

from axios_python.middleware.pipeline import Pipeline


class TestPipeline:

    @pytest.mark.asyncio
    async def test_empty_pipeline_calls_final(self) -> None:
        pipeline = Pipeline()

        async def final(ctx: dict) -> str:
            return f"final:{ctx['value']}"

        result = await pipeline.execute({"value": "hello"}, final)
        assert result == "final:hello"

    @pytest.mark.asyncio
    async def test_single_middleware(self) -> None:
        pipeline = Pipeline()
        calls: list[str] = []

        async def mw(ctx: dict, next_fn) -> str:
            calls.append("before")
            result = await next_fn(ctx)
            calls.append("after")
            return result

        pipeline.use(mw)

        async def final(ctx: dict) -> str:
            calls.append("final")
            return "done"

        await pipeline.execute({}, final)
        assert calls == ["before", "final", "after"]

    @pytest.mark.asyncio
    async def test_middleware_order(self) -> None:
        pipeline = Pipeline()
        order: list[int] = []

        async def mw1(ctx: dict, next_fn):
            order.append(1)
            return await next_fn(ctx)

        async def mw2(ctx: dict, next_fn):
            order.append(2)
            return await next_fn(ctx)

        pipeline.use(mw1)
        pipeline.use(mw2)

        async def final(ctx: dict) -> str:
            order.append(3)
            return "done"

        await pipeline.execute({}, final)
        assert order == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_middleware_can_modify_context(self) -> None:
        pipeline = Pipeline()

        async def inject(ctx: dict, next_fn):
            ctx["injected"] = True
            return await next_fn(ctx)

        pipeline.use(inject)

        async def final(ctx: dict) -> bool:
            return ctx.get("injected", False)

        result = await pipeline.execute({}, final)
        assert result is True

    @pytest.mark.asyncio
    async def test_double_next_raises(self) -> None:
        pipeline = Pipeline()

        async def bad_mw(ctx: dict, next_fn):
            await next_fn(ctx)
            return await next_fn(ctx)

        pipeline.use(bad_mw)

        async def final(ctx: dict) -> str:
            return "done"

        with pytest.raises(RuntimeError, match="next.*called multiple times"):
            await pipeline.execute({}, final)

    def test_len(self) -> None:
        pipeline = Pipeline()
        assert len(pipeline) == 0
        pipeline.use(lambda ctx, nxt: None)
        assert len(pipeline) == 1
