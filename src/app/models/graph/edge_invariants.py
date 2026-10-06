from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet

from .enums import ArtifactType, EdgeType


@dataclass(frozen=True)
class EdgeInvariant:
    """
    Semantic contract for a graph edge.

    source_kinds and target_kinds contain the Python record kind names
    returned by GraphNode.kind().
    """

    edge_type: EdgeType
    source_kinds: FrozenSet[str]
    target_kinds: FrozenSet[str]
    description: str


# ---------------------------------------------------------------------------
# Generic edge invariants
# ---------------------------------------------------------------------------

EDGE_INVARIANTS: dict[EdgeType, EdgeInvariant] = {
    EdgeType.HAS_ACCEPTANCE: EdgeInvariant(
        edge_type=EdgeType.HAS_ACCEPTANCE,
        source_kinds=frozenset({"REQUIREMENT"}),
        target_kinds=frozenset({"ACCEPTANCECRITERION"}),
        description="A requirement has acceptance criteria.",
    ),

    EdgeType.APPLIES_TO: EdgeInvariant(
        edge_type=EdgeType.APPLIES_TO,
        source_kinds=frozenset({
            "CONSTRAINT",
            "ASSESSMENT",
            "DECISION",
        }),
        target_kinds=frozenset({
            "REQUIREMENT",
            "DESIGNELEMENT",
            "INTERFACECONTRACT",
            "DECISION",
            "CONSTRAINT",
        }),
        description="A policy, assessment, or decision applies to a domain object.",
    ),

    EdgeType.ASSESSED_BY: EdgeInvariant(
        edge_type=EdgeType.ASSESSED_BY,
        source_kinds=frozenset({"REQUIREMENT", "CONSTRAINT"}),
        target_kinds=frozenset({"ASSESSMENT"}),
        description="A requirement or constraint is assessed by an assessment.",
    ),

    EdgeType.CONSTRAINS: EdgeInvariant(
        edge_type=EdgeType.CONSTRAINS,
        source_kinds=frozenset({"CONSTRAINT"}),
        target_kinds=frozenset({
            "REQUIREMENT",
            "DESIGNELEMENT",
            "INTERFACECONTRACT",
            "DECISION",
        }),
        description="A constraint constrains a domain object.",
    ),

    EdgeType.SELECTS: EdgeInvariant(
        edge_type=EdgeType.SELECTS,
        source_kinds=frozenset({"DECISION"}),
        target_kinds=frozenset({
            "DESIGNELEMENT",
            "INTERFACECONTRACT",
        }),
        description="A decision selects a design option.",
    ),

    EdgeType.IMPLEMENTS: EdgeInvariant(
        edge_type=EdgeType.IMPLEMENTS,
        source_kinds=frozenset({
            "DESIGNELEMENT",
            "INTERFACECONTRACT",
        }),
        target_kinds=frozenset({"REQUIREMENT"}),
        description="A design or implementation element implements a requirement.",
    ),

    EdgeType.EXPOSES: EdgeInvariant(
        edge_type=EdgeType.EXPOSES,
        source_kinds=frozenset({"DESIGNELEMENT"}),
        target_kinds=frozenset({"INTERFACECONTRACT"}),
        description="A design element exposes an interface contract.",
    ),

    EdgeType.REALIZES: EdgeInvariant(
        edge_type=EdgeType.REALIZES,
        source_kinds=frozenset({"DESIGNELEMENT"}),
        target_kinds=frozenset({
            "REQUIREMENT",
            "CONSTRAINT",
        }),
        description="A design element realizes a requirement or constraint.",
    ),

    EdgeType.SPECIFIED_BY: EdgeInvariant(
        edge_type=EdgeType.SPECIFIED_BY,
        source_kinds=frozenset({
            "DESIGNELEMENT",
            "INTERFACECONTRACT",
        }),
        target_kinds=frozenset({"DECISION"}),
        description="A design element is specified by a design decision.",
    ),

    EdgeType.VERIFIED_BY: EdgeInvariant(
        edge_type=EdgeType.VERIFIED_BY,
        source_kinds=frozenset({
            "REQUIREMENT",
            "CONSTRAINT",
            "DESIGNELEMENT",
            "INTERFACECONTRACT",
        }),
        target_kinds=frozenset({"TESTCASE"}),
        description="A domain object is verified by a test case.",
    ),

    EdgeType.VERIFIES: EdgeInvariant(
        edge_type=EdgeType.VERIFIES,
        source_kinds=frozenset({"TESTCASE"}),
        target_kinds=frozenset({
            "REQUIREMENT",
            "CONSTRAINT",
            "DESIGNELEMENT",
            "INTERFACECONTRACT",
        }),
        description="A test case verifies a domain object.",
    ),

    EdgeType.EXECUTED_AS: EdgeInvariant(
        edge_type=EdgeType.EXECUTED_AS,
        source_kinds=frozenset({"TESTCASE"}),
        target_kinds=frozenset({"ASSESSMENTRUN"}),
        description="A test case is executed as an assessment run.",
    ),

    EdgeType.PRODUCED: EdgeInvariant(
        edge_type=EdgeType.PRODUCED,
        source_kinds=frozenset({
            "ASSESSMENT",
            "ASSESSMENTRUN",
        }),
        target_kinds=frozenset({"EVIDENCE"}),
        description="An assessment or assessment run produces evidence.",
    ),

    EdgeType.CONFIRMS: EdgeInvariant(
        edge_type=EdgeType.CONFIRMS,
        source_kinds=frozenset({"EVIDENCE"}),
        target_kinds=frozenset({
            "ASSESSMENT",
            "ASSESSMENTRUN",
        }),
        description="Evidence confirms an assessment or assessment run.",
    ),

    EdgeType.IMPLEMENTATION_OF: EdgeInvariant(
        edge_type=EdgeType.IMPLEMENTATION_OF,
        source_kinds=frozenset({
            "DESIGNELEMENT",
            "INTERFACECONTRACT",
        }),
        target_kinds=frozenset({
            "REQUIREMENT",
            "DESIGNELEMENT",
        }),
        description="An implementation/design element is an implementation of a domain object.",
    ),

    EdgeType.PROVENANCE_OF: EdgeInvariant(
        edge_type=EdgeType.PROVENANCE_OF,
        source_kinds=frozenset({"PROVENANCE"}),
        target_kinds=frozenset({
            "ARTIFACTREVISION",
            "REQUIREMENT",
            "ACCEPTANCECRITERION",
            "CONSTRAINT",
            "ASSESSMENT",
            "DECISION",
            "DESIGNELEMENT",
            "INTERFACECONTRACT",
            "TESTCASE",
            "ASSESSMENTRUN",
            "EVIDENCE",
        }),
        description="A provenance record describes the source of another graph record.",
    ),
}


# ---------------------------------------------------------------------------
# Artifact-specific CONTAINS rules
# ---------------------------------------------------------------------------

ARTIFACT_CONTAINS_TARGETS: dict[ArtifactType, FrozenSet[str]] = {
    ArtifactType.CHAPTER: frozenset({
        "ARTIFACTREVISION",
        "REQUIREMENT",
        "CONSTRAINT",
        "DECISION",
        "DESIGNELEMENT",
        "INTERFACECONTRACT",
        "TESTCASE",
    }),

    ArtifactType.FRD: frozenset({
        "REQUIREMENT",
        "ACCEPTANCECRITERION",
        "CONSTRAINT",
    }),

    ArtifactType.NFRD: frozenset({
        "REQUIREMENT",
        "ACCEPTANCECRITERION",
        "CONSTRAINT",
    }),

    ArtifactType.HLD: frozenset({
        "DESIGNELEMENT",
        "DECISION",
        "INTERFACECONTRACT",
        "CONSTRAINT",
    }),

    ArtifactType.LLD: frozenset({
        "DESIGNELEMENT",
        "DECISION",
        "INTERFACECONTRACT",
        "CONSTRAINT",
    }),

    ArtifactType.VERIFICATION: frozenset({
        "TESTCASE",
        "ASSESSMENT",
        "ASSESSMENTRUN",
        "EVIDENCE",
    }),

    ArtifactType.IMPLEMENTATION: frozenset({
        "DESIGNELEMENT",
        "INTERFACECONTRACT",
    }),
}