from __future__ import annotations

from datetime import datetime, timezone

from app.models.graph.enums import (
    ProvenanceMethod,
    ProvenanceSourceType,
)
from app.models.graph.records import (
    Provenance,
    Record,
    RevisionMeta,
)
from app.models.graph.enums import AssertionKind, RevisionStatus


class DefaultProvenanceService:

    def create(
        self,
        *,
        record: Record,
        source_type: ProvenanceSourceType,
        source_id: str,
        method: ProvenanceMethod,
        description: str | None = None,
        source_hash: str | None = None,
        actor_id: str | None = None,
        confidence: float | None = None,
    ) -> Provenance:

        provenance_entity_id = (
            f"PROV-{record.meta.entity_id}"
        )

        provenance_revision_id = (
            f"{provenance_entity_id}-v1"
        )

        meta = RevisionMeta(
            entity_id=provenance_entity_id,
            revision_id=provenance_revision_id,
            version="v1",
            title=(
                f"{record.meta.entity_id} "
                f"provenance"
            ),
            status=RevisionStatus.DRAFT,
            owner_id=actor_id or "system",
            assertion_kind=AssertionKind.SOURCE_QUOTED,
        )

        return Provenance(
            meta=meta,
            source_type=source_type,
            source_id=source_id,
            method=method,
            description=description,
            source_hash=source_hash,
            actor_id=actor_id,
            captured_at=datetime.now(timezone.utc),
            confidence=confidence,
        )