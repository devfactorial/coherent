from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.graph.records import Baseline


class BaselineRepository(ABC):
    """Read/query boundary for governed specification baselines."""

    @abstractmethod
    def get(self, baseline_id: str) -> Baseline | None:
        raise NotImplementedError

    @abstractmethod
    def get_latest_approved(self) -> Baseline | None:
        raise NotImplementedError

    @abstractmethod
    def list_revision_ids(self, baseline_id: str) -> list[str]:
        raise NotImplementedError
