Perfect — let’s treat this like a **real production OSS product**.

Below is a **complete PRD + architecture + folder structure + coding standards** for building an Axios-like Python HTTP client.

---

# Product Name

`axiospy`

---

# 1. Product Requirement Document (PRD)

## 1.1 Vision

Provide a **developer-experience-first HTTP client for Python** inspired by Axios.

Not just a transport tool — but a **network orchestration layer**.

Goal:

Make API calls in Python feel like modern frontend networking.

---

## 1.2 Problem Statement

Python HTTP ecosystem is transport-focused:

| Library  | Focus         |
| -------- | ------------- |
| requests | simplicity    |
| httpx    | async support |
| aiohttp  | performance   |

Missing:

* request lifecycle hooks
* middleware chain
* interceptor model
* instance isolation
* cancellation
* unified sync + async DX

Modern apps need:

* observability
* auth injection
* retries
* caching
* request tracing

Today this is scattered across:

```
requests + tenacity + custom wrapper + logging
```

We unify this.

---

## 1.3 Goals

### Functional Goals

* Instance-based client
* Request / Response interceptors
* Middleware pipeline
* Retry engine
* Cancellation tokens
* Config merging
* Plugin system
* Sync + Async support
* Transport abstraction

---

### Non-Goals (V1)

* Browser compatibility
* WebSocket support
* HTTP server functionality
* GraphQL client

---

# 2. User Personas

## SDK Builder

Needs:

* auth injection
* retry
* tracing

## Platform Engineer

Needs:

* observability
* middleware

## CLI Developer

Needs:

* cancellation
* timeout

## Microservices Team

Needs:

* config isolation

---

# 3. Core Features

## 3.1 Client Instance

```python
api = axiospy.create({
    "base_url": "...",
    "timeout": 5
})
```

Isolated state.

---

## 3.2 HTTP Methods

```
get
post
put
patch
delete
request
```

---

## 3.3 Interceptors

```
request.use()
response.use()
error.use()
```

---

## 3.4 Middleware

Pipeline execution model:

```
middleware → interceptors → transport
```

---

## 3.5 Retry Engine

Configurable:

* retries
* strategy
* retry_on

---

## 3.6 Cancellation

Token-based.

---

## 3.7 Plugins

Examples:

* cache
* logger
* auth
* tracing

---

## 3.8 Transport Layer

Swappable:

Default:

* httpx

Optional:

* aiohttp
* urllib3

---

# 4. Public API

## Instance

```python
api = axiospy.create(config)
```

---

## Request

```python
res = api.get("/users")
```

---

## Async

```python
res = await api.get("/users")
```

---

## Interceptors

```python
api.interceptors.request.use(fn)
api.interceptors.response.use(fn)
```

---

## Middleware

```python
api.use(middleware)
```

---

## Cancel

```python
token = axiospy.CancelToken()
api.get("/slow", cancel_token=token)
```

---

# 5. System Architecture

```
Client
 ├── Config Manager
 ├── Middleware Pipeline
 ├── Interceptor Manager
 ├── Retry Engine
 ├── Cancellation Engine
 ├── Transport Adapter
 └── Plugin Manager
```

---

# 6. Execution Flow

```
User Call
   ↓
Config Merge
   ↓
Middleware
   ↓
Request Interceptors
   ↓
Retry Wrapper
   ↓
Transport
   ↓
Response Interceptors
   ↓
Return Response
```

---

# 7. Folder Structure

```
axiospy/
│
├── __init__.py
├── client.py
├── config.py
├── request.py
├── response.py
├── exceptions.py
│
├── interceptors/
│   ├── manager.py
│   └── chain.py
│
├── middleware/
│   ├── manager.py
│   └── pipeline.py
│
├── retry/
│   ├── engine.py
│   └── strategy.py
│
├── cancel/
│   ├── token.py
│   └── exceptions.py
│
├── transport/
│   ├── base.py
│   ├── httpx_adapter.py
│   └── aiohttp_adapter.py
│
├── plugins/
│   ├── logger.py
│   ├── cache.py
│   └── auth.py
│
├── utils/
│   ├── merge.py
│   └── async_utils.py
│
└── defaults.py
```

---

# 8. Core Modules Responsibility

## client.py

* Public entry point
* Instance creation
* Method routing

---

## config.py

* Merge defaults
* Normalize config

---

## interceptors/

* Chain manager
* Execution order

---

## middleware/

* Express-style pipeline

---

## retry/

* Backoff strategies

---

## transport/

* Network adapters

---

## cancel/

* Token lifecycle

---

# 9. Coding Standards

## 9.1 Language

* Python 3.10+

---

## 9.2 Style

Follow:

PEP8 + strict typing

---

## 9.3 Typing

Mandatory:

```
from typing import TypedDict, Callable, Awaitable
```

All public APIs typed.

---

## 9.4 Naming

| Type      | Style      |
| --------- | ---------- |
| Class     | PascalCase |
| Function  | snake_case |
| Private   | _prefix    |
| Constants | UPPER_CASE |

---

## 9.5 File Rules

Each file must have:

* single responsibility
* no circular imports

---

## 9.6 Public API Rule

Only export via:

```
__all__
```

---

## 9.7 Exception Handling

Custom base:

```
AxiospyError
```

Derived:

```
TimeoutError
NetworkError
CancelError
RetryError
```

---

## 9.8 Async Rules

Never mix sync/async logic.

Use:

```
async_utils.run_sync()
```

---

## 9.9 Interceptor Signature

```
Callable[[Config], Config]
Callable[[Response], Response]
```

---

## 9.10 Middleware Signature

```
async def middleware(ctx, next)
```

---

# 10. Design Patterns

| Pattern  | Where        |
| -------- | ------------ |
| Factory  | create()     |
| Adapter  | transport    |
| Chain    | interceptors |
| Pipeline | middleware   |
| Strategy | retry        |
| Observer | cancellation |

---

# 11. Performance Targets

* <= httpx latency overhead
* < 5% interceptor cost
* retry zero overhead when disabled

---

# 12. V1 Release Scope

Must include:

* instance client
* interceptors
* middleware
* retry
* cancellation
* httpx adapter

---

# 13. Future Roadmap

V2:

* cache plugin
* circuit breaker
* tracing

V3:

* rate limiting
* batching

---

# 14. Success Criteria

Adoption by:

* SDK builders
* internal platforms
* AI infra tools

---

# 15. Versioning

Semantic:

```
0.x → unstable
1.0 → production ready
```

---

# 16. Contribution Guidelines

* 100% typed
* test required
* no breaking API without RFC

---

# 17. Testing Strategy

Use:

```
pytest
respx (mock transport)
```

---

# Done

You now have a **production-grade blueprint**.


