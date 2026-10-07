from __future__ import annotations

import hashlib
from typing import Any

from app.utils.canonical_json import canonical_json


def sha256_text(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def sha256_canonical(value: Any) -> str:
    """
    SHA-256 hash of deterministic canonical JSON.
    """

    return sha256_text(
        canonical_json(value)
    )