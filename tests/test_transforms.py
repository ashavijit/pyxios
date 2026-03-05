# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import json
import pytest
import respx
import httpx

from axios_python import create


BASE = "https://test.local"


@respx.mock
class TestTransformRequest:

    def test_transform_request_modifies_data(self) -> None:
        route = respx.post(f"{BASE}/data").mock(return_value=httpx.Response(200, json={}))
        api = create({"base_url": BASE})

        def serialize(data, headers):
            headers["content-type"] = "application/json"
            return json.dumps(data) if data else data

        res = api.post(
            "/data",
            data={"key": "value"},
            transform_request=[serialize],
        )
        assert res.status_code == 200

    def test_multiple_transforms_chain(self) -> None:
        respx.post(f"{BASE}/data").mock(return_value=httpx.Response(200, json={}))
        api = create({"base_url": BASE})

        def add_timestamp(data, headers):
            if isinstance(data, dict):
                data["ts"] = 123
            return data

        def wrap(data, headers):
            return {"payload": data}

        res = api.post(
            "/data",
            data={"key": "value"},
            transform_request=[add_timestamp, wrap],
        )
        assert res.status_code == 200

    def test_no_transforms_is_noop(self) -> None:
        respx.get(f"{BASE}/data").mock(return_value=httpx.Response(200, json={"ok": True}))
        api = create({"base_url": BASE})
        res = api.get("/data")
        assert res.json()["ok"] is True


@respx.mock
class TestTransformResponse:

    def test_transform_response_modifies_data(self) -> None:
        respx.get(f"{BASE}/data").mock(
            return_value=httpx.Response(200, json={"results": [1, 2, 3], "meta": {}})
        )
        api = create({"base_url": BASE})

        def unwrap(data):
            if isinstance(data, dict):
                return data.get("results", data)
            return data

        res = api.get("/data", transform_response=[unwrap])
        assert res.data == [1, 2, 3]

    def test_multiple_response_transforms(self) -> None:
        respx.get(f"{BASE}/data").mock(
            return_value=httpx.Response(200, json={"items": [10, 20]})
        )
        api = create({"base_url": BASE})

        def extract(data):
            return data.get("items", [])

        def double(data):
            return [x * 2 for x in data]

        res = api.get("/data", transform_response=[extract, double])
        assert res.data == [20, 40]


@respx.mock
class TestTransformAsync:

    @pytest.mark.asyncio
    async def test_async_transforms(self) -> None:
        respx.get(f"{BASE}/data").mock(
            return_value=httpx.Response(200, json={"value": 5})
        )
        api = create({"base_url": BASE})

        def extract_value(data):
            return data.get("value", 0)

        res = await api.async_get("/data", transform_response=[extract_value])
        assert res.data == 5
