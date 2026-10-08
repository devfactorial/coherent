from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.models.graph.enums import (
    ActorType,
    GovernanceOperation,
    GovernanceSubjectType,
)


@dataclass(frozen=True, kw_only=True)
class ProvenanceEvent:
    """
    Immutable product-owned governance audit event.

    The event may apply to a governed record revision or to a higher-level
    governance aggregate such as a baseline.
    """

    event_id: str
    actor: str
    actor_type: ActorType
    operation: GovernanceOperation
    timestamp: datetime

    subject_type: GovernanceSubjectType
    subject_id: str

    revision_id: str | None
    record_version: str | None
    previous_revision_id: str | None
    previous_version: str | None

    payload_hash: str
    approval_id: str | None = None

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id cannot be empty")
        if not self.actor.strip():
            raise ValueError("actor cannot be empty")
        if not self.subject_id.strip():
            raise ValueError("subject_id cannot be empty")
        if not self.payload_hash.strip():
            raise ValueError("payload_hash cannot be empty")

        if self.subject_type is GovernanceSubjectType.RECORD_REVISION:
            if not self.revision_id or not self.revision_id.strip():
                raise ValueError(
                    "Record revision events require revision_id"
                )
            if not self.record_version or not self.record_version.strip():
                raise ValueError(
                    "Record revision events require record_version"
                )
        elif self.subject_type is GovernanceSubjectType.BASELINE:
            if self.revision_id is not None:
                raise ValueError(
                    "Baseline events must not carry revision_id"
                )
            if self.record_version is not None:
                raise ValueError(
                    "Baseline events must not carry record_version"
                )

        if (
            self.previous_revision_id is None
            and self.previous_version is not None
        ):
            raise ValueError(
                "previous_version cannot be set when previous_revision_id is None"
            )
        if (
            self.previous_version is None
            and self.previous_revision_id is not None
        ):
            raise ValueError(
                "previous_revision_id cannot be set when previous_version is None"
            )

    @property
    def record_id(self) -> str:
        """Backward-compatible alias for record-oriented callers."""
        return self.subject_id
