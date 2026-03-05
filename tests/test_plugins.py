# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import logging
import pytest
import respx
import httpx

from axios_python import create
from axios_python.plugins.auth import AuthPlugin
from axios_python.plugins.cache import CachePlugin
from axios_python.plugins.logger import LoggerPlugin


BASE = "https://test.local"


class TestAuthPlugin:

    @respx.mock
    def test_static_token_injection(self) -> None:
        route = respx.get(f"{BASE}/secure").mock(return_value=httpx.Response(200, json={}))
        api = create({"base_url": BASE})
        api.plugin(AuthPlugin(token="abc123", scheme="Bearer"))
        api.get("/secure")
        sent_request = route.calls[0].request
        assert sent_request.headers["authorization"] == "Bearer abc123"

    @respx.mock
    def test_dynamic_token_provider(self) -> None:
        route = respx.get(f"{BASE}/secure").mock(return_value=httpx.Response(200, json={}))
        api = create({"base_url": BASE})
        api.plugin(AuthPlugin(token_provider=lambda: "dynamic_token"))
        api.get("/secure")
        sent_request = route.calls[0].request
        assert sent_request.headers["authorization"] == "Bearer dynamic_token"

    @respx.mock
    def test_custom_scheme(self) -> None:
        route = respx.get(f"{BASE}/secure").mock(return_value=httpx.Response(200, json={}))
        api = create({"base_url": BASE})
        api.plugin(AuthPlugin(token="key", scheme="Token"))
        api.get("/secure")
        sent_request = route.calls[0].request
        assert sent_request.headers["authorization"] == "Token key"


class TestCachePlugin:

    def test_cache_stores_and_returns(self) -> None:
        plugin = CachePlugin(ttl=60)
        plugin._set("url1", "response1")
        assert plugin._get("url1") == "response1"

    def test_cache_ttl_expiry(self) -> None:
        plugin = CachePlugin(ttl=0.01)
        plugin._set("url1", "response1")
        import time
        time.sleep(0.02)
        assert plugin._get("url1") is None

    def test_cache_max_size_eviction(self) -> None:
        plugin = CachePlugin(ttl=60, max_size=2)
        plugin._set("a", 1)
        plugin._set("b", 2)
        plugin._set("c", 3)
        assert plugin._get("a") is None
        assert plugin._get("b") == 2
        assert plugin._get("c") == 3

    def test_cache_clear(self) -> None:
        plugin = CachePlugin(ttl=60)
        plugin._set("a", 1)
        plugin.clear()
        assert plugin._get("a") is None


class TestLoggerPlugin:

    @respx.mock
    def test_logger_logs_request(self, caplog: pytest.LogCaptureFixture) -> None:
        respx.get(f"{BASE}/logged").mock(return_value=httpx.Response(200, json={}))
        api = create({"base_url": BASE})
        api.plugin(LoggerPlugin(level=logging.INFO))
        with caplog.at_level(logging.INFO, logger="axios_python"):
            api.get("/logged")
        assert any("GET" in r.message for r in caplog.records)
