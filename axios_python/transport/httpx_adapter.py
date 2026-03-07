# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import httpx

from axios_python.exceptions import NetworkError, TimeoutError
from axios_python.progress import ProgressEvent
from axios_python.request import PreparedRequest
from axios_python.response import Response
from axios_python.transport.base import BaseTransport

class UploadProgressStream(httpx.SyncByteStream):
    def __init__(self, stream, callback, total):
        self._stream = stream
        self._callback = callback
        self._loaded = 0
        self._total = total
        
    def __iter__(self):
        for chunk in self._stream:
            self._loaded += len(chunk)
            self._callback(ProgressEvent(loaded=self._loaded, total=self._total))
            yield chunk

class AsyncUploadProgressStream(httpx.AsyncByteStream):
    def __init__(self, stream, callback, total):
        self._stream = stream
        self._callback = callback
        self._loaded = 0
        self._total = total
        
    async def __aiter__(self):
        async for chunk in self._stream:
            self._loaded += len(chunk)
            self._callback(ProgressEvent(loaded=self._loaded, total=self._total))
            yield chunk

__all__ = [
    "HttpxTransport",
]


class HttpxTransport(BaseTransport):

    def __init__(self) -> None:
        self._sync_client: httpx.Client | None = None
        self._async_client: httpx.AsyncClient | None = None

    def _get_sync_client(self) -> httpx.Client:
        if self._sync_client is None:
            self._sync_client = httpx.Client()
        return self._sync_client

    def _get_async_client(self) -> httpx.AsyncClient:
        import asyncio
        loop = asyncio.get_running_loop()
        if not hasattr(self, "_async_client_loop") or self._async_client_loop is not loop:
            self._async_client = httpx.AsyncClient()
            self._async_client_loop = loop
        return self._async_client

    def _build_response(self, raw: httpx.Response, request: PreparedRequest, pre_fetched_data: bytes | None = None) -> Response:
        data = None
        if not request.stream:
            if pre_fetched_data is not None:
                try:
                    data = __import__('json').loads(pre_fetched_data)
                except Exception:
                    try:
                        data = pre_fetched_data.decode('utf-8')
                    except Exception:
                        data = pre_fetched_data
            else:
                try:
                    data = raw.json()
                except Exception:
                    try:
                        data = raw.text
                    except Exception:
                        pass
        return Response(
            status_code=raw.status_code,
            headers=dict(raw.headers),
            data=data,
            request=request,
            raw=raw,
        )

    def send(self, request: PreparedRequest) -> Response:
        client = self._get_sync_client()
        try:
            req = client.build_request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                params=request.params,
                content=request.data,
                json=request.json,
                files=request.files,
                timeout=request.timeout,
            )
            if request.on_upload_progress and hasattr(req, "stream") and req.stream is not None:
                total_str = req.headers.get("content-length")
                total = int(total_str) if total_str and total_str.isdigit() else None
                req.stream = UploadProgressStream(req.stream, request.on_upload_progress, total)

            if request.on_download_progress and not request.stream:
                raw = client.send(
                    req,
                    stream=True,
                    follow_redirects=request.follow_redirects,
                )
                total_str = raw.headers.get("content-length")
                total = int(total_str) if total_str and total_str.isdigit() else None
                
                loaded = 0
                chunks = []
                for chunk in raw.iter_bytes():
                    chunks.append(chunk)
                    loaded += len(chunk)
                    request.on_download_progress(ProgressEvent(loaded=loaded, total=total))
                raw.close()
                return self._build_response(raw, request, pre_fetched_data=b"".join(chunks))

            raw = client.send(
                req,
                stream=request.stream,
                follow_redirects=request.follow_redirects,
            )
            return self._build_response(raw, request)
        except httpx.TimeoutException as exc:
            raise TimeoutError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise NetworkError(str(exc)) from exc

    async def send_async(self, request: PreparedRequest) -> Response:
        client = self._get_async_client()
        try:
            req = client.build_request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                params=request.params,
                content=request.data,
                json=request.json,
                files=request.files,
                timeout=request.timeout,
            )
            if request.on_upload_progress and hasattr(req, "stream") and req.stream is not None:
                total_str = req.headers.get("content-length")
                total = int(total_str) if total_str and total_str.isdigit() else None
                req.stream = AsyncUploadProgressStream(req.stream, request.on_upload_progress, total)

            if request.on_download_progress and not request.stream:
                raw = await client.send(
                    req,
                    stream=True,
                    follow_redirects=request.follow_redirects,
                )
                total_str = raw.headers.get("content-length")
                total = int(total_str) if total_str and total_str.isdigit() else None
                
                loaded = 0
                chunks = []
                async for chunk in raw.aiter_bytes():
                    chunks.append(chunk)
                    loaded += len(chunk)
                    request.on_download_progress(ProgressEvent(loaded=loaded, total=total))
                await raw.aclose()
                return self._build_response(raw, request, pre_fetched_data=b"".join(chunks))

            raw = await client.send(
                req,
                stream=request.stream,
                follow_redirects=request.follow_redirects,
            )
            return self._build_response(raw, request)
        except httpx.TimeoutException as exc:
            raise TimeoutError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise NetworkError(str(exc)) from exc

    def close(self) -> None:
        if self._sync_client is not None:
            self._sync_client.close()
            self._sync_client = None

    async def aclose(self) -> None:
        if self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None
