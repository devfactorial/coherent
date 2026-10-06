from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.models.graph.enums import ArtifactType, EdgeType
from app.models.graph.graph import Graph
from app.models.graph.node import GraphNode
from app.models.graph.records import ArtifactRevision, Provenance

from app.models.graph.edge_invariants import (
    ARTIFACT_CONTAINS_TARGETS,
    EDGE_INVARIANTS,
)


class ValidationSeverity(StrEnum):
    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass(frozen=True)
class GraphValidationFinding:
    severity: ValidationSeverity
    code: str
    message: str
    edge_id: str | None = None
    source_revision_id: str | None = None
    target_revision_id: str | None = None


class GraphSemanticValidator:
    """
    Validates semantic invariants of the graph.

    Graph itself validates structural integrity.
    This validator validates domain meaning.

    Validation is intentionally split into:

    1. Edge-level semantic validation
       - source/target kinds
       - self-reference
       - SUPERSEDES semantics
       - CONTAINS semantics

    2. Graph-level governance validation
       - provenance existence
       - provenance direction
       - duplicate provenance relationships
       - provenance isolation
    """

    def validate(self, graph: Graph) -> list[GraphValidationFinding]:
        findings: list[GraphValidationFinding] = []

        # ---------------------------------------------------------------
        # Edge-level validation
        # ---------------------------------------------------------------

        for edge in graph.edges.values():
            source = graph.get_node(edge.source_revision_id)
            target = graph.get_node(edge.target_revision_id)

            if source is None or target is None:
                findings.append(
                    GraphValidationFinding(
                        severity=ValidationSeverity.ERROR,
                        code="GRAPH-001",
                        message=(
                            f"Edge {edge.id} references a missing node."
                        ),
                        edge_id=edge.id,
                        source_revision_id=edge.source_revision_id,
                        target_revision_id=edge.target_revision_id,
                    )
                )
                continue

            findings.extend(
                self._validate_edge(source, target, edge)
            )

        # ---------------------------------------------------------------
        # Graph-level governance validation
        # ---------------------------------------------------------------

        findings.extend(
            self._validate_provenance(graph)
        )

        return findings

    # ===================================================================
    # EDGE VALIDATION
    # ===================================================================

    def _validate_edge(
        self,
        source: GraphNode,
        target: GraphNode,
        edge,
    ) -> list[GraphValidationFinding]:

        findings: list[GraphValidationFinding] = []

        # ---------------------------------------------------------------
        # General self-reference rule
        # ---------------------------------------------------------------

        if source.id == target.id:
            findings.append(
                GraphValidationFinding(
                    severity=ValidationSeverity.ERROR,
                    code="EDGE-001",
                    message=(
                        f"{edge.edge_type.value} cannot reference the "
                        "same revision on both sides."
                    ),
                    edge_id=edge.id,
                    source_revision_id=source.id,
                    target_revision_id=target.id,
                )
            )

            return findings

        # ---------------------------------------------------------------
        # SUPERSEDES has a special same-entity invariant
        # ---------------------------------------------------------------

        if edge.edge_type is EdgeType.SUPERSEDES:
            if not source.is_same_entity(target):
                findings.append(
                    GraphValidationFinding(
                        severity=ValidationSeverity.ERROR,
                        code="EDGE-002",
                        message=(
                            "SUPERSEDES must connect two revisions of "
                            "the same entity."
                        ),
                        edge_id=edge.id,
                        source_revision_id=source.id,
                        target_revision_id=target.id,
                    )
                )

            return findings

        # ---------------------------------------------------------------
        # PROVENANCE_OF has dedicated semantics
        # ---------------------------------------------------------------

        if edge.edge_type is EdgeType.PROVENANCE_OF:
            findings.extend(
                self._validate_provenance_edge(
                    source,
                    target,
                    edge,
                )
            )

            return findings

        # ---------------------------------------------------------------
        # CONTAINS has artifact-specific rules
        # ---------------------------------------------------------------

        if edge.edge_type is EdgeType.CONTAINS:
            findings.extend(
                self._validate_contains(
                    source,
                    target,
                    edge,
                )
            )

            return findings

        # ---------------------------------------------------------------
        # Generic source/target invariant
        # ---------------------------------------------------------------

        invariant = EDGE_INVARIANTS.get(edge.edge_type)

        if invariant is None:
            findings.append(
                GraphValidationFinding(
                    severity=ValidationSeverity.WARNING,
                    code="EDGE-003",
                    message=(
                        f"No semantic invariant is defined for "
                        f"{edge.edge_type.value}."
                    ),
                    edge_id=edge.id,
                    source_revision_id=source.id,
                    target_revision_id=target.id,
                )
            )

            return findings

        if source.kind not in invariant.source_kinds:
            findings.append(
                GraphValidationFinding(
                    severity=ValidationSeverity.ERROR,
                    code="EDGE-004",
                    message=(
                        f"{edge.edge_type.value} requires source kind "
                        f"to be one of "
                        f"{sorted(invariant.source_kinds)}, "
                        f"but got {source.kind}."
                    ),
                    edge_id=edge.id,
                    source_revision_id=source.id,
                    target_revision_id=target.id,
                )
            )

        if target.kind not in invariant.target_kinds:
            findings.append(
                GraphValidationFinding(
                    severity=ValidationSeverity.ERROR,
                    code="EDGE-005",
                    message=(
                        f"{edge.edge_type.value} requires target kind "
                        f"to be one of "
                        f"{sorted(invariant.target_kinds)}, "
                        f"but got {target.kind}."
                    ),
                    edge_id=edge.id,
                    source_revision_id=source.id,
                    target_revision_id=target.id,
                )
            )

        return findings

    # ===================================================================
    # PROVENANCE VALIDATION
    # ===================================================================

    def _validate_provenance(
        self,
        graph: Graph,
    ) -> list[GraphValidationFinding]:

        findings: list[GraphValidationFinding] = []

        provenance_nodes: dict[str, GraphNode] = {}
        governed_nodes: dict[str, GraphNode] = {}

        for node in graph.nodes.values():
            if node.kind == "PROVENANCE":
                provenance_nodes[node.id] = node
            else:
                governed_nodes[node.id] = node

        # ---------------------------------------------------------------
        # Every provenance node must actually contain Provenance
        # ---------------------------------------------------------------

        for node in provenance_nodes.values():

            if not isinstance(node.record, Provenance):
                findings.append(
                    GraphValidationFinding(
                        severity=ValidationSeverity.ERROR,
                        code="PROV-001",
                        message=(
                            f"Node {node.id} is classified as PROVENANCE "
                            "but does not contain a Provenance record."
                        ),
                        source_revision_id=node.id,
                    )
                )

        # ---------------------------------------------------------------
        # Track PROVENANCE_OF relationships
        # ---------------------------------------------------------------

        provenance_targets: dict[str, list[str]] = {}

        for edge in graph.edges.values():

            if edge.edge_type is not EdgeType.PROVENANCE_OF:
                continue

            provenance_targets.setdefault(
                edge.source_revision_id,
                [],
            ).append(
                edge.target_revision_id
            )

        # ---------------------------------------------------------------
        # Every provenance node must have exactly one target
        # ---------------------------------------------------------------

        for provenance_id in provenance_nodes:

            targets = provenance_targets.get(
                provenance_id,
                [],
            )

            if not targets:
                findings.append(
                    GraphValidationFinding(
                        severity=ValidationSeverity.ERROR,
                        code="PROV-002",
                        message=(
                            f"Provenance node {provenance_id} does not "
                            "have a PROVENANCE_OF relationship."
                        ),
                        source_revision_id=provenance_id,
                    )
                )

                continue

            if len(targets) > 1:
                findings.append(
                    GraphValidationFinding(
                        severity=ValidationSeverity.ERROR,
                        code="PROV-003",
                        message=(
                            f"Provenance node {provenance_id} has "
                            f"{len(targets)} PROVENANCE_OF targets; "
                            "exactly one is required."
                        ),
                        source_revision_id=provenance_id,
                    )
                )

        # ---------------------------------------------------------------
        # Every governed node must have provenance
        # ---------------------------------------------------------------

        targets_with_provenance: set[str] = set()

        for targets in provenance_targets.values():
            targets_with_provenance.update(targets)

        for node_id, node in governed_nodes.items():

            if node_id not in targets_with_provenance:
                findings.append(
                    GraphValidationFinding(
                        severity=ValidationSeverity.ERROR,
                        code="PROV-004",
                        message=(
                            f"Governed node {node_id} has no "
                            "PROVENANCE_OF relationship."
                        ),
                        target_revision_id=node_id,
                    )
                )

        # ---------------------------------------------------------------
        # A governed node must not have multiple provenance records
        # ---------------------------------------------------------------

        provenance_count_by_target: dict[str, int] = {}

        for targets in provenance_targets.values():
            for target_id in targets:
                provenance_count_by_target[target_id] = (
                    provenance_count_by_target.get(target_id, 0) + 1
                )

        for target_id, count in provenance_count_by_target.items():

            if count > 1:
                findings.append(
                    GraphValidationFinding(
                        severity=ValidationSeverity.ERROR,
                        code="PROV-005",
                        message=(
                            f"Node {target_id} has {count} "
                            "PROVENANCE_OF relationships; "
                            "exactly one is required."
                        ),
                        target_revision_id=target_id,
                    )
                )

        # ---------------------------------------------------------------
        # Provenance edges must originate from PROVENANCE nodes
        # ---------------------------------------------------------------

        for edge in graph.edges.values():

            if edge.edge_type is not EdgeType.PROVENANCE_OF:
                continue

            source = graph.get_node(
                edge.source_revision_id
            )

            target = graph.get_node(
                edge.target_revision_id
            )

            if source is None or target is None:
                continue

            if source.kind != "PROVENANCE":
                findings.append(
                    GraphValidationFinding(
                        severity=ValidationSeverity.ERROR,
                        code="PROV-006",
                        message=(
                            "PROVENANCE_OF must originate from a "
                            f"PROVENANCE node, but source is "
                            f"{source.kind}."
                        ),
                        edge_id=edge.id,
                        source_revision_id=source.id,
                        target_revision_id=target.id,
                    )
                )

            if target.kind == "PROVENANCE":
                findings.append(
                    GraphValidationFinding(
                        severity=ValidationSeverity.ERROR,
                        code="PROV-007",
                        message=(
                            "PROVENANCE_OF cannot target another "
                            "PROVENANCE node."
                        ),
                        edge_id=edge.id,
                        source_revision_id=source.id,
                        target_revision_id=target.id,
                    )
                )

        return findings

    def _validate_provenance_edge(
        self,
        source: GraphNode,
        target: GraphNode,
        edge,
    ) -> list[GraphValidationFinding]:

        findings: list[GraphValidationFinding] = []

        if source.kind != "PROVENANCE":
            findings.append(
                GraphValidationFinding(
                    severity=ValidationSeverity.ERROR,
                    code="PROV-006",
                    message=(
                        "PROVENANCE_OF must originate from a "
                        f"PROVENANCE node, but got {source.kind}."
                    ),
                    edge_id=edge.id,
                    source_revision_id=source.id,
                    target_revision_id=target.id,
                )
            )

        if target.kind == "PROVENANCE":
            findings.append(
                GraphValidationFinding(
                    severity=ValidationSeverity.ERROR,
                    code="PROV-007",
                    message=(
                        "PROVENANCE_OF cannot target another "
                        "PROVENANCE node."
                    ),
                    edge_id=edge.id,
                    source_revision_id=source.id,
                    target_revision_id=target.id,
                )
            )

        return findings

    # ===================================================================
    # CONTAINS VALIDATION
    # ===================================================================

    def _validate_contains(
        self,
        source: GraphNode,
        target: GraphNode,
        edge,
    ) -> list[GraphValidationFinding]:

        findings: list[GraphValidationFinding] = []

        if source.kind != "ARTIFACTREVISION":
            findings.append(
                GraphValidationFinding(
                    severity=ValidationSeverity.ERROR,
                    code="EDGE-006",
                    message=(
                        "CONTAINS requires an ARTIFACTREVISION as "
                        f"the source, but got {source.kind}."
                    ),
                    edge_id=edge.id,
                    source_revision_id=source.id,
                    target_revision_id=target.id,
                )
            )

            return findings

        artifact = source.record

        if not isinstance(artifact, ArtifactRevision):
            findings.append(
                GraphValidationFinding(
                    severity=ValidationSeverity.ERROR,
                    code="EDGE-007",
                    message=(
                        "Node is classified as ARTIFACTREVISION but does "
                        "not contain an ArtifactRevision record."
                    ),
                    edge_id=edge.id,
                    source_revision_id=source.id,
                    target_revision_id=target.id,
                )
            )

            return findings

        allowed_targets = ARTIFACT_CONTAINS_TARGETS.get(
            artifact.artifact_type
        )

        if allowed_targets is None:
            findings.append(
                GraphValidationFinding(
                    severity=ValidationSeverity.WARNING,
                    code="EDGE-008",
                    message=(
                        "No CONTAINS invariant has been defined for "
                        f"artifact type "
                        f"{artifact.artifact_type.value}."
                    ),
                    edge_id=edge.id,
                    source_revision_id=source.id,
                    target_revision_id=target.id,
                )
            )

            return findings

        if target.kind not in allowed_targets:
            findings.append(
                GraphValidationFinding(
                    severity=ValidationSeverity.ERROR,
                    code="EDGE-009",
                    message=(
                        f"{artifact.artifact_type.value} cannot contain "
                        f"{target.kind}. Allowed target kinds: "
                        f"{sorted(allowed_targets)}."
                    ),
                    edge_id=edge.id,
                    source_revision_id=source.id,
                    target_revision_id=target.id,
                )
            )

        return findings

    # ===================================================================
    # CONVENIENCE
    # ===================================================================

    def is_valid(self, graph: Graph) -> bool:
        return not any(
            finding.severity is ValidationSeverity.ERROR
            for finding in self.validate(graph)
        )