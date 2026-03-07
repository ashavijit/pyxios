# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

import pytest
import respx
from httpx import Response

from axios_python import AxiosPython
from axios_python.progress import ProgressEvent

@pytest.mark.asyncio
@respx.mock
async def test_download_progress_async(api: AxiosPython) -> None:
    content = b"a" * 1024
    respx.get("https://test.local/large").mock(
        return_value=Response(200, content=content, headers={"Content-Length": "1024"})
    )
    
    events = []
    def on_progress(event: ProgressEvent):
        events.append(event)
        
    response = await api.async_get("/large", on_download_progress=on_progress)
    
    assert response.status_code == 200
    assert len(events) > 0
    assert events[-1].loaded == 1024
    assert events[-1].total == 1024
    assert events[-1].progress_percent == 100.0

@respx.mock
def test_download_progress_sync(api: AxiosPython) -> None:
    content = b"a" * 2048
    respx.get("https://test.local/large_sync").mock(
        return_value=Response(200, content=content, headers={"Content-Length": "2048"})
    )
    
    events = []
    def on_progress(event: ProgressEvent):
        events.append(event)
        
    response = api.get("/large_sync", on_download_progress=on_progress)
    
    assert response.status_code == 200
    assert len(events) > 0
    assert events[-1].loaded == 2048
    assert events[-1].total == 2048
    assert events[-1].progress_percent == 100.0

# NOTE: Testing upload progress is trickier with httpx + respx because `respx` consumes the request stream instantly
# But we can verify no crashes happen when providing the callbacks.
@pytest.mark.asyncio
@respx.mock
async def test_upload_progress_async(api: AxiosPython) -> None:
    respx.post("https://test.local/upload").mock(
        return_value=Response(200, json={"status": "ok"})
    )
    
    events = []
    def on_progress(event: ProgressEvent):
        events.append(event)
        
    data = b"x" * 1000
    response = await api.async_post("/upload", data=data, headers={"Content-Length": "1000"}, on_upload_progress=on_progress)
    
    assert response.status_code == 200
    # respx or httpx adapter handles the stream
