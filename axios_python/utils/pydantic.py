# Copyright (c) 2026 Avijit
# Licensed under the MIT License.

from __future__ import annotations

import sys
from typing import Any, TypeVar

HAS_PYDANTIC = False
try:
    import pydantic
    HAS_PYDANTIC = True
except ImportError:
    pass

T = TypeVar("T")

def parse_model(model_cls: type[T], data: Any) -> T | Any:
    """Safely parse a dictionary or list into a Pydantic model.
    Falls back to returning data if Pydantic isn't installed or model_cls isn't a pydantic model.
    """
    if not HAS_PYDANTIC:
        return data

    if hasattr(pydantic, "VERSION") and pydantic.VERSION.startswith("2."):
        if isinstance(model_cls, type) and issubclass(model_cls, pydantic.BaseModel):
            return model_cls.model_validate(data)
        from pydantic import TypeAdapter
        try:
            return TypeAdapter(model_cls).validate_python(data)
        except Exception:
            return data

    if isinstance(model_cls, type) and issubclass(model_cls, getattr(pydantic, "BaseModel", type(None))):
        import typing
        return typing.cast(Any, model_cls).parse_obj(data)
    
    if getattr(pydantic, "parse_obj_as", None):
        try:
            return pydantic.parse_obj_as(model_cls, data)
        except Exception:
            pass

    return data
