from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from app.database.repositories.baseline_governance_repository import BaselineGovernanceRepository
from app.database.repositories.baseline_repository import BaselineRepository
from app.models.graph.enums import (
    ActorType,
    GovernanceOperation,
    GovernanceSubjectType,
    RevisionStatus,
)
from app.models.graph.provenance_event import ProvenanceEvent
from app.models.graph.records import Baseline
from app.utils.hashing import sha256_canonical


@dataclass(frozen=True)
class BaselineCreationResult:
    baseline: Baseline
    revision_ids: tuple[str, ...]
    provenance_event: ProvenanceEvent


class BaselineService:
    """Application service for the governed baseline lifecycle."""

    def __init__(
        self,
        *,
        baseline_repository: BaselineRepository,
        governance_repository: BaselineGovernanceRepository,
    ) -> None:
        self._baseline_repository = baseline_repository
        self._governance_repository = governance_repository

    def create(
        self,
        *,
        baseline_id: str,
        title: str,
        scope: str,
        revision_ids: list[str],
        actor: str,
        actor_type: ActorType,
    ) -> BaselineCreationResult:
        self._validate_actor(actor, actor_type)
        if not baseline_id.strip():
            raise ValueError("baseline_id must not be empty.")
        if not title.strip():
            raise ValueError("title must not be empty.")
        if not scope.strip():
            raise ValueError("scope must not be empty.")
        if not revision_ids:
            raise ValueError("A baseline must contain at least one revision.")
        if self._baseline_repository.get(baseline_id) is not None:
            raise ValueError(f"Baseline already exists: {baseline_id}")

        normalized = tuple(sorted(set(revision_ids)))
        baseline = Baseline(
            id=baseline_id,
            title=title,
            scope=scope,
            status=RevisionStatus.DRAFT,
        )
        timestamp = datetime.now(timezone.utc)
        provenance_event = self._event(
            baseline=baseline,
            revision_ids=normalized,
            actor=actor,
            actor_type=actor_type,
            operation=GovernanceOperation.BASELINE_CREATED,
            timestamp=timestamp,
        )

        self._governance_repository.create_draft(
            baseline=baseline,
            revision_ids=list(normalized),
            provenance_event=provenance_event,
        )
        return BaselineCreationResult(
            baseline=baseline,
            revision_ids=normalized,
            provenance_event=provenance_event,
        )

    def request_review(
        self,
        *,
        baseline_id: str,
        actor: str,
        actor_type: ActorType,
    ) -> Baseline:
        self._validate_actor(actor, actor_type)
        baseline = self._require(baseline_id)
        if baseline.status is not RevisionStatus.DRAFT:
            raise ValueError(
                f"Only DRAFT baselines can be submitted for review: {baseline_id}"
            )

        revision_ids = tuple(self._baseline_repository.list_revision_ids(baseline_id))
        if not revision_ids:
            raise ValueError(f"Cannot review an empty baseline: {baseline_id}")

        event = self._event(
            baseline=baseline,
            revision_ids=revision_ids,
            actor=actor,
            actor_type=actor_type,
            operation=GovernanceOperation.BASELINE_REVIEW_REQUESTED,
            timestamp=datetime.now(timezone.utc),
        )
        self._governance_repository.request_review(
            baseline_id=baseline_id,
            provenance_event=event,
        )
        return self._require(baseline_id)


    def supersede(
        self,
        *,
        baseline_id: str,
        actor: str,
        actor_type: ActorType,
    ) -> Baseline:
        self._validate_actor(actor, actor_type)
        baseline = self._require(baseline_id)
        if baseline.status is not RevisionStatus.APPROVED:
            raise ValueError(
                f"Only APPROVED baselines can be superseded: {baseline_id}"
            )

        revision_ids = tuple(self._baseline_repository.list_revision_ids(baseline_id))
        event = self._event(
            baseline=baseline,
            revision_ids=revision_ids,
            actor=actor,
            actor_type=actor_type,
            operation=GovernanceOperation.BASELINE_SUPERSEDED,
            timestamp=datetime.now(timezone.utc),
        )
        self._governance_repository.supersede(
            baseline_id=baseline_id,
            provenance_event=event,
        )
        return self._require(baseline_id)

    def get(self, baseline_id: str) -> Baseline:
        return self._require(baseline_id)

    def get_latest_approved(self) -> Baseline:
        baseline = self._baseline_repository.get_latest_approved()
        if baseline is None:
            raise ValueError("No APPROVED baseline exists.")
        return baseline

    def revision_ids(self, baseline_id: str) -> list[str]:
        self._require(baseline_id)
        return self._baseline_repository.list_revision_ids(baseline_id)

    @staticmethod
    def _event(
        *,
        baseline: Baseline,
        revision_ids: tuple[str, ...],
        actor: str,
        actor_type: ActorType,
        operation: GovernanceOperation,
        timestamp: datetime,
    ) -> ProvenanceEvent:
        payload = {
            "operation": operation.value,
            "baseline": {
                "id": baseline.id,
                "title": baseline.title,
                "scope": baseline.scope,
                "status": baseline.status.value,
            },
            "revision_ids": list(revision_ids),
        }
        return ProvenanceEvent(
            event_id=f"EVT-{uuid4().hex}",
            actor=actor,
            actor_type=actor_type,
            operation=operation,
            timestamp=timestamp,
            subject_type=GovernanceSubjectType.BASELINE,
            subject_id=baseline.id,
            revision_id=None,
            record_version=None,
            previous_revision_id=None,
            previous_version=None,
            payload_hash=sha256_canonical(payload),
        )

    @staticmethod
    def _validate_actor(actor: str, actor_type: ActorType) -> None:
        if not actor.strip():
            raise ValueError("actor cannot be empty")
        if actor_type is None:
            raise ValueError("actor_type is required")

    def _require(self, baseline_id: str) -> Baseline:
        baseline = self._baseline_repository.get(baseline_id)
        if baseline is None:
            raise ValueError(f"Baseline not found: {baseline_id}")
        return baseline
