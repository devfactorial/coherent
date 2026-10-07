from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.models.graph.enums import ActorType, ApprovalDecision


@dataclass(frozen=True, kw_only=True)
class Approval:
    """Immutable decision made against one specific record revision."""

    approval_id: str
    record_id: str
    revision_id: str
    record_version: str
    decision: ApprovalDecision
    actor: str
    actor_type: ActorType
    timestamp: datetime
    comment: str | None = None

    def __post_init__(self) -> None:
        if not self.approval_id.strip():
            raise ValueError("approval_id cannot be empty")
        if not self.record_id.strip():
            raise ValueError("record_id cannot be empty")
        if not self.revision_id.strip():
            raise ValueError("revision_id cannot be empty")
        if not self.record_version.strip():
            raise ValueError("record_version cannot be empty")
        if not self.actor.strip():
            raise ValueError("actor cannot be empty")
