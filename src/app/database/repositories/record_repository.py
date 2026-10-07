from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.graph.records import Record


class RecordRepository(ABC):
    """
    Persistence abstraction for canonical governed records.

    A record is identified logically by entity_id and physically by
    revision_id.

    This repository is the authoritative structured state for governed
    records.
    """

    @abstractmethod
    def save(
        self,
        record: Record,
    ) -> None:
        """
        Persist one immutable record revision.
        """
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        revision_id: str,
    ) -> Record | None:
        """
        Retrieve a specific revision.
        """
        raise NotImplementedError

    @abstractmethod
    def get_latest(
        self,
        entity_id: str,
    ) -> Record | None:
        """
        Retrieve the latest revision of a logical record.
        """
        raise NotImplementedError

    @abstractmethod
    def list_revisions(
        self,
        entity_id: str,
    ) -> list[Record]:
        """
        Retrieve all revisions for a logical record in ascending
        creation order.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        revision_id: str,
    ) -> None:
        """
        Delete a specific revision.

        Normally governed records should be immutable, so this operation
        should be used only for administrative/test scenarios.
        """
        raise NotImplementedError
    
    