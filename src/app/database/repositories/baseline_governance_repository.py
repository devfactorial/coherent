from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.graph.approval import Approval
from app.models.graph.provenance_event import ProvenanceEvent
from app.models.graph.records import Baseline


class BaselineGovernanceRepository(ABC):
    """Transactional persistence boundary for baseline lifecycle changes."""

    @abstractmethod
    def create_draft(
        self,
        *,
        baseline: Baseline,
        revision_ids: list[str],
        provenance_event: ProvenanceEvent,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def request_review(
        self,
        *,
        baseline_id: str,
        provenance_event: ProvenanceEvent,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def approve(
        self,
        *,
        baseline_id: str,
        approval: Approval,
        provenance_event: ProvenanceEvent,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def supersede(
        self,
        *,
        baseline_id: str,
        provenance_event: ProvenanceEvent,
    ) -> None:
        raise NotImplementedError
