# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import pytest
import respx
import httpx

from axios_python import AxiosPython, create


@pytest.fixture()
def mock_router() -> respx.MockRouter:
    return respx.MockRouter(assert_all_called=False)


@pytest.fixture()
def api() -> AxiosPython:
    return create({"base_url": "https://test.local", "timeout": 5})
