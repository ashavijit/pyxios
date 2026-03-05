# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import pytest
import respx
import httpx

from axios_python import create
from axios_python.helpers import all, spread


BASE = "https://test.local"


@respx.mock
class TestAll:

    @pytest.mark.asyncio
    async def test_concurrent_requests(self) -> None:
        respx.get(f"{BASE}/a").mock(return_value=httpx.Response(200, json={"id": "a"}))
        respx.get(f"{BASE}/b").mock(return_value=httpx.Response(200, json={"id": "b"}))

        api = create({"base_url": BASE})
        results = await all([
            api.async_get("/a"),
            api.async_get("/b"),
        ])
        assert len(results) == 2
        assert results[0].json()["id"] == "a"
        assert results[1].json()["id"] == "b"

    @pytest.mark.asyncio
    async def test_all_empty_list(self) -> None:
        results = await all([])
        assert results == []

    @pytest.mark.asyncio
    async def test_all_single_request(self) -> None:
        respx.get(f"{BASE}/only").mock(return_value=httpx.Response(200, json={"x": 1}))
        api = create({"base_url": BASE})
        results = await all([api.async_get("/only")])
        assert len(results) == 1


class TestSpread:

    def test_spread_unpacks_results(self) -> None:
        def handler(a, b, c):
            return a + b + c

        wrapped = spread(handler)
        result = wrapped([1, 2, 3])
        assert result == 6

    def test_spread_with_single_item(self) -> None:
        wrapped = spread(lambda x: x * 10)
        assert wrapped([5]) == 50

    def test_spread_preserves_return_type(self) -> None:
        wrapped = spread(lambda a, b: {"sum": a + b})
        result = wrapped([10, 20])
        assert result == {"sum": 30}
