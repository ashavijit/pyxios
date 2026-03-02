from __future__ import annotations

from typing import Any

__all__ = [
    "deep_merge",
]


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge two dictionaries.

    Values in *override* take precedence. Nested dicts are merged recursively;
    all other types are replaced outright.

    Args:
        base: The base dictionary.
        override: The dictionary whose values take priority.

    Returns:
        A new dictionary containing the merged result.
    """
    result = dict(base)
    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
