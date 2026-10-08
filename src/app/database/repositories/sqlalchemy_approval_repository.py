from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.database.repositories.approval_repository import ApprovalRepository
from app.database.sqlalchemy.models import ApprovalModel
from app.models.graph.approval import Approval
from app.models.graph.enums import (
    ActorType,
    ApprovalDecision,
    GovernanceSubjectType,
)


class SQLAlchemyApprovalRepository(ApprovalRepository):
    """SQLAlchemy persistence for immutable approvals."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def save(self, approval: Approval) -> None:
        row = ApprovalModel(
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
        with self._session_factory() as session:
            session.add(row)
            session.commit()

    def get(self, approval_id: str) -> Approval | None:
        with self._session_factory() as session:
            row = session.get(ApprovalModel, approval_id)
            return self._to_domain(row) if row else None

    def list_for_revision(self, revision_id: str) -> list[Approval]:
        stmt = (
            select(ApprovalModel)
            .where(
                ApprovalModel.subject_type == GovernanceSubjectType.RECORD_REVISION.value,
                ApprovalModel.revision_id == revision_id,
            )
            .order_by(ApprovalModel.timestamp.asc())
        )
        with self._session_factory() as session:
            return [self._to_domain(row) for row in session.scalars(stmt).all()]

    @staticmethod
    def _to_domain(row: ApprovalModel) -> Approval:
        return Approval(
            approval_id=row.approval_id,
            subject_type=GovernanceSubjectType(row.subject_type),
            subject_id=row.subject_id,
            revision_id=row.revision_id,
            record_version=row.record_version,
            decision=ApprovalDecision(row.decision),
            actor=row.actor,
            actor_type=ActorType(row.actor_type),
            timestamp=row.timestamp,
            comment=row.comment,
        )
