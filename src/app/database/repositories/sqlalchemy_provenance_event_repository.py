# src/app/database/repositories/sqlalchemy_provenance_event_repository.py

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.database.repositories.provenance_event_repository import (
    ProvenanceEventRepository,
)
from app.database.sqlalchemy.models import ProvenanceEventModel
from app.models.graph.enums import (
    ActorType,
    GovernanceOperation,
)
from app.models.graph.provenance_event import (
    ProvenanceEvent,
)


class SQLAlchemyProvenanceEventRepository(
    ProvenanceEventRepository
):
    """SQLAlchemy persistence for append-only audit events."""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
    ) -> None:
        self._session_factory = session_factory

    def append(
        self,
        event: ProvenanceEvent,
    ) -> None:
        row = ProvenanceEventModel(
            event_id=event.event_id,
            actor=event.actor,
            actor_type=event.actor_type.value,
            operation=event.operation.value,
            timestamp=event.timestamp,
            record_id=event.record_id,
            revision_id=event.revision_id,
            record_version=event.record_version,
            previous_revision_id=event.previous_revision_id,
            previous_version=event.previous_version,
            payload_hash=event.payload_hash,
            approval_id=event.approval_id,
        )

        with self._session_factory() as session:
            session.add(row)
            session.commit()

    def get(
        self,
        event_id: str,
    ) -> ProvenanceEvent | None:
        with self._session_factory() as session:
            row = session.get(
                ProvenanceEventModel,
                event_id,
            )

            if row is None:
                return None

            return self._to_domain(row)

    def list_for_record(
        self,
        record_id: str,
    ) -> list[ProvenanceEvent]:
        stmt = (
            select(ProvenanceEventModel)
            .where(
                ProvenanceEventModel.record_id == record_id
            )
            .order_by(
                ProvenanceEventModel.timestamp.asc()
            )
        )

        with self._session_factory() as session:
            rows = session.scalars(stmt).all()

            return [
                self._to_domain(row)
                for row in rows
            ]

    def list_all(
        self,
    ) -> list[ProvenanceEvent]:
        stmt = (
            select(ProvenanceEventModel)
            .order_by(
                ProvenanceEventModel.timestamp.asc()
            )
        )

        with self._session_factory() as session:
            rows = session.scalars(stmt).all()

            return [
                self._to_domain(row)
                for row in rows
            ]

    @staticmethod
    def _to_domain(
        row: ProvenanceEventModel,
    ) -> ProvenanceEvent:
        return ProvenanceEvent(
            event_id=row.event_id,
            actor=row.actor,
            actor_type=ActorType(row.actor_type),
            operation=GovernanceOperation(row.operation),
            timestamp=row.timestamp,
            record_id=row.record_id,
            revision_id=row.revision_id,
            record_version=row.record_version,
            previous_revision_id=row.previous_revision_id,
            previous_version=row.previous_version,
            payload_hash=row.payload_hash,
            approval_id=row.approval_id,
        )