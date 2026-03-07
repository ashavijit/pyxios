# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from axios_python.progress import ProgressEvent

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
    follow_redirects: bool = True
    on_upload_progress: Callable[[ProgressEvent], None] | None = None
    on_download_progress: Callable[[ProgressEvent], None] | None = None
