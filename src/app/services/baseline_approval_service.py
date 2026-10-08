from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.database.repositories.baseline_governance_repository import BaselineGovernanceRepository
from app.database.repositories.baseline_repository import BaselineRepository
from app.models.graph.approval import Approval
from app.models.graph.enums import (
    ActorType,
    ApprovalDecision,
    GovernanceOperation,
    GovernanceSubjectType,
    RevisionStatus,
)
from app.models.graph.provenance_event import ProvenanceEvent
from app.utils.hashing import sha256_canonical


class BaselineApprovalService:
    """Creates an immutable approval and audit event for a baseline atomically."""

    def __init__(
        self,
        *,
        baseline_repository: BaselineRepository,
        governance_repository: BaselineGovernanceRepository,
    ) -> None:
        self._baseline_repository = baseline_repository
        self._governance_repository = governance_repository

    def approve(
        self,
        *,
        baseline_id: str,
        actor: str,
        actor_type: ActorType,
        comment: str | None = None,
    ) -> tuple[Approval, ProvenanceEvent]:
        if not actor.strip():
            raise ValueError("actor cannot be empty")
        if actor_type is None:
            raise ValueError("actor_type is required")

        baseline = self._baseline_repository.get(baseline_id)
        if baseline is None:
            raise ValueError(f"Baseline not found: {baseline_id}")
        if baseline.status is not RevisionStatus.REVIEW_REQUESTED:
            raise ValueError(
                "Only REVIEW_REQUESTED baselines can be approved: "
                f"{baseline_id}"
            )

        revision_ids = tuple(
            self._baseline_repository.list_revision_ids(baseline_id)
        )
        if not revision_ids:
            raise ValueError(f"Cannot approve an empty baseline: {baseline_id}")

        timestamp = datetime.now(timezone.utc)
        approval = Approval(
            approval_id=f"APR-{uuid4().hex}",
            subject_type=GovernanceSubjectType.BASELINE,
            subject_id=baseline_id,
            revision_id=None,
            record_version=None,
            decision=ApprovalDecision.APPROVED,
            actor=actor,
            actor_type=actor_type,
            timestamp=timestamp,
            comment=comment,
        )

        payload = {
            "operation": GovernanceOperation.BASELINE_APPROVED.value,
            "approval": {
                "approval_id": approval.approval_id,
                "subject_type": approval.subject_type.value,
                "subject_id": approval.subject_id,
                "decision": approval.decision.value,
                "actor": approval.actor,
                "actor_type": approval.actor_type.value,
                "timestamp": approval.timestamp,
                "comment": approval.comment,
            },
            "baseline": {
                "id": baseline.id,
                "title": baseline.title,
                "scope": baseline.scope,
            },
            "revision_ids": list(revision_ids),
        }
        provenance_event = ProvenanceEvent(
            event_id=f"EVT-{uuid4().hex}",
            actor=actor,
            actor_type=actor_type,
            operation=GovernanceOperation.BASELINE_APPROVED,
            timestamp=timestamp,
            subject_type=GovernanceSubjectType.BASELINE,
            subject_id=baseline_id,
            revision_id=None,
            record_version=None,
            previous_revision_id=None,
            previous_version=None,
            payload_hash=sha256_canonical(payload),
            approval_id=approval.approval_id,
        )

        self._governance_repository.approve(
            baseline_id=baseline_id,
            approval=approval,
            provenance_event=provenance_event,
        )
        return approval, provenance_event
