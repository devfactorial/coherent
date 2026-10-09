from __future__ import annotations

from dataclasses import dataclass

from app.context.pack.enums import ContextPackPurpose, ContextSelectionBasis
from app.context.pack.models import ContextPack, ContextPackItem
from app.context.pack.relevance import (
    NFRRelevanceAnalyzer,
    OpenAICompatibleNFRRelevanceAnalyzer,
)
from app.database.repositories.baseline_repository import BaselineRepository
from app.database.repositories.graph_repository import GraphRepository
from app.database.repositories.record_repository import RecordRepository
from app.models.graph.edge import GraphEdge
from app.models.graph.enums import ArtifactType, EdgeType, RevisionStatus
from app.models.graph.records import (
    ArtifactRevision,
    Constraint,
    DesignElement,
    Record,
    Requirement,
)
import os

@dataclass(frozen=True)
class _Selected:
    record: Record
    basis: ContextSelectionBasis
    related_via: tuple[str, ...]


class ContextPackService:
    """Build deterministic, governed context from the specification graph."""

    def __init__(
        self,
        *,
        baseline_repository: BaselineRepository,
        record_repository: RecordRepository,
        graph_repository: GraphRepository,
        nfr_relevance_analyzer: NFRRelevanceAnalyzer | None = None,
    ) -> None:
        self._baseline_repository = baseline_repository
        self._record_repository = record_repository
        self._graph_repository = graph_repository
        self._nfr_relevance_analyzer = (
            nfr_relevance_analyzer or OpenAICompatibleNFRRelevanceAnalyzer()
        )

    def build(
        self,
        *,
        target_id: str,
        purpose: ContextPackPurpose,
    ) -> ContextPack:
        """Build a pack for a logical record entity against the latest approved baseline."""
        if not target_id.strip():
            raise ValueError("target_id cannot be empty")

        baseline = self._baseline_repository.get_latest_approved()
        if baseline is None:
            raise LookupError("No approved baseline is available")

        baseline_revision_ids = set(
            self._baseline_repository.list_revision_ids(baseline.id)
        )
        if not baseline_revision_ids:
            raise LookupError(
                f"Approved baseline contains no governed revisions: {baseline.id}"
            )

        records = self._load_baseline_records(baseline_revision_ids)
        target = self._resolve_target(target_id, records)

        selected: dict[str, _Selected] = {
            target.meta.revision_id: _Selected(
                record=target,
                basis=ContextSelectionBasis.TARGET,
                related_via=(),
            )
        }
        relationships: dict[str, GraphEdge] = {}

        self._select_direct_context(
            target=target,
            baseline_revision_ids=baseline_revision_ids,
            records=records,
            selected=selected,
            relationships=relationships,
            purpose=purpose,
        )

        self._select_semantically_relevant_nfrs(
            target=target,
            baseline_revision_ids=baseline_revision_ids,
            records=records,
            selected=selected,
            relationships=relationships,
        )

        if purpose is ContextPackPurpose.VERIFICATION:
            self._select_implementation_context(
                target=target,
                baseline_revision_ids=baseline_revision_ids,
                records=records,
                selected=selected,
                relationships=relationships,
            )

        items = tuple(
            ContextPackItem(
                record=item.record,
                basis=item.basis,
                related_via=item.related_via,
            )
            for revision_id, item in selected.items()
            if revision_id != target.meta.revision_id
        )

        return ContextPack(
            purpose=purpose,
            target=ContextPackItem(
                record=target,
                basis=ContextSelectionBasis.TARGET,
            ),
            baseline=baseline,
            items=items,
            relationships=tuple(
                relationships[key] for key in sorted(relationships)
            ),
        )

    def _load_baseline_records(
        self,
        revision_ids: set[str],
    ) -> dict[str, Record]:
        records: dict[str, Record] = {}
        for revision_id in revision_ids:
            record = self._record_repository.get(revision_id)
            if record is None:
                raise ValueError(
                    "Baseline references missing governed record: "
                    f"{revision_id}"
                )
            if record.meta.status is not RevisionStatus.APPROVED:
                raise ValueError(
                    "Approved baseline references a non-approved record: "
                    f"{revision_id} ({record.meta.status.value})"
                )
            records[revision_id] = record
        return records

    @staticmethod
    def _resolve_target(
        target_id: str,
        records: dict[str, Record],
    ) -> Record:
        matches = [
            record
            for record in records.values()
            if record.meta.entity_id == target_id
            or record.meta.revision_id == target_id
        ]
        if not matches:
            raise KeyError(
                f"Target record is not present in the approved baseline: {target_id}"
            )
        if len(matches) == 1:
            return matches[0]

        # A baseline must contain at most one revision for a logical entity.
        # Refuse ambiguity rather than silently choosing a revision.
        raise ValueError(
            f"Target resolves to multiple revisions in baseline: {target_id}"
        )

    def _select_direct_context(
        self,
        *,
        target: Record,
        baseline_revision_ids: set[str],
        records: dict[str, Record],
        selected: dict[str, _Selected],
        relationships: dict[str, GraphEdge],
        purpose: ContextPackPurpose,
    ) -> None:
        target_id = target.meta.revision_id
        edges = self._connected_edges(target_id)

        for edge in edges:
            if not edge.is_active():
                continue
            if edge.source_revision_id not in baseline_revision_ids:
                continue
            if edge.target_revision_id not in baseline_revision_ids:
                continue

            other_id = (
                edge.target_revision_id
                if edge.source_revision_id == target_id
                else edge.source_revision_id
            )
            other = records[other_id]

            include = False
            if edge.edge_type is EdgeType.HAS_ACCEPTANCE:
                include = edge.source_revision_id == target_id
            elif edge.edge_type in {
                EdgeType.CONSTRAINS,
                EdgeType.REALIZES,
                EdgeType.APPLIES_TO,
            }:
                include = True
            elif edge.edge_type in {
                EdgeType.VERIFIES,
                EdgeType.VERIFIED_BY,
                EdgeType.IMPLEMENTATION_OF,
            }:
                include = purpose is ContextPackPurpose.VERIFICATION
            elif edge.edge_type in {EdgeType.ASSESSED_BY}:
                include = isinstance(target, Constraint)
            elif edge.edge_type is EdgeType.SPECIFIED_BY:
                # A design may point to a decision. It is selected when the
                # design itself is selected below.
                include = False
            elif edge.edge_type is EdgeType.EXPOSES:
                include = False

            if include:
                self._add_selected(
                    selected=selected,
                    record=other,
                    basis=ContextSelectionBasis.DIRECT_RELATION,
                    related_via=(edge.edge_type.value,),
                )
                relationships[edge.id] = edge

        # Expand design nodes selected directly from the target.
        design_ids = [
            revision_id
            for revision_id, item in selected.items()
            if (
                isinstance(item.record, DesignElement)
                or (
                    isinstance(item.record, ArtifactRevision)
                    and item.record.artifact_type in {ArtifactType.HLD, ArtifactType.LLD}
                )
            )
        ]
        for design_id in design_ids:
            self._expand_design(
                design_id=design_id,
                baseline_revision_ids=baseline_revision_ids,
                records=records,
                selected=selected,
                relationships=relationships,
            )

        # Constraints selected from the target may point to an NFR and/or
        # to an assessment. This is how the current graph model connects
        # an NFR Requirement to the functional target indirectly.
        constraint_ids = [
            revision_id
            for revision_id, item in selected.items()
            if isinstance(item.record, Constraint)
        ]
        for constraint_id in constraint_ids:
            for edge in self._outgoing_edges(constraint_id):
                if not edge.is_active() or edge.target_revision_id not in baseline_revision_ids:
                    continue
                if edge.edge_type is EdgeType.CONSTRAINS:
                    pass
                elif edge.edge_type is EdgeType.ASSESSED_BY:
                    if purpose is not ContextPackPurpose.VERIFICATION:
                        continue
                else:
                    continue
                related = records[edge.target_revision_id]
                self._add_selected(
                    selected=selected,
                    record=related,
                    basis=ContextSelectionBasis.TRANSITIVE_RELATION,
                    related_via=(edge.edge_type.value,),
                )
                relationships[edge.id] = edge

        # A newly selected design element may itself expose/specify more
        # design context. Keep this bounded to one semantic expansion hop
        # for v1; deeper traversal can become a policy concern later.
        design_ids = [
            revision_id
            for revision_id, item in selected.items()
            if isinstance(item.record, DesignElement)
            or (
                isinstance(item.record, ArtifactRevision)
                and item.record.artifact_type in {ArtifactType.HLD, ArtifactType.LLD}
            )
        ]
        for design_id in design_ids:
            self._expand_design(
                design_id=design_id,
                baseline_revision_ids=baseline_revision_ids,
                records=records,
                selected=selected,
                relationships=relationships,
            )

    def _expand_design(
        self,
        *,
        design_id: str,
        baseline_revision_ids: set[str],
        records: dict[str, Record],
        selected: dict[str, _Selected],
        relationships: dict[str, GraphEdge],
    ) -> None:
        for edge in self._outgoing_edges(design_id):
            if not edge.is_active():
                continue
            if edge.target_revision_id not in baseline_revision_ids:
                continue
            if edge.edge_type not in {
                EdgeType.SPECIFIED_BY,
                EdgeType.EXPOSES,
            }:
                continue
            self._add_selected(
                selected=selected,
                record=records[edge.target_revision_id],
                basis=ContextSelectionBasis.TRANSITIVE_RELATION,
                related_via=(edge.edge_type.value,),
            )
            relationships[edge.id] = edge

   
    def _select_semantically_relevant_nfrs(
        self,
        *,
        target: Record,
        baseline_revision_ids: set[str],
        records: dict[str, Record],
        selected: dict[str, _Selected],
        relationships: dict[str, GraphEdge],
    ) -> None:
        """Select relevant NFRs using the optional LLM, including them by default."""
        if (
            not isinstance(target, Requirement)
            or target.meta.entity_id.upper().startswith("NFR-")
        ):
            return

        llm_enabled = (
            os.getenv("AIGOV_LLM_NFR_RELEVANCE_ENABLED", "false")
            .strip()
            .lower()
            in {"1", "true", "yes", "on"}
        )

        context = tuple(item.record for item in selected.values())
        candidates = sorted(
            (
                record
                for record in records.values()
                if isinstance(record, Requirement)
                and record.meta.entity_id.upper().startswith("NFR-")
                and record.meta.revision_id != target.meta.revision_id
                and record.meta.revision_id not in selected
            ),
            key=lambda record: record.meta.entity_id,
        )

        for nfr in candidates:
            if llm_enabled:
                assessment = self._nfr_relevance_analyzer.assess(
                    target=target,
                    context=context,
                    nfr=nfr,
                )
                if assessment.decision == "NOT_RELEVANT":
                    continue

                decision = assessment.decision
                rationale = assessment.rationale
            else:
                decision = "DEFAULT_INCLUDED"
                rationale = (
                    "LLM relevance analysis disabled; "
                    "NFR included by default."
                )

            self._add_selected(
                selected=selected,
                record=nfr,
                basis=ContextSelectionBasis.SEMANTIC_RELEVANCE,
                related_via=(
                    f"NFR_{decision}",
                    rationale,
                ),
            )

            # Include constraints that explicitly constrain this NFR.
            # Edge direction: constraint -> NFR.
            for edge in self._connected_edges(nfr.meta.revision_id):
                if not edge.is_active() or edge.edge_type is not EdgeType.CONSTRAINS:
                    continue
                if edge.target_revision_id != nfr.meta.revision_id:
                    continue
                if edge.source_revision_id not in baseline_revision_ids:
                    continue

                constraint = records[edge.source_revision_id]
                self._add_selected(
                    selected=selected,
                    record=constraint,
                    basis=ContextSelectionBasis.SEMANTIC_RELEVANCE,
                    related_via=(
                        "CONSTRAINS",
                        f"APPLIES_TO_{nfr.meta.entity_id}",
                    ),
                )
                relationships[edge.id] = edge


    def _select_implementation_context(
        self,
        *,
        target: Record,
        baseline_revision_ids: set[str],
        records: dict[str, Record],
        selected: dict[str, _Selected],
        relationships: dict[str, GraphEdge],
    ) -> None:
        for edge in self._connected_edges(target.meta.revision_id):
            if not edge.is_active():
                continue
            if edge.edge_type is not EdgeType.IMPLEMENTATION_OF:
                continue
            other_id = (
                edge.source_revision_id
                if edge.target_revision_id == target.meta.revision_id
                else edge.target_revision_id
            )
            if other_id not in baseline_revision_ids:
                continue
            self._add_selected(
                selected=selected,
                record=records[other_id],
                basis=ContextSelectionBasis.DIRECT_RELATION,
                related_via=(edge.edge_type.value,),
            )
            relationships[edge.id] = edge

    def _connected_edges(self, revision_id: str) -> list[GraphEdge]:
        return [
            *self._graph_repository.get_outgoing_edges(revision_id),
            *self._graph_repository.get_incoming_edges(revision_id),
        ]

    def _outgoing_edges(self, revision_id: str) -> list[GraphEdge]:
        return self._graph_repository.get_outgoing_edges(revision_id)

    @staticmethod
    def _add_selected(
        *,
        selected: dict[str, _Selected],
        record: Record,
        basis: ContextSelectionBasis,
        related_via: tuple[str, ...],
    ) -> None:
        revision_id = record.meta.revision_id
        existing = selected.get(revision_id)
        if existing is None:
            selected[revision_id] = _Selected(
                record=record,
                basis=basis,
                related_via=related_via,
            )
            return

        if existing.basis is ContextSelectionBasis.TRANSITIVE_RELATION and basis is ContextSelectionBasis.DIRECT_RELATION:
            selected[revision_id] = _Selected(
                record=record,
                basis=basis,
                related_via=tuple(dict.fromkeys(existing.related_via + related_via)),
            )
