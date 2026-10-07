from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.models.graph.record_registry import RECORD_TYPES
from app.database.repositories.record_repository import (
    RecordRepository,
)
from app.database.sqlalchemy.models import GovernedRecordModel
from app.models.graph.enums import (
    ArtifactType,
    AssertionKind,
    AssessmentStage,
    ConstraintType,
    EvidenceType,
    ExecutionMode,
    Priority,
    QualityCategory,
    RevisionStatus,
)
from app.models.graph.records import (
    AcceptanceCriterion,
    ArtifactRevision,
    Assessment,
    AssessmentRun,
    Constraint,
    Decision,
    DesignElement,
    Document,
    DocumentLocation,
    DocumentMembership,
    DocumentRevision,
    Evidence,
    InterfaceContract,
    Record,
    Requirement,
    RevisionMeta,
    TestCase,
)
from app.utils.canonical_json import to_canonical_data



class SQLAlchemyRecordRepository(RecordRepository):
    """
    SQLAlchemy-backed canonical governed-record repository.

    SQLAlchemy stores:
        - governed record metadata
        - serialized canonical record payload

    Database schema is managed by Alembic.
    """

    def __init__(
        self,
        session_factory: sessionmaker[Session],
    ) -> None:
        self._session_factory = session_factory
        
        
    def _record_type(self, record: Record) -> str:
        for record_type, record_class in RECORD_TYPES.items():
            if isinstance(record, record_class):
                return record_type

        raise ValueError(
            f"Unsupported governed record type: "
            f"{type(record).__name__}"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save(
        self,
        record: Record,
    ) -> None:
        payload = to_canonical_data(record)
        meta = record.meta

        record_type=self._record_type(record)

        row = GovernedRecordModel(
            revision_id=meta.revision_id,
            entity_id=meta.entity_id,
            record_type=record_type,
            version=meta.version,
            status=meta.status.value,
            owner_id=meta.owner_id,
            assertion_kind=meta.assertion_kind.value,
            record_json=json.dumps(
                payload,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ),
        )

        with self._session_factory() as session:
            session.add(row)
            session.commit()

    def get(
        self,
        revision_id: str,
    ) -> Record | None:
        with self._session_factory() as session:
            row = session.get(
                GovernedRecordModel,
                revision_id,
            )

            if row is None:
                return None

            return self._deserialize_row(row)

    def get_latest(
        self,
        entity_id: str,
    ) -> Record | None:
        stmt = (
            select(GovernedRecordModel)
            .where(
                GovernedRecordModel.entity_id
                == entity_id
            )
            .order_by(
                GovernedRecordModel.created_at.desc(),
                GovernedRecordModel.revision_id.desc(),
            )
            .limit(1)
        )

        with self._session_factory() as session:
            row = session.scalars(stmt).first()

            if row is None:
                return None

            return self._deserialize_row(row)

    def list_revisions(
        self,
        entity_id: str,
    ) -> list[Record]:
        stmt = (
            select(GovernedRecordModel)
            .where(
                GovernedRecordModel.entity_id
                == entity_id
            )
            .order_by(
                GovernedRecordModel.created_at.asc(),
                GovernedRecordModel.revision_id.asc(),
            )
        )

        with self._session_factory() as session:
            rows = session.scalars(stmt).all()

            return [
                self._deserialize_row(row)
                for row in rows
            ]

    def delete(
        self,
        revision_id: str,
    ) -> None:
        with self._session_factory() as session:
            row = session.get(
                GovernedRecordModel,
                revision_id,
            )

            if row is not None:
                session.delete(row)
                session.commit()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def _deserialize_row(
        self,
        row: GovernedRecordModel,
    ) -> Record:
        record_type = row.record_type

        record_class = RECORD_TYPES.get(
            record_type
        )

        if record_class is None:
            raise ValueError(
                f"Unknown governed record type: "
                f"{record_type}"
            )

        payload = json.loads(
            row.record_json
        )

        return self._deserialize_record(
            payload,
            record_class,
        )

    def _deserialize_record(
        self,
        payload: dict[str, Any],
        record_class: type,
    ) -> Record:
        meta_payload = payload["meta"]

        meta = RevisionMeta(
            entity_id=meta_payload["entity_id"],
            revision_id=meta_payload["revision_id"],
            version=meta_payload["version"],
            title=meta_payload["title"],
            status=RevisionStatus(
                meta_payload["status"]
            ),
            owner_id=meta_payload["owner_id"],
            assertion_kind=AssertionKind(
                meta_payload["assertion_kind"]
            ),
        )

        payload = dict(payload)
        payload["meta"] = meta

        enum_fields: dict[type, dict[str, type]] = {
            ArtifactRevision: {
                "artifact_type": ArtifactType,
                "stage": AssessmentStage,
            },
            Requirement: {
                "priority": Priority,
            },
            Constraint: {
                "constraint_type": ConstraintType,
                "quality_category": QualityCategory,
            },
            Assessment: {
                "execution_mode": ExecutionMode,
                "assessment_stage": AssessmentStage,
            },
            AssessmentRun: {},
            Evidence: {
                "evidence_type": EvidenceType,
            },
        }

        for field_name, enum_type in (
            enum_fields.get(record_class, {})
        ).items():
            value = payload.get(field_name)

            if value is not None:
                payload[field_name] = enum_type(
                    value
                )

        return record_class(
            **payload
        )