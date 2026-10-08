from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.models.graph.enums import (
    ActorType,
    ApprovalDecision,
    GovernanceSubjectType,
)


@dataclass(frozen=True, kw_only=True)
class Approval:
    """Immutable governance decision against a governance subject."""

    approval_id: str
    subject_type: GovernanceSubjectType
    subject_id: str
    revision_id: str | None
    record_version: str | None
    decision: ApprovalDecision
    actor: str
    actor_type: ActorType
    timestamp: datetime
    comment: str | None = None

    def __post_init__(self) -> None:
        if not self.approval_id.strip():
            raise ValueError("approval_id cannot be empty")
        if not self.subject_id.strip():
            raise ValueError("subject_id cannot be empty")
        if not self.actor.strip():
            raise ValueError("actor cannot be empty")
        if self.subject_type is GovernanceSubjectType.RECORD_REVISION:
            if not self.revision_id or not self.revision_id.strip():
                raise ValueError(
                    "Record revision approvals require revision_id"
                )
            if not self.record_version or not self.record_version.strip():
                raise ValueError(
                    "Record revision approvals require record_version"
                )
        elif self.subject_type is GovernanceSubjectType.BASELINE:
            if self.revision_id is not None:
                raise ValueError(
                    "Baseline approvals must not carry revision_id"
                )
            if self.record_version is not None:
                raise ValueError(
                    "Baseline approvals must not carry record_version"
                )

    @property
    def record_id(self) -> str:
        """Backward-compatible alias for record-oriented callers."""
        return self.subject_id
