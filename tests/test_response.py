# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import pytest

from axios_python.request import PreparedRequest
from axios_python.response import Response
from axios_python.exceptions import HTTPStatusError


class TestResponseOk:

    def test_ok_for_200(self) -> None:
        res = self._make(200)
        assert res.ok is True

    def test_ok_for_299(self) -> None:
        res = self._make(299)
        assert res.ok is True

    def test_not_ok_for_400(self) -> None:
        res = self._make(400)
        assert res.ok is False

    def test_not_ok_for_500(self) -> None:
        res = self._make(500)
        assert res.ok is False

    @staticmethod
    def _make(status: int) -> Response:
        req = PreparedRequest(method="GET", url="https://example.com")
        return Response(status_code=status, headers={}, data=None, request=req)


class TestResponseText:

    def test_string_data(self) -> None:
        res = self._make("hello")
        assert res.text == "hello"

    def test_bytes_data(self) -> None:
        res = self._make(b"bytes")
        assert res.text == "bytes"

    def test_dict_data(self) -> None:
        res = self._make({"key": "val"})
        assert "key" in res.text

    def test_none_data_without_raw(self) -> None:
        req = PreparedRequest(method="GET", url="https://example.com")
        res = Response(status_code=200, headers={}, data=None, request=req, raw=None)
        assert res.text == ""

    @staticmethod
    def _make(data) -> Response:
        req = PreparedRequest(method="GET", url="https://example.com")
        return Response(status_code=200, headers={}, data=data, request=req)


class TestResponseJson:

    def test_dict_data_returned_directly(self) -> None:
        req = PreparedRequest(method="GET", url="https://example.com")
        res = Response(status_code=200, headers={}, data={"a": 1}, request=req)
        assert res.json() == {"a": 1}

    def test_list_data_returned_directly(self) -> None:
        req = PreparedRequest(method="GET", url="https://example.com")
        res = Response(status_code=200, headers={}, data=[1, 2], request=req)
        assert res.json() == [1, 2]

    def test_string_data_parsed(self) -> None:
        req = PreparedRequest(method="GET", url="https://example.com")
        res = Response(status_code=200, headers={}, data='{"b": 2}', request=req)
        assert res.json() == {"b": 2}


class TestRaiseForStatus:

    def test_success_returns_self(self) -> None:
        req = PreparedRequest(method="GET", url="https://example.com")
        res = Response(status_code=200, headers={}, data=None, request=req)
        assert res.raise_for_status() is res

    def test_error_raises(self) -> None:
        req = PreparedRequest(method="GET", url="https://example.com")
        res = Response(status_code=404, headers={}, data=None, request=req)
        with pytest.raises(HTTPStatusError) as exc_info:
            res.raise_for_status()
        assert exc_info.value.response is res

    def test_error_message_contains_url(self) -> None:
        req = PreparedRequest(method="GET", url="https://example.com/missing")
        res = Response(status_code=404, headers={}, data=None, request=req)
        with pytest.raises(HTTPStatusError, match="example.com/missing"):
            res.raise_for_status()


class TestResponseRepr:

    def test_repr(self) -> None:
        req = PreparedRequest(method="GET", url="https://example.com")
        res = Response(status_code=201, headers={}, data=None, request=req)
        assert "201" in repr(res)


class TestResponseContextManager:

    def test_sync_context_manager(self) -> None:
        req = PreparedRequest(method="GET", url="https://example.com")
        res = Response(status_code=200, headers={}, data=None, request=req, raw=None)
        with res as r:
            assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_async_context_manager(self) -> None:
        req = PreparedRequest(method="GET", url="https://example.com")
        res = Response(status_code=200, headers={}, data=None, request=req, raw=None)
        async with res as r:
            assert r.status_code == 200
