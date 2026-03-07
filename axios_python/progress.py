# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "ProgressEvent",
]


@dataclass
class ProgressEvent:
    loaded: int
    total: int | None

    @property
    def progress_percent(self) -> float | None:
        if self.total is None or self.total == 0:
            return None
        return round((self.loaded / self.total) * 100, 2)
