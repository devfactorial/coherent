from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.database.repositories.baseline_repository import BaselineRepository
from app.database.sqlalchemy.models.baseline import (
    BaselineMembershipModel,
    BaselineModel,
)
from app.models.graph.enums import RevisionStatus
from app.models.graph.records import Baseline


class SQLAlchemyBaselineRepository(BaselineRepository):
    """SQLAlchemy read/query persistence for specification baselines."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get(self, baseline_id: str) -> Baseline | None:
        with self._session_factory() as session:
            row = session.get(BaselineModel, baseline_id)
            return self._to_domain(row) if row else None

    def get_latest_approved(self) -> Baseline | None:
        stmt = (
            select(BaselineModel)
            .where(BaselineModel.status == RevisionStatus.APPROVED.value)
            .order_by(BaselineModel.created_at.desc(), BaselineModel.id.desc())
            .limit(1)
        )
        with self._session_factory() as session:
            row = session.scalars(stmt).first()
            return self._to_domain(row) if row else None

    def list_revision_ids(self, baseline_id: str) -> list[str]:
        stmt = (
            select(BaselineMembershipModel.revision_id)
            .where(BaselineMembershipModel.baseline_id == baseline_id)
            .order_by(BaselineMembershipModel.revision_id.asc())
        )
        with self._session_factory() as session:
            return list(session.scalars(stmt).all())

    @staticmethod
    def _to_domain(row: BaselineModel) -> Baseline:
        return Baseline(
            id=row.id,
            title=row.title,
            scope=row.scope,
            status=RevisionStatus(row.status),
        )
