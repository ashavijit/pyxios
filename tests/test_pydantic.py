# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

import pytest
pytest.importorskip("pydantic")

import respx
from httpx import Response
from pydantic import BaseModel

from axios_python import AxiosPython

class User(BaseModel):
    id: int
    name: str

@pytest.mark.asyncio
@respx.mock
async def test_pydantic_response_model(api: AxiosPython) -> None:
    respx.get("https://test.local/user").mock(
        return_value=Response(200, json={"id": 1, "name": "Avijit"})
    )
    
    response = await api.async_get("/user", response_model=User)
    
    assert response.status_code == 200
    assert isinstance(response.data, User)
    assert response.data.id == 1
    assert response.data.name == "Avijit"

@respx.mock
def test_pydantic_response_model_sync(api: AxiosPython) -> None:
    respx.get("https://test.local/user").mock(
        return_value=Response(200, json={"id": 2, "name": "John"})
    )
    
    response = api.get("/user", response_model=User)
    
    assert response.status_code == 200
    assert isinstance(response.data, User)
    assert response.data.id == 2
    assert response.data.name == "John"
