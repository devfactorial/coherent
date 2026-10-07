from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any


def to_canonical_data(value: Any) -> Any:
    """
    Convert supported domain objects into deterministic JSON-compatible data.

    Rules:

    - dataclasses -> dictionaries
    - enums -> their values
    - datetime/date -> ISO-8601 strings
    - dictionaries -> recursively normalized
    - lists/tuples -> recursively normalized
    - primitive values -> unchanged
    """

    if is_dataclass(value):
        return {
            field.name: to_canonical_data(
                getattr(value, field.name)
            )
            for field in fields(value)
        }

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        value = value.astimezone(timezone.utc)

        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): to_canonical_data(item)
            for key, item in sorted(
                value.items(),
                key=lambda item: str(item[0]),
            )
        }

    if isinstance(value, (list, tuple)):
        return [
            to_canonical_data(item)
            for item in value
        ]

    if value is None or isinstance(
        value,
        (str, int, float, bool),
    ):
        return value

    raise TypeError(
        f"Unsupported value for canonical serialization: "
        f"{type(value).__name__}"
    )


def canonical_json(value: Any) -> str:
    """
    Produce deterministic JSON representation.
    """

    normalized = to_canonical_data(value)

    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )