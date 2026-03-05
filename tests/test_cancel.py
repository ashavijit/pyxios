# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import pytest

from axios_python.cancel.token import CancelToken
from axios_python.exceptions import CancelError


class TestCancelToken:

    def test_not_cancelled_initially(self) -> None:
        token = CancelToken()
        assert token.is_cancelled is False

    def test_cancel_sets_flag(self) -> None:
        token = CancelToken()
        token.cancel()
        assert token.is_cancelled is True

    def test_cancel_with_reason(self) -> None:
        token = CancelToken()
        token.cancel(reason="user abort")
        assert token.reason == "user abort"

    def test_default_reason(self) -> None:
        token = CancelToken()
        token.cancel()
        assert token.reason == "Request cancelled"

    def test_cancel_is_idempotent(self) -> None:
        token = CancelToken()
        token.cancel(reason="first")
        token.cancel(reason="second")
        assert token.reason == "first"

    def test_raise_if_cancelled(self) -> None:
        token = CancelToken()
        token.cancel()
        with pytest.raises(CancelError):
            token.raise_if_cancelled()

    def test_raise_if_not_cancelled(self) -> None:
        token = CancelToken()
        token.raise_if_cancelled()

    def test_on_cancel_fires_callback(self) -> None:
        token = CancelToken()
        called = []
        token.on_cancel(lambda: called.append(True))
        token.cancel()
        assert called == [True]

    def test_on_cancel_fires_immediately_if_already_cancelled(self) -> None:
        token = CancelToken()
        token.cancel()
        called = []
        token.on_cancel(lambda: called.append(True))
        assert called == [True]

    def test_multiple_callbacks(self) -> None:
        token = CancelToken()
        results: list[int] = []
        token.on_cancel(lambda: results.append(1))
        token.on_cancel(lambda: results.append(2))
        token.cancel()
        assert results == [1, 2]
