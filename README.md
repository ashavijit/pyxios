# axios_python

[![PyPI version](https://img.shields.io/pypi/v/axios_python.svg)](https://pypi.org/project/axios_python/)
[![Python versions](https://img.shields.io/pypi/pyversions/axios_python.svg)](https://pypi.org/project/axios_python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A developer-experience-first HTTP client for Python, heavily inspired by [Axios](https://axios-http.com/).

The Python ecosystem has amazing HTTP transport libraries (`requests`, `httpx`, `aiohttp`), but they are often focused purely on sending requests and getting responses. Modern applications need a **network orchestration layer**—features like request lifecycle hooks, middleware, interceptors, isolated client instances, request cancellation, and unified synchronous/asynchronous developer experience. 

`axios_python` brings the elegant, feature-rich Axios model to Python, built natively on top of `httpx`.

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
pip install axios_python
```

Requires Python 3.10+.

---

## Quick Start

### Basic Synchronous Usage

```python
import axios_python

# Zero-setup module level request
response = axios_python.get("https://httpbin.org/get", params={"query": "python"})

# Or create an isolated instance with default configuration
api = axios_python.create({
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

`axios_python` treats async as a first-class citizen. Just prefix method names with `async_`.

```python
import asyncio
import axios_python

async def fetch_data():
    # Non-blocking async call via instance
    api = axios_python.create({"base_url": "https://httpbin.org"})
    response = await api.async_get("/delay/2")
    
    # Or module level
    response = await axios_python.async_get("https://httpbin.org/delay/2")
    print(response.data)

asyncio.run(fetch_data())
```

### Concurrent Requests

Run multiple requests simultaneously using `all()` and unpack the results cleanly with the `spread()` callback wrapper, just like in JavaScript Axios.

```python
import asyncio
from axios_python import create, all, spread

api = create({"base_url": "https://api.github.com"})

async def fetch_multiple():
    # Fetch user profile and repos concurrently
    results = await all([
        api.async_get("/users/octocat"),
        api.async_get("/users/octocat/repos")
    ])

    @spread
    def process(profile, repos):
        print(f"User: {profile.json()['name']}")
        print(f"Repos: {len(repos.json())}")

    process(results)

asyncio.run(fetch_multiple())
```

### File Uploads

Multipart file uploads are supported out of the box matching the `requests` interface.

```python
with open("report.csv", "rb") as f:
    # Files can be passed as an open file handle or a tuple mapping
    files = {"file": ("report.csv", f, "text/csv")}
    response = axios_python.post("https://httpbin.org/post", files=files)
```

### Streaming Responses

For large files or continuous data streams, use `stream=True`. The response is exposed as a context manager for both sync and async calls.

```python
import axios_python

# Synchronous execution
with axios_python.get("https://httpbin.org/stream-bytes/100", stream=True) as response:
    for chunk in response.iter_bytes(chunk_size=10):
        print(len(chunk))

# Asynchronous execution in an async function
async with await axios_python.async_get("https://.../stream", stream=True) as response:
    async for line in response.aiter_lines():
        print(line)
```

---

## Core Concepts

### Interceptors

Interceptors allow you to tap into the lifecycle of a request or response. They run sequentially.

```python
api = axios_python.create({"base_url": "https://api.myapp.com"})

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

### Data Transformation

In addition to interceptors, you can use `transform_request` and `transform_response` to modify the payload directly before sending or after receiving.

```python
import json

def stringify_json(data, headers):
    if isinstance(data, dict):
        headers['Content-Type'] = 'application/json'
        return json.dumps(data)
    return data

api = axios_python.create({
    "transform_request": [stringify_json]
})

# Dictionary sent will automatically be stringified using our transform
api.post("/submit", data={"key": "value"})
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
from axios_python import ExponentialBackoff

api = axios_python.create({
    "base_url": "https://httpbin.org",
    "max_retries": 3,
    "retry_strategy": ExponentialBackoff(base=1.0, multiplier=2.0, max_delay=10.0),
})
```

By default, this retries on Network Errors and Timeouts.

### Request Cancellation

Use a `CancelToken` to abort long-running requests or cancel requests when a user navigates away.

```python
from axios_python import CancelToken
import threading
import time

token = CancelToken()

def background_fetch():
    try:
        api.get("/delay/10", cancel_token=token)
    except axios_python.CancelError as e:
        print(f"Request aborted: {e}")

threading.Thread(target=background_fetch).start()

time.sleep(1)
token.cancel(reason="User clicked 'Stop'")
```

---

## Plugins

`axios_python` ships with first-party plugins for common use-cases.

### Authentication Plugin

Automatically injects `Authorization` headers. Supports static tokens or dynamic providers.

```python
from axios_python import AuthPlugin

api.plugin(AuthPlugin(scheme="Bearer", token="super-secret-key"))

# Or dynamically fetch it:
# api.plugin(AuthPlugin(token_provider=lambda: get_fresh_token()))
```

### Cache Plugin

In-memory TTL cache for `GET` requests to reduce redundant network load.

```python
from axios_python import CachePlugin

# Cache GET responses for 120 seconds, max 256 items
api.plugin(CachePlugin(ttl=120, max_size=256))
```

### Logger Plugin

Standardized `logging` for requests and responses out of the box.

```python
import logging
from axios_python import LoggerPlugin

logging.basicConfig(level=logging.INFO)
api.plugin(LoggerPlugin(level=logging.INFO))
```

---

## Configuration Reference

You can pass the following properties to `axios_python.create(config)` or as overrides to individual request methods (`api.get("/url", **kwargs)`):

| Property | Type | Description |
|----------|------|-------------|
| `base_url` | `str` | Base URL attached to relative paths. |
| `method` | `str` | HTTP Method (e.g., `"GET"`, `"POST"`, `"HEAD"`, `"OPTIONS"`). |
| `url` | `str` | The target path or absolute URL. |
| `headers` | `dict` | Dictionary of HTTP headers. |
| `params` | `dict` | URL Query parameters. |
| `data` | `Any` | Request body content (raw). |
| `json` | `Any` | Request body content (automatically serialized to JSON). |
| `files` | `Any` | Multipart-encoded files dictionary. |
| `stream` | `bool` | Stream the response (Default: False). |
| `timeout` | `float` | Max seconds to wait for a response (Default: 30). |
| `follow_redirects` | `bool` | Whether to automatically follow HTTP redirects (Default: True). |
| `transform_request` | `list[Callable]`| Functions to manipulate data/headers before sending. |
| `transform_response` | `list[Callable]`| Functions to manipulate response data before returning. |
| `max_retries` | `int` | Maximum retry attempts on failure (Default: 0). |
| `retry_strategy` | `RetryStrategy` | Backoff class instance (e.g., `ExponentialBackoff`). |
| `cancel_token` | `CancelToken` | Token to cancel the request mid-flight. |

---

## Error Handling

`axios_python` provides strongly typed exceptions extending from `AxiosPythonError`. The `Response` object provides a `.raise_for_status()` method exactly like `requests`.

```python
import axios_python

try:
    response = axios_python.get("https://httpbin.org/status/404")
    response.raise_for_status()
except axios_python.HTTPStatusError as e:
    print(f"Request failed with status code {e.response.status_code}")
except axios_python.TimeoutError:
    print("Request timed out.")
except axios_python.NetworkError:
    print("Unable to connect to the server.")
except axios_python.RetryError:
    print("All retry attempts failed.")
except axios_python.CancelError:
    print("Request was manually cancelled.")
except axios_python.AxiosPythonError as e:
    print(f"A general axios_python error occurred: {e}")
```

---

## Advanced

### Custom Transports

You aren't locked into `httpx`. You can build a custom transport adapter by implementing the `BaseTransport` abstract class.

```python
from axios_python import AxiosPython, BaseTransport

class MockTransport(BaseTransport):
    def send(self, request):
        return axios_python.Response(200, {}, {"mock": "data"}, request)

    async def send_async(self, request):
        return self.send(request)

# Pass the custom transport directly to the AxiosPython constructor
api = AxiosPython(config={"base_url": "mock://"}, transport=MockTransport())
```

---

## License

This project is licensed under the [MIT License](LICENSE).
