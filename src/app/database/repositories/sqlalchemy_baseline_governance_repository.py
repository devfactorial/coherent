from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.database.repositories.baseline_governance_repository import (
    BaselineGovernanceRepository,
)
from app.database.sqlalchemy.models import (
    ApprovalModel,
    BaselineMembershipModel,
    BaselineModel,
    GovernedRecordModel,
    ProvenanceEventModel,
)
from app.models.graph.approval import Approval
from app.models.graph.enums import (
    ApprovalDecision,
    GovernanceSubjectType,
    RevisionStatus,
)
from app.models.graph.provenance_event import ProvenanceEvent
from app.models.graph.records import Baseline


class SQLAlchemyBaselineGovernanceRepository(BaselineGovernanceRepository):
    """Atomic SQLAlchemy persistence for baseline governance operations."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create_draft(
        self,
        *,
        baseline: Baseline,
        revision_ids: list[str],
        provenance_event: ProvenanceEvent,
    ) -> None:
        if baseline.status is not RevisionStatus.DRAFT:
            raise ValueError("Baseline creation requires DRAFT status.")
        self._validate_baseline_event(
            provenance_event,
            baseline.id,
            "BASELINE_CREATED",
        )

        normalized = sorted(set(revision_ids))
        if not normalized:
            raise ValueError("A baseline must contain at least one revision.")

        with self._session_factory() as session:
            with session.begin():
                if session.get(BaselineModel, baseline.id) is not None:
                    raise ValueError(f"Baseline already exists: {baseline.id}")

                rows = session.scalars(
                    select(GovernedRecordModel).where(
                        GovernedRecordModel.revision_id.in_(normalized)
                    )
                ).all()
                found = {row.revision_id for row in rows}
                missing = [rid for rid in normalized if rid not in found]
                if missing:
                    raise ValueError(
                        "Unknown governed revisions: "
                        + ", ".join(missing)
                    )

                session.add(
                    BaselineModel(
                        id=baseline.id,
                        title=baseline.title,
                        scope=baseline.scope,
                        status=baseline.status.value,
                    )
                )
                session.flush()

                session.add_all(
                    [
                        BaselineMembershipModel(
                            baseline_id=baseline.id,
                            revision_id=revision_id,
                        )
                        for revision_id in normalized
                    ]
                )

                session.add(self._provenance_row(provenance_event))

    def request_review(
        self,
        *,
        baseline_id: str,
        provenance_event: ProvenanceEvent,
    ) -> None:
        self._validate_baseline_event(
            provenance_event,
            baseline_id,
            "BASELINE_REVIEW_REQUESTED",
        )

        with self._session_factory() as session:
            with session.begin():
                row = session.get(BaselineModel, baseline_id)
                if row is None:
                    raise ValueError(f"Baseline not found: {baseline_id}")
                if row.status != RevisionStatus.DRAFT.value:
                    raise ValueError(
                        "Only DRAFT baselines can be submitted for review: "
                        f"{baseline_id}"
                    )

                membership_exists = session.scalar(
                    select(BaselineMembershipModel.revision_id)
                    .where(BaselineMembershipModel.baseline_id == baseline_id)
                    .limit(1)
                )
                if membership_exists is None:
                    raise ValueError(
                        f"Cannot review an empty baseline: {baseline_id}"
                    )

                row.status = RevisionStatus.REVIEW_REQUESTED.value
                session.add(self._provenance_row(provenance_event))

    def approve(
        self,
        *,
        baseline_id: str,
        approval: Approval,
        provenance_event: ProvenanceEvent,
    ) -> None:
        if approval.subject_type is not GovernanceSubjectType.BASELINE:
            raise ValueError("Baseline approval must target a BASELINE subject.")
        if approval.subject_id != baseline_id:
            raise ValueError("Approval subject does not match baseline_id.")
        if approval.decision is not ApprovalDecision.APPROVED:
            raise ValueError("Baseline approval requires APPROVED decision.")
        if provenance_event.subject_type is not GovernanceSubjectType.BASELINE:
            raise ValueError("Baseline provenance must target a BASELINE subject.")
        if provenance_event.subject_id != baseline_id:
            raise ValueError("Provenance subject does not match baseline_id.")
        if provenance_event.approval_id != approval.approval_id:
            raise ValueError("Provenance approval_id must match approval_id.")

        with self._session_factory() as session:
            with session.begin():
                baseline_row = session.get(BaselineModel, baseline_id)
                if baseline_row is None:
                    raise ValueError(f"Baseline not found: {baseline_id}")
                if baseline_row.status != RevisionStatus.REVIEW_REQUESTED.value:
                    raise ValueError(
                        "Only REVIEW_REQUESTED baselines can be approved: "
                        f"{baseline_id}"
                    )

                revision_ids = list(
                    session.scalars(
                        select(BaselineMembershipModel.revision_id)
                        .where(BaselineMembershipModel.baseline_id == baseline_id)
                        .order_by(BaselineMembershipModel.revision_id.asc())
                    ).all()
                )
                if not revision_ids:
                    raise ValueError(
                        f"Cannot approve an empty baseline: {baseline_id}"
                    )

                revision_rows = session.scalars(
                    select(GovernedRecordModel).where(
                        GovernedRecordModel.revision_id.in_(revision_ids)
                    )
                ).all()

                not_approved = sorted(
                    row.revision_id
                    for row in revision_rows
                    if row.status != RevisionStatus.APPROVED.value
                )
                missing = sorted(
                    set(revision_ids)
                    - {row.revision_id for row in revision_rows}
                )

                if missing:
                    raise ValueError(
                        "Baseline contains missing governed revisions: "
                        + ", ".join(missing)
                    )
                if not_approved:
                    raise ValueError(
                        "All baseline members must be APPROVED before "
                        "the baseline can be approved. Invalid revisions: "
                        + ", ".join(not_approved)
                    )

                session.add(
                    ApprovalModel(
                        approval_id=approval.approval_id,
                        subject_type=approval.subject_type.value,
                        subject_id=approval.subject_id,
                        revision_id=approval.revision_id,
                        record_version=approval.record_version,
                        decision=approval.decision.value,
                        actor=approval.actor,
                        actor_type=approval.actor_type.value,
                        timestamp=approval.timestamp,
                        comment=approval.comment,
                    )
                )
                session.flush()
                session.add(self._provenance_row(provenance_event))
                baseline_row.status = RevisionStatus.APPROVED.value

    def supersede(
        self,
        *,
        baseline_id: str,
        provenance_event: ProvenanceEvent,
    ) -> None:
        self._validate_baseline_event(
            provenance_event,
            baseline_id,
            "BASELINE_SUPERSEDED",
        )

        with self._session_factory() as session:
            with session.begin():
                row = session.get(BaselineModel, baseline_id)
                if row is None:
                    raise ValueError(f"Baseline not found: {baseline_id}")
                if row.status != RevisionStatus.APPROVED.value:
                    raise ValueError(
                        "Only APPROVED baselines can be superseded: "
                        f"{baseline_id}"
                    )
                row.status = RevisionStatus.SUPERSEDED.value
                session.add(self._provenance_row(provenance_event))

    @staticmethod
    def _validate_baseline_event(
        event: ProvenanceEvent,
        baseline_id: str,
        operation_name: str,
    ) -> None:
        if event.subject_type is not GovernanceSubjectType.BASELINE:
            raise ValueError("Baseline lifecycle events require BASELINE subject type.")
        if event.subject_id != baseline_id:
            raise ValueError("Provenance subject does not match baseline_id.")
        if event.operation.value != operation_name:
            raise ValueError(
                f"Expected {operation_name} provenance event, "
                f"got {event.operation.value}."
            )

    @staticmethod
    def _provenance_row(event: ProvenanceEvent) -> ProvenanceEventModel:
        return ProvenanceEventModel(
            event_id=event.event_id,
            actor=event.actor,
            actor_type=event.actor_type.value,
            operation=event.operation.value,
            timestamp=event.timestamp,
            subject_type=event.subject_type.value,
            subject_id=event.subject_id,
            revision_id=event.revision_id,
            record_version=event.record_version,
            previous_revision_id=event.previous_revision_id,
            previous_version=event.previous_version,
            payload_hash=event.payload_hash,
            approval_id=event.approval_id,
        )
