from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.graph.approval import Approval


class ApprovalRepository(ABC):
    """Persistence abstraction for immutable approval decisions."""

    @abstractmethod
    def save(self, approval: Approval) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, approval_id: str) -> Approval | None:
        raise NotImplementedError

    @abstractmethod
    def list_for_revision(self, revision_id: str) -> list[Approval]:
        raise NotImplementedError
