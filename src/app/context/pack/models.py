from __future__ import annotations

from dataclasses import dataclass, field

from app.models.graph.edge import GraphEdge
from app.models.graph.records import Baseline, Record

from .enums import ContextPackPurpose, ContextSelectionBasis


@dataclass(frozen=True, kw_only=True)
class ContextPackItem:
    """One governed record selected into a Context Pack."""

    record: Record
    basis: ContextSelectionBasis
    related_via: tuple[str, ...] = ()


@dataclass(frozen=True, kw_only=True)
class ContextPack:
    """Structured, task-scoped projection of the governed specification graph."""

    purpose: ContextPackPurpose
    target: ContextPackItem
    baseline: Baseline
    items: tuple[ContextPackItem, ...] = field(default_factory=tuple)
    relationships: tuple[GraphEdge, ...] = field(default_factory=tuple)

    @property
    def record_revision_ids(self) -> tuple[str, ...]:
        return tuple(item.record.meta.revision_id for item in self.items)

    @property
    def record_entity_ids(self) -> tuple[str, ...]:
        return tuple(item.record.meta.entity_id for item in self.items)
