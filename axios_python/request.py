from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "PreparedRequest",
]


@dataclass
class PreparedRequest:
    """An immutable snapshot of a fully resolved HTTP request."""

    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    data: Any = None
    json: Any = None
    files: Any = None
    stream: bool = False
    timeout: int | float = 30
