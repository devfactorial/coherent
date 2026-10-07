from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.graph.provenance_event import ProvenanceEvent


class ProvenanceEventRepository(ABC):
    """
    Persistence abstraction for immutable governance audit events.

    Events are append-only.
    """

    @abstractmethod
    def append(
        self,
        event: ProvenanceEvent,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        event_id: str,
    ) -> ProvenanceEvent | None:
        raise NotImplementedError

    @abstractmethod
    def list_for_record(
        self,
        record_id: str,
    ) -> list[ProvenanceEvent]:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[ProvenanceEvent]:
        raise NotImplementedError