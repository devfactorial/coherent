from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.database.repositories.approval_repository import ApprovalRepository
from app.models.graph.approval import Approval
from app.models.graph.enums import (
    ActorType,
    ApprovalDecision,
    GovernanceSubjectType,
)
from app.models.graph.records import Record


class ApprovalService:
    """Creates immutable approval decisions for exact record revisions."""

    def __init__(self, repository: ApprovalRepository) -> None:
        self._repository = repository

    def approve(
        self,
        *,
        record: Record,
        actor: str,
        actor_type: ActorType,
        comment: str | None = None,
    ) -> Approval:
        return self._decide(
            record=record,
            actor=actor,
            actor_type=actor_type,
            decision=ApprovalDecision.APPROVED,
            comment=comment,
        )

    def reject(
        self,
        *,
        record: Record,
        actor: str,
        actor_type: ActorType,
        comment: str | None = None,
    ) -> Approval:
        return self._decide(
            record=record,
            actor=actor,
            actor_type=actor_type,
            decision=ApprovalDecision.REJECTED,
            comment=comment,
        )

    def get(self, approval_id: str) -> Approval | None:
        return self._repository.get(approval_id)

    def list_for_revision(self, revision_id: str) -> list[Approval]:
        return self._repository.list_for_revision(revision_id)

    def _decide(
        self,
        *,
        record: Record,
        actor: str,
        actor_type: ActorType,
        decision: ApprovalDecision,
        comment: str | None,
    ) -> Approval:
        if not actor.strip():
            raise ValueError("actor cannot be empty")
        if actor_type is None:
            raise ValueError("actor_type is required")

        approval = Approval(
            approval_id=f"APR-{uuid4().hex}",
            subject_type=GovernanceSubjectType.RECORD_REVISION,
            subject_id=record.meta.entity_id,
            revision_id=record.meta.revision_id,
            record_version=record.meta.version,
            decision=decision,
            actor=actor,
            actor_type=actor_type,
            timestamp=datetime.now(timezone.utc),
            comment=comment,
        )
        self._repository.save(approval)
        return approval
