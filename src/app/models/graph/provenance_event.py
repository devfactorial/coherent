from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.models.graph.enums import (
    ActorType,
    GovernanceOperation,
)


@dataclass(frozen=True, kw_only=True)
class ProvenanceEvent:
    """
    Immutable audit event describing a governed record operation.

    This is distinct from Provenance.

    Provenance answers:
        "Where did this information come from?"

    ProvenanceEvent answers:
        "Who performed this governance operation,
         on which record revision, and what payload was recorded?"
    """

    event_id: str

    actor: str
    actor_type: ActorType
    operation: GovernanceOperation
    timestamp: datetime

    record_id: str
    revision_id: str
    record_version: str
    previous_revision_id: str | None
    previous_version: str | None

    payload_hash: str

    approval_id: str | None = None

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id cannot be empty")

        if not self.actor.strip():
            raise ValueError("actor cannot be empty")

        if not self.record_id.strip():
            raise ValueError("record_id cannot be empty")

        if not self.revision_id.strip():
            raise ValueError("revision_id cannot be empty")

        if not self.record_version.strip():
            raise ValueError("record_version cannot be empty")

        if self.previous_revision_id is None and self.previous_version is not None:
            raise ValueError(
                "previous_version cannot be set when previous_revision_id is None"
            )
        if self.previous_version is None and self.previous_revision_id is not None:
            raise ValueError(
                "previous_revision_id cannot be set when previous_version is None"
            )

        if not self.payload_hash.strip():
            raise ValueError("payload_hash cannot be empty")