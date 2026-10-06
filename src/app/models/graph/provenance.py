from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .records import RevisionMeta


class ProvenanceSourceType(str, Enum):
    USER_INPUT = "USER_INPUT"
    DOCUMENT = "DOCUMENT"
    FILE = "FILE"
    LLM = "LLM"
    TOOL = "TOOL"
    TEST_RUN = "TEST_RUN"
    AUDIT = "AUDIT"
    EXTERNAL_SOURCE = "EXTERNAL_SOURCE"
    


class ProvenanceMethod(str, Enum):
    DIRECT_INPUT = "DIRECT_INPUT"
    QUOTED = "QUOTED"
    EXTRACTED = "EXTRACTED"
    GENERATED = "GENERATED"
    INFERRED = "INFERRED"
    DERIVED = "DERIVED"
    VERIFIED = "VERIFIED"


@dataclass(frozen=True, kw_only=True)
class Provenance:
    """
    Records where a graph assertion or artifact came from.

    Provenance is itself revisioned so that changes to provenance
    remain auditable.
    """

    meta: RevisionMeta

    source_type: ProvenanceSourceType
    source_id: str
    method: ProvenanceMethod

    description: str | None = None

    source_hash: str | None = None

    actor_id: str | None = None

    captured_at: datetime | None = None

    confidence: float | None = None

    def __post_init__(self) -> None:
        if not self.source_id:
            raise ValueError("source_id cannot be empty")

        if self.confidence is not None:
            if not 0.0 <= self.confidence <= 1.0:
                raise ValueError(
                    "confidence must be between 0.0 and 1.0"
                )