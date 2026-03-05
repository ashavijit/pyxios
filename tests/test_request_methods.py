# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import pytest
import respx
import httpx

from axios_python import create


BASE = "https://test.local"


@respx.mock
class TestSyncMethods:

    def test_get(self) -> None:
        respx.get(f"{BASE}/data").mock(return_value=httpx.Response(200, json={"ok": True}))
        api = create({"base_url": BASE})
        res = api.get("/data")
        assert res.status_code == 200
        assert res.json()["ok"] is True

    def test_post(self) -> None:
        respx.post(f"{BASE}/data").mock(return_value=httpx.Response(201, json={"id": 1}))
        api = create({"base_url": BASE})
        res = api.post("/data", json={"name": "test"})
        assert res.status_code == 201

    def test_put(self) -> None:
        respx.put(f"{BASE}/data/1").mock(return_value=httpx.Response(200, json={"updated": True}))
        api = create({"base_url": BASE})
        res = api.put("/data/1", json={"name": "updated"})
        assert res.status_code == 200

    def test_patch(self) -> None:
        respx.patch(f"{BASE}/data/1").mock(return_value=httpx.Response(200, json={"patched": True}))
        api = create({"base_url": BASE})
        res = api.patch("/data/1", json={"name": "patched"})
        assert res.status_code == 200

    def test_delete(self) -> None:
        respx.delete(f"{BASE}/data/1").mock(return_value=httpx.Response(204))
        api = create({"base_url": BASE})
        res = api.delete("/data/1")
        assert res.status_code == 204

    def test_head(self) -> None:
        respx.head(f"{BASE}/data").mock(return_value=httpx.Response(200, headers={"x-total": "42"}))
        api = create({"base_url": BASE})
        res = api.head("/data")
        assert res.status_code == 200
        assert res.headers["x-total"] == "42"

    def test_options(self) -> None:
        respx.options(f"{BASE}/data").mock(
            return_value=httpx.Response(200, headers={"allow": "GET, POST, OPTIONS"})
        )
        api = create({"base_url": BASE})
        res = api.options("/data")
        assert res.status_code == 200
        assert "GET" in res.headers["allow"]


@respx.mock
class TestAsyncMethods:

    @pytest.mark.asyncio
    async def test_async_get(self) -> None:
        respx.get(f"{BASE}/data").mock(return_value=httpx.Response(200, json={"ok": True}))
        api = create({"base_url": BASE})
        res = await api.async_get("/data")
        assert res.status_code == 200
        assert res.json()["ok"] is True

    @pytest.mark.asyncio
    async def test_async_post(self) -> None:
        respx.post(f"{BASE}/data").mock(return_value=httpx.Response(201, json={"id": 1}))
        api = create({"base_url": BASE})
        res = await api.async_post("/data", json={"name": "test"})
        assert res.status_code == 201

    @pytest.mark.asyncio
    async def test_async_put(self) -> None:
        respx.put(f"{BASE}/data/1").mock(return_value=httpx.Response(200, json={"updated": True}))
        api = create({"base_url": BASE})
        res = await api.async_put("/data/1", json={"name": "updated"})
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_async_patch(self) -> None:
        respx.patch(f"{BASE}/data/1").mock(return_value=httpx.Response(200, json={"patched": True}))
        api = create({"base_url": BASE})
        res = await api.async_patch("/data/1", json={"name": "patched"})
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_async_delete(self) -> None:
        respx.delete(f"{BASE}/data/1").mock(return_value=httpx.Response(204))
        api = create({"base_url": BASE})
        res = await api.async_delete("/data/1")
        assert res.status_code == 204

    @pytest.mark.asyncio
    async def test_async_head(self) -> None:
        respx.head(f"{BASE}/data").mock(return_value=httpx.Response(200, headers={"x-total": "42"}))
        api = create({"base_url": BASE})
        res = await api.async_head("/data")
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_async_options(self) -> None:
        respx.options(f"{BASE}/data").mock(
            return_value=httpx.Response(200, headers={"allow": "GET, POST"})
        )
        api = create({"base_url": BASE})
        res = await api.async_options("/data")
        assert res.status_code == 200


@respx.mock
class TestRequestMethod:

    def test_request_with_explicit_method(self) -> None:
        respx.get(f"{BASE}/resource").mock(return_value=httpx.Response(200, json={}))
        api = create({"base_url": BASE})
        res = api.request("GET", "/resource")
        assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_async_request_with_explicit_method(self) -> None:
        respx.post(f"{BASE}/resource").mock(return_value=httpx.Response(201, json={}))
        api = create({"base_url": BASE})
        res = await api.async_request("POST", "/resource")
        assert res.status_code == 201
