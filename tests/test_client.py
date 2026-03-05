# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import pytest

from axios_python import AxiosPython, create
from axios_python.config import merge_config


class TestCreate:

    def test_create_returns_instance(self) -> None:
        client = create()
        assert isinstance(client, AxiosPython)

    def test_create_with_base_url(self) -> None:
        client = create({"base_url": "https://example.com"})
        assert client.defaults.get("base_url") == "https://example.com"

    def test_create_with_kwargs(self) -> None:
        client = create(timeout=42)
        assert client.defaults.get("timeout") == 42

    def test_create_merges_config_and_kwargs(self) -> None:
        client = create({"base_url": "https://example.com"}, timeout=15)
        assert client.defaults.get("base_url") == "https://example.com"
        assert client.defaults.get("timeout") == 15


class TestUrlResolution:

    def test_absolute_url_ignores_base(self) -> None:
        client = create({"base_url": "https://example.com"})
        resolved = client._resolve_url({"base_url": "https://example.com", "url": "https://other.com/path"})
        assert resolved == "https://other.com/path"

    def test_relative_url_joins_base(self) -> None:
        client = create({"base_url": "https://example.com"})
        resolved = client._resolve_url({"base_url": "https://example.com", "url": "/users"})
        assert resolved == "https://example.com/users"

    def test_base_url_trailing_slash(self) -> None:
        client = create({"base_url": "https://example.com/"})
        resolved = client._resolve_url({"base_url": "https://example.com/", "url": "/users"})
        assert resolved == "https://example.com/users"

    def test_no_base_url(self) -> None:
        client = create()
        resolved = client._resolve_url({"url": "/users"})
        assert resolved == "/users"


class TestMergeConfig:

    def test_later_overrides_earlier(self) -> None:
        result = merge_config({"timeout": 10}, {"timeout": 20})
        assert result["timeout"] == 20

    def test_deep_merge_headers(self) -> None:
        result = merge_config(
            {"headers": {"X-A": "1"}},
            {"headers": {"X-B": "2"}},
        )
        assert result["headers"]["X-A"] == "1"
        assert result["headers"]["X-B"] == "2"


class TestContextManager:

    def test_sync_context_manager(self) -> None:
        with create() as client:
            assert isinstance(client, AxiosPython)

    @pytest.mark.asyncio
    async def test_async_context_manager(self) -> None:
        async with AxiosPython() as client:
            assert isinstance(client, AxiosPython)


class TestRepr:

    def test_repr_with_base_url(self) -> None:
        client = create({"base_url": "https://api.example.com"})
        assert "api.example.com" in repr(client)

    def test_repr_without_base_url(self) -> None:
        client = create()
        assert "AxiosPython" in repr(client)
