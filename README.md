# axiospy

[![PyPI version](https://img.shields.io/pypi/v/axiospy.svg)](https://pypi.org/project/axiospy/)
[![Python versions](https://img.shields.io/pypi/pyversions/axiospy.svg)](https://pypi.org/project/axiospy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A developer-experience-first HTTP client for Python, heavily inspired by [Axios](https://axios-http.com/).

The Python ecosystem has amazing HTTP transport libraries (`requests`, `httpx`, `aiohttp`), but they are often focused purely on sending requests and getting responses. Modern applications need a **network orchestration layer**—features like request lifecycle hooks, middleware, interceptors, isolated client instances, request cancellation, and unified synchronous/asynchronous developer experience. 

`axiospy` brings the elegant, feature-rich Axios model to Python, built natively on top of `httpx`.

---

## Features

- 🌐 **Instance-based Client:** Completely isolated state for different APIs.
- 🔄 **Unified API:** Identical interface for both Sync (`api.get()`) and Async (`await api.async_get()`).
- 🔗 **Interceptors:** Hook into requests before they are sent, or responses before they are returned.
- 🚰 **Middleware Pipeline:** Express.js-style async middleware for complex request wrapping.
- 🔁 **Retry Engine:** Built-in strategies for linear, fixed, and exponential backoff.
- 🚫 **Cancellation Tokens:** Cleanly abort requests gracefully.
- 🔌 **Plugin System:** Easily extend clients with Cache, Auth, and Logging plugins (included out-of-the-box).
- 🧩 **Swappable Transport:** Backed by `httpx` by default, but completely abstracted for custom transports.
- 📝 **Fully Typed:** 100% strict typing support for modern Python 3.10+.

---

## Installation

Install using `pip`:

```bash
pip install axiospy
```

Requires Python 3.10+.

---

## Quick Start

### Basic Synchronous Usage

```python
import axiospy

# Zero-setup module level request
response = axiospy.get("https://httpbin.org/get", params={"query": "python"})

# Or create an isolated instance with default configuration
api = axiospy.create({
    "base_url": "https://httpbin.org",
    "timeout": 10,
    "headers": {
        "X-App-Client": "MyCLI/1.0"
    }
})

# Make a request using the instance
response = api.get("/get", params={"query": "python"})

print(f"Status: {response.status_code}")
if response.ok:
    print(response.json())
```

### Asynchronous Native

`axiospy` treats async as a first-class citizen. Just prefix method names with `async_`.

```python
import asyncio
import axiospy

async def fetch_data():
    # Non-blocking async call via instance
    api = axiospy.create({"base_url": "https://httpbin.org"})
    response = await api.async_get("/delay/2")
    
    # Or module level
    response = await axiospy.async_get("https://httpbin.org/delay/2")
    print(response.data)

asyncio.run(fetch_data())
```

### File Uploads

Multipart file uploads are supported out of the box matching the `requests` interface.

```python
with open("report.csv", "rb") as f:
    # Files can be passed as an open file handle or a tuple mapping
    files = {"file": ("report.csv", f, "text/csv")}
    response = axiospy.post("https://httpbin.org/post", files=files)
```

### Streaming Responses

For large files or continuous data streams, use `stream=True`. The response is exposed as a context manager for both sync and async calls.

```python
import axiospy

# Synchronous execution
with axiospy.get("https://httpbin.org/stream-bytes/100", stream=True) as response:
    for chunk in response.iter_bytes(chunk_size=10):
        print(len(chunk))

# Asynchronous execution in an async function
async with await axiospy.async_get("https://.../stream", stream=True) as response:
    async for line in response.aiter_lines():
        print(line)
```

---

## Core Concepts

### Interceptors

Interceptors allow you to tap into the lifecycle of a request or response. They run sequentially.

```python
api = axiospy.create({"base_url": "https://api.myapp.com"})

# Add a request interceptor
def authorize_request(config):
    config["headers"]["Authorization"] = "Bearer token123"
    return config

api.interceptors.request.use(authorize_request)

# Add a response interceptor
def unwrap_data(response):
    # Automatically unwrap the 'data' payload from the JSON
    response.data = response.json().get("data", response.data)
    return response

api.interceptors.response.use(unwrap_data)
```

### Middleware

For more complex logic that needs to "wrap" the entire request (like timing, distributed tracing, or custom caching), use the Express.js-style middleware pipeline.

```python
import time

async def logger_middleware(ctx, next_fn):
    print(f"Starting {ctx.get('method')} to {ctx.get('url')}")
    start = time.monotonic()
    
    # Yield control to the next middleware / transport layer
    result = await next_fn(ctx)
    
    elapsed = time.monotonic() - start
    print(f"Finished in {elapsed:.3f}s with status {result.status_code}")
    
    return result

api.use(logger_middleware)
```

### Retry Engine

Temporary network issues shouldn't hard-crash your app. Provide a retry strategy when creating your client.

```python
from axiospy import ExponentialBackoff

api = axiospy.create({
    "base_url": "https://httpbin.org",
    "max_retries": 3,
    "retry_strategy": ExponentialBackoff(base=1.0, multiplier=2.0, max_delay=10.0),
})
```

By default, this retries on Network Errors and Timeouts.

### Request Cancellation

Use a `CancelToken` to abort long-running requests or cancel requests when a user navigates away.

```python
from axiospy import CancelToken
import threading
import time

token = CancelToken()

def background_fetch():
    try:
        api.get("/delay/10", cancel_token=token)
    except axiospy.CancelError as e:
        print(f"Request aborted: {e}")

threading.Thread(target=background_fetch).start()

time.sleep(1)
token.cancel(reason="User clicked 'Stop'")
```

---

## Plugins

`axiospy` ships with first-party plugins for common use-cases.

### Authentication Plugin

Automatically injects `Authorization` headers. Supports static tokens or dynamic providers.

```python
from axiospy import AuthPlugin

api.plugin(AuthPlugin(scheme="Bearer", token="super-secret-key"))

# Or dynamically fetch it:
# api.plugin(AuthPlugin(token_provider=lambda: get_fresh_token()))
```

### Cache Plugin

In-memory TTL cache for `GET` requests to reduce redundant network load.

```python
from axiospy import CachePlugin

# Cache GET responses for 120 seconds, max 256 items
api.plugin(CachePlugin(ttl=120, max_size=256))
```

### Logger Plugin

Standardized `logging` for requests and responses out of the box.

```python
import logging
from axiospy import LoggerPlugin

logging.basicConfig(level=logging.INFO)
api.plugin(LoggerPlugin(level=logging.INFO))
```

---

## Configuration Reference

You can pass the following properties to `axiospy.create(config)` or as overrides to individual request methods (`api.get("/url", **kwargs)`):

| Property | Type | Description |
|----------|------|-------------|
| `base_url` | `str` | Base URL attached to relative paths. |
| `method` | `str` | HTTP Method (e.g., `"GET"`, `"POST"`). |
| `url` | `str` | The target path or absolute URL. |
| `headers` | `dict` | Dictionary of HTTP headers. |
| `params` | `dict` | URL Query parameters. |
| `data` | `Any` | Request body content (raw). |
| `json` | `Any` | Request body content (automatically serialized to JSON). |
| `files` | `Any` | Multipart-encoded files dictionary. |
| `stream` | `bool` | Stream the response (Default: False). |
| `timeout` | `float` | Max seconds to wait for a response (Default: 30). |
| `max_retries` | `int` | Maximum retry attempts on failure (Default: 0). |
| `retry_strategy` | `RetryStrategy` | Backoff class instance (e.g., `ExponentialBackoff`). |
| `cancel_token` | `CancelToken` | Token to cancel the request mid-flight. |

---

## Error Handling

`axiospy` provides strongly typed exceptions extending from `AxiospyError`. The `Response` object provides a `.raise_for_status()` method exactly like `requests`.

```python
import axiospy

try:
    response = axiospy.get("https://httpbin.org/status/404")
    response.raise_for_status()
except axiospy.HTTPStatusError as e:
    print(f"Request failed with status code {e.response.status_code}")
except axiospy.TimeoutError:
    print("Request timed out.")
except axiospy.NetworkError:
    print("Unable to connect to the server.")
except axiospy.RetryError:
    print("All retry attempts failed.")
except axiospy.CancelError:
    print("Request was manually cancelled.")
except axiospy.AxiospyError as e:
    print(f"A general axiospy error occurred: {e}")
```

---

## Advanced

### Custom Transports

You aren't locked into `httpx`. You can build a custom transport adapter by implementing the `BaseTransport` abstract class.

```python
from axiospy import Axiospy, BaseTransport

class MockTransport(BaseTransport):
    def send(self, request):
        return axiospy.Response(200, {}, {"mock": "data"}, request)

    async def send_async(self, request):
        return self.send(request)

# Pass the custom transport directly to the Axiospy constructor
api = Axiospy(config={"base_url": "mock://"}, transport=MockTransport())
```

---

## License

This project is licensed under the [MIT License](LICENSE).
