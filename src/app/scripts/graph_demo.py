
"""
Graph + Governance Integration Demo

Demonstrates the current aigov architecture:

    Domain Record
        |
        v
    GovernedRecordService
        |
        +--> RecordPolicyRegistry
        |       |
        |       +--> rendering
        |       +--> anchoring
        |       +--> governance requirements
        |
        +--> DocumentService
        |       |
        |       +--> SQLite metadata
        |       +--> Markdown projection
        |       +--> membership
        |       +--> document locations
        |
        +--> ProvenanceService
        |
        +--> GraphService
                |
                +--> Graph node
                +--> PROVENANCE_OF edge

Document placement is deliberately NOT owned by RecordPolicy.

The application/orchestration layer chooses which logical document
a governed record belongs to:

    Requirement -> FRD-001
    NFR         -> NFRD-001
    Decision    -> HLD-001
    etc.

RecordPolicy only describes how the record is governed and rendered.

This demo uses a temporary renderer because the production renderer
has not yet been implemented.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from app.database.repositories.sqlite_document_repository import (
    SQLiteDocumentRepository,
)
from app.database.repositories.sqlite_graph_repository import (
    SQLiteGraphRepository,
)
from app.governance.record_policy import (
    RecordPolicy,
    RecordPolicyRegistry,
)
from app.models.graph.edge import EdgeType
from app.models.graph.enums import (
    AssertionKind,
    AssessmentStage,
    ConstraintType,
    ExecutionMode,
    EvidenceType,
    Priority,
    QualityCategory,
    RevisionStatus,
)
from app.models.graph.provenance import (
    ProvenanceMethod,
    ProvenanceSourceType,
)
from app.models.graph.records import (
    AcceptanceCriterion,
    Assessment,
    Constraint,
    Decision,
    DesignElement,
    Evidence,
    InterfaceContract,
    Provenance,
    Requirement,
    RevisionMeta,
    TestCase,
)
from app.services.document_service import DocumentService
from app.services.governed_record_service import (
    GovernedRecordService,
    GovernanceContext,
)
from app.services.graph_service import GraphService
from app.services.semantic_validator import (
    GraphSemanticValidator,
    ValidationSeverity,
)
from app.config import Settings

# ============================================================================
# Demo paths
# ============================================================================

settings = Settings()

settings.initialize_storage()

print("AIGOV_HOME =", settings.aigov_home)
print("DATABASE         =", settings.database_path)
print("DOCUMENT ROOT    =", settings.document_root)

DATABASE_PATH = settings.database_path
DOCUMENT_ROOT = settings.document_root


# ============================================================================
# Temporary demo renderer
# ============================================================================


class DemoRecordRenderer:
    """
    Temporary renderer used only by this demo.

    Production rendering will eventually be implemented behind the
    RecordPolicy renderer abstraction.
    """

    def render(self, record) -> str:
        if isinstance(record, Requirement):
            return self._render_requirement(record)

        if isinstance(record, AcceptanceCriterion):
            return self._render_acceptance(record)

        if isinstance(record, Constraint):
            return self._render_constraint(record)

        if isinstance(record, Decision):
            return self._render_decision(record)

        if isinstance(record, DesignElement):
            return self._render_design_element(record)

        if isinstance(record, InterfaceContract):
            return self._render_interface(record)

        if isinstance(record, Assessment):
            return self._render_assessment(record)

        if isinstance(record, TestCase):
            return self._render_test_case(record)

        if isinstance(record, Evidence):
            return self._render_evidence(record)

        raise ValueError(
            f"Demo renderer does not support {type(record).__name__}"
        )

    def anchor(self, record) -> str:
        """
        Return a stable Markdown heading used as the document anchor.

        The logical entity ID is included in the heading so that a
        title change does not orphan the existing logical record.

        Example:

            ## FR-001 — Process customer orders
        """

        return (
            f"## {record.meta.entity_id} "
            f"— {record.meta.title}"
        )

    # ------------------------------------------------------------------
    # Requirement
    # ------------------------------------------------------------------

    def _render_requirement(
        self,
        record: Requirement,
    ) -> str:
        return (
            f"{self.anchor(record)}\n\n"
            f"**ID:** `{record.meta.revision_id}`  \n"
            f"**Entity:** `{record.meta.entity_id}`  \n"
            f"**Priority:** `{record.priority.value}`  \n"
            f"**Status:** `{record.meta.status.value}`  \n\n"
            f"{record.statement}\n"
        )

    # ------------------------------------------------------------------
    # Acceptance criterion
    # ------------------------------------------------------------------

    def _render_acceptance(
        self,
        record: AcceptanceCriterion,
    ) -> str:
        return (
            f"{self.anchor(record)}\n\n"
            f"**ID:** `{record.meta.revision_id}`  \n"
            f"**Entity:** `{record.meta.entity_id}`  \n"
            f"**Status:** `{record.meta.status.value}`  \n\n"
            f"### Given\n"
            f"{record.given}\n\n"
            f"### When\n"
            f"{record.when}\n\n"
            f"### Then\n"
            f"{record.then}\n"
        )

    # ------------------------------------------------------------------
    # Constraint
    # ------------------------------------------------------------------

    def _render_constraint(
        self,
        record: Constraint,
    ) -> str:
        quality_category = (
            record.quality_category.value
            if record.quality_category is not None
            else None
        )

        quality_line = (
            f"**Quality Category:** `{quality_category}`  \n"
            if quality_category
            else ""
        )

        return (
            f"{self.anchor(record)}\n\n"
            f"**ID:** `{record.meta.revision_id}`  \n"
            f"**Entity:** `{record.meta.entity_id}`  \n"
            f"**Type:** `{record.constraint_type.value}`  \n"
            f"{quality_line}"
            f"**Status:** `{record.meta.status.value}`  \n\n"
            f"{record.statement}\n"
        )

    # ------------------------------------------------------------------
    # Decision
    # ------------------------------------------------------------------

    def _render_decision(
        self,
        record: Decision,
    ) -> str:
        return (
            f"{self.anchor(record)}\n\n"
            f"**ID:** `{record.meta.revision_id}`  \n"
            f"**Entity:** `{record.meta.entity_id}`  \n"
            f"**Status:** `{record.meta.status.value}`  \n\n"
            f"### Decision\n"
            f"{record.decision}\n\n"
            f"### Rationale\n"
            f"{record.rationale}\n"
        )

    # ------------------------------------------------------------------
    # Design element
    # ------------------------------------------------------------------

    def _render_design_element(
        self,
        record: DesignElement,
    ) -> str:
        return (
            f"{self.anchor(record)}\n\n"
            f"**ID:** `{record.meta.revision_id}`  \n"
            f"**Entity:** `{record.meta.entity_id}`  \n"
            f"**Type:** `{record.element_type}`  \n"
            f"**Status:** `{record.meta.status.value}`  \n\n"
            f"### Responsibility\n"
            f"{record.responsibility}\n"
        )

    # ------------------------------------------------------------------
    # Interface contract
    # ------------------------------------------------------------------

    def _render_interface(
        self,
        record: InterfaceContract,
    ) -> str:
        return (
            f"{self.anchor(record)}\n\n"
            f"**ID:** `{record.meta.revision_id}`  \n"
            f"**Entity:** `{record.meta.entity_id}`  \n"
            f"**Method:** `{record.method}`  \n"
            f"**Path:** `{record.path}`  \n"
            f"**Response Status:** `{record.response_status}`  \n"
            f"**Idempotency Required:** "
            f"`{record.idempotency_required}`  \n"
        )

    # ------------------------------------------------------------------
    # Assessment
    # ------------------------------------------------------------------

    def _render_assessment(
        self,
        record: Assessment,
    ) -> str:
        return (
            f"{self.anchor(record)}\n\n"
            f"**ID:** `{record.meta.revision_id}`  \n"
            f"**Entity:** `{record.meta.entity_id}`  \n"
            f"**Execution Mode:** "
            f"`{record.execution_mode.value}`  \n"
            f"**Stage:** `{record.assessment_stage.value}`  \n"
            f"**Expected Evidence:** "
            f"`{record.expected_evidence.value}`  \n\n"
            f"{record.method_description}\n"
        )

    # ------------------------------------------------------------------
    # Test case
    # ------------------------------------------------------------------

    def _render_test_case(
        self,
        record: TestCase,
    ) -> str:
        return (
            f"{self.anchor(record)}\n\n"
            f"**ID:** `{record.meta.revision_id}`  \n"
            f"**Entity:** `{record.meta.entity_id}`  \n"
            f"**Test Type:** `{record.test_type}`  \n"
            f"**Automated:** `{record.automated}`  \n"
        )

    # ------------------------------------------------------------------
    # Evidence
    # ------------------------------------------------------------------

    def _render_evidence(
        self,
        record: Evidence,
    ) -> str:
        return (
            f"{self.anchor(record)}\n\n"
            f"**ID:** `{record.meta.revision_id}`  \n"
            f"**Entity:** `{record.meta.entity_id}`  \n"
            f"**Evidence Type:** "
            f"`{record.evidence_type.value}`  \n"
            f"**Source Hash:** `{record.source_hash}`  \n\n"
            f"{record.observation}\n"
        )


# ============================================================================
# Temporary demo provenance service
# ============================================================================


class DemoProvenanceService:
    """
    Temporary in-memory provenance implementation.

    The real ProvenanceService can later capture richer source information.
    """

    def __init__(self) -> None:
        self._counter = 0

    def create(
        self,
        *,
        record,
        source_type: ProvenanceSourceType,
        source_id: str,
        method: ProvenanceMethod,
        description: str | None = None,
        source_hash: str | None = None,
        actor_id: str | None = None,
        confidence: float | None = None,
    ) -> Provenance:

        self._counter += 1

        provenance_id = f"PROV-{self._counter:03d}"

        return Provenance(
            meta=_revision_meta(
                entity_id=provenance_id,
                revision_id=f"{provenance_id}-v1",
                title=(
                    f"Provenance for "
                    f"{record.meta.revision_id}"
                ),
                owner_id=actor_id or "demo-user",
                status=RevisionStatus.APPROVED,
                assertion_kind=AssertionKind.USER_CONFIRMED,
            ),
            source_type=source_type,
            source_id=source_id,
            method=method,
            description=description,
            source_hash=source_hash,
            actor_id=actor_id,
            confidence=confidence,
        )


# ============================================================================
# Helpers
# ============================================================================


def _revision_meta(
    *,
    entity_id: str,
    revision_id: str,
    title: str,
    owner_id: str = "demo-user",
    status: RevisionStatus = RevisionStatus.DRAFT,
    assertion_kind: AssertionKind = AssertionKind.USER_CONFIRMED,
) -> RevisionMeta:
    """
    Construct RevisionMeta without duplicating the fields everywhere.
    """

    return RevisionMeta(
        entity_id=entity_id,
        revision_id=revision_id,
        version="1",
        title=title,
        status=status,
        owner_id=owner_id,
        assertion_kind=assertion_kind,
    )


# ============================================================================
# Record policies
# ============================================================================


def _policy(
    *,
    record_type,
    renderer: DemoRecordRenderer,
) -> RecordPolicy:
    """
    Build a demo record policy.

    IMPORTANT:

    RecordPolicy does not decide document placement.

    It only describes how a record type is governed and rendered.

    The caller of GovernedRecordService.create() supplies document_id.
    """

    return RecordPolicy(
        record_type=record_type,
        document_required=True,
        provenance_required=True,
        graph_required=True,
        renderer=renderer.render,
        anchor_resolver=renderer.anchor,
    )


def create_demo_policy_registry(
    renderer: DemoRecordRenderer,
) -> RecordPolicyRegistry:
    """
    Demo-only policy registry.

    Document placement is intentionally absent from the policies.

    The same Requirement policy can therefore be used for:

        FR-001 -> FRD-001
        NFR-001 -> NFRD-001

    This is important because policy and document placement are
    separate concerns.
    """

    return RecordPolicyRegistry(
        [
            _policy(
                record_type=Requirement,
                renderer=renderer,
            ),

            _policy(
                record_type=AcceptanceCriterion,
                renderer=renderer,
            ),

            _policy(
                record_type=Constraint,
                renderer=renderer,
            ),

            _policy(
                record_type=Decision,
                renderer=renderer,
            ),

            _policy(
                record_type=DesignElement,
                renderer=renderer,
            ),

            _policy(
                record_type=InterfaceContract,
                renderer=renderer,
            ),

            _policy(
                record_type=Assessment,
                renderer=renderer,
            ),

            _policy(
                record_type=TestCase,
                renderer=renderer,
            ),

            _policy(
                record_type=Evidence,
                renderer=renderer,
            ),
        ]
    )


# ============================================================================
# Demo documents
# ============================================================================


def create_demo_documents(
    *,
    document_service: DocumentService,
) -> None:
    """
    Explicitly create the logical documents used by this demo.

    Document placement belongs to application orchestration, not
    RecordPolicy.

    Each logical document has:

        stable document ID
        physical path
        current projection
        document revisions
    """

    documents = [
        {
            "document_id": "FRD-001",
            "path": "documents/requirements/FRD-001.md",
        },
        {
            "document_id": "NFRD-001",
            "path": "documents/requirements/NFRD-001.md",
        },
        {
            "document_id": "HLD-001",
            "path": "documents/design/HLD-001.md",
        },
        {
            "document_id": "VER-001",
            "path": "documents/verification/VER-001.md",
        },
    ]

    for definition in documents:
        document_service.create(
            document_id=definition["document_id"],
            baseline_id="BASELINE-001",
            path=definition["path"],
            content="",
        )


# ============================================================================
# Demo records
# ============================================================================


def create_demo_records() -> dict[str, object]:

    # ------------------------------------------------------------------
    # Functional requirement
    # ------------------------------------------------------------------

    fr = Requirement(
        meta=_revision_meta(
            entity_id="FR-001",
            revision_id="FR-001-v1",
            title="Process customer orders",
        ),
        statement=(
            "The system shall process valid customer orders."
        ),
        priority=Priority.HIGH,
    )

    # ------------------------------------------------------------------
    # Non-functional requirement
    # ------------------------------------------------------------------

    nfr = Requirement(
        meta=_revision_meta(
            entity_id="NFR-001",
            revision_id="NFR-001-v1",
            title="Order API response time",
        ),
        statement=(
            "The order API shall respond within 500 ms for "
            "95% of requests under normal load."
        ),
        priority=Priority.HIGH,
    )

    # ------------------------------------------------------------------
    # Acceptance criterion
    # ------------------------------------------------------------------

    acceptance = AcceptanceCriterion(
        meta=_revision_meta(
            entity_id="AC-001",
            revision_id="AC-001-v1",
            title="Successful order processing",
        ),
        given="A valid customer order is submitted",
        when="The order is processed",
        then="The system returns a successful order response",
    )

    # ------------------------------------------------------------------
    # Technology constraint
    # ------------------------------------------------------------------

    platform_constraint = Constraint(
        meta=_revision_meta(
            entity_id="CON-001",
            revision_id="CON-001-v1",
            title="Use existing order platform",
        ),
        constraint_type=ConstraintType.TECHNOLOGY,
        statement=(
            "The solution shall use the existing order platform."
        ),
    )

    # ------------------------------------------------------------------
    # Quality constraint
    # ------------------------------------------------------------------

    performance_constraint = Constraint(
        meta=_revision_meta(
            entity_id="CON-002",
            revision_id="CON-002-v1",
            title="API performance constraint",
        ),
        constraint_type=ConstraintType.QUALITY,
        statement=(
            "The API must maintain the agreed response-time target."
        ),
        quality_category=QualityCategory.PERFORMANCE,
    )

    # ------------------------------------------------------------------
    # Design decision
    # ------------------------------------------------------------------

    decision = Decision(
        meta=_revision_meta(
            entity_id="DEC-001",
            revision_id="DEC-001-v1",
            title="Use asynchronous order events",
        ),
        decision=(
            "Use asynchronous events for downstream "
            "order processing."
        ),
        rationale=(
            "This decouples order acceptance from downstream "
            "processing and allows consumers to scale independently."
        ),
    )

    # ------------------------------------------------------------------
    # Design element
    # ------------------------------------------------------------------

    design = DesignElement(
        meta=_revision_meta(
            entity_id="DES-001",
            revision_id="DES-001-v1",
            title="Order Processing Service",
        ),
        element_type="SERVICE",
        responsibility=(
            "Accept customer orders, validate them, persist "
            "the order and publish the order event."
        ),
    )

    # ------------------------------------------------------------------
    # Interface contract
    # ------------------------------------------------------------------

    interface = InterfaceContract(
        meta=_revision_meta(
            entity_id="API-001",
            revision_id="API-001-v1",
            title="Create Order API",
        ),
        method="POST",
        path="/orders",
        response_status="201",
        idempotency_required=True,
    )

    # ------------------------------------------------------------------
    # Assessment
    # ------------------------------------------------------------------

    assessment = Assessment(
        meta=_revision_meta(
            entity_id="ASM-001",
            revision_id="ASM-001-v1",
            title="Order API performance assessment",
        ),
        method_description=(
            "Execute a load test against the order API and verify "
            "the 95th percentile response time."
        ),
        execution_mode=ExecutionMode.AUTOMATED,
        assessment_stage=AssessmentStage.VERIFICATION,
        expected_evidence=EvidenceType.TEST_RESULT,
    )

    # ------------------------------------------------------------------
    # Test case
    # ------------------------------------------------------------------

    test_case = TestCase(
        meta=_revision_meta(
            entity_id="TC-001",
            revision_id="TC-001-v1",
            title="Process valid order",
        ),
        test_type="INTEGRATION",
        automated=True,
    )

    # ------------------------------------------------------------------
    # Evidence
    # ------------------------------------------------------------------

    evidence = Evidence(
        meta=_revision_meta(
            entity_id="EVD-001",
            revision_id="EVD-001-v1",
            title="Order API benchmark",
        ),
        evidence_type=EvidenceType.TEST_RESULT,
        observation=(
            "Load test completed successfully. The observed 95th "
            "percentile response time was 420 ms."
        ),
        source_hash="demo-source-hash-001",
    )

    return {
        "fr": fr,
        "nfr": nfr,
        "acceptance": acceptance,
        "platform_constraint": platform_constraint,
        "performance_constraint": performance_constraint,
        "decision": decision,
        "design": design,
        "interface": interface,
        "assessment": assessment,
        "test_case": test_case,
        "evidence": evidence,
    }


# ============================================================================
# Governance contexts
# ============================================================================


def create_governance_contexts() -> dict[str, GovernanceContext]:
    """
    GovernanceContext contains workflow/baseline information.

    It intentionally does not contain document identity.

    Document identity is supplied independently during governed
    record creation.
    """

    return {
        # ----------------------------------------------------------
        # Functional requirements
        # ----------------------------------------------------------

        "fr": GovernanceContext(
            baseline_id="BASELINE-001",
            artifact_revision_id="FRD-001-v1",
        ),

        "acceptance": GovernanceContext(
            baseline_id="BASELINE-001",
            artifact_revision_id="FRD-001-v1",
        ),

        "platform_constraint": GovernanceContext(
            baseline_id="BASELINE-001",
            artifact_revision_id="FRD-001-v1",
        ),

        # ----------------------------------------------------------
        # Non-functional requirements
        # ----------------------------------------------------------

        "nfr": GovernanceContext(
            baseline_id="BASELINE-001",
            artifact_revision_id="NFRD-001-v1",
        ),

        "performance_constraint": GovernanceContext(
            baseline_id="BASELINE-001",
            artifact_revision_id="NFRD-001-v1",
        ),

        # ----------------------------------------------------------
        # High-level design
        # ----------------------------------------------------------

        "decision": GovernanceContext(
            baseline_id="BASELINE-001",
            artifact_revision_id="HLD-001-v1",
        ),

        "design": GovernanceContext(
            baseline_id="BASELINE-001",
            artifact_revision_id="HLD-001-v1",
        ),

        "interface": GovernanceContext(
            baseline_id="BASELINE-001",
            artifact_revision_id="HLD-001-v1",
        ),

        # ----------------------------------------------------------
        # Verification
        # ----------------------------------------------------------

        "assessment": GovernanceContext(
            baseline_id="BASELINE-001",
            artifact_revision_id="VER-001-v1",
        ),

        "test_case": GovernanceContext(
            baseline_id="BASELINE-001",
            artifact_revision_id="VER-001-v1",
        ),

        "evidence": GovernanceContext(
            baseline_id="BASELINE-001",
            artifact_revision_id="VER-001-v1",
        ),
    }


# ============================================================================
# Document placement
# ============================================================================


def create_document_placements() -> dict[str, str]:
    """
    Explicit application-level mapping from demo record names to
    logical document IDs.

    This is deliberately separate from RecordPolicy.

    In the real product this decision could eventually come from:

        - CLI arguments
        - workflow/stage
        - document creation service
        - project configuration
        - refinement workflow
        - document placement policy

    But it should not be embedded inside RecordPolicy.
    """

    return {
        "fr": "FRD-001",
        "acceptance": "FRD-001",
        "platform_constraint": "FRD-001",

        "nfr": "NFRD-001",
        "performance_constraint": "NFRD-001",

        "decision": "HLD-001",
        "design": "HLD-001",
        "interface": "HLD-001",

        "assessment": "VER-001",
        "test_case": "VER-001",
        "evidence": "VER-001",
    }


# ============================================================================
# Governed record creation
# ============================================================================


def create_governed_records(
    *,
    governed_service: GovernedRecordService,
    records: dict[str, object],
) -> dict[str, object]:
    """
    Create every domain record through GovernedRecordService.

    Document placement is explicitly supplied here.

    GovernedRecordService remains responsible for:

        - policy validation
        - document rendering
        - document projection
        - provenance
        - graph node creation
        - provenance graph relationship

    It does not decide which logical document should receive the
    record.
    """

    contexts = create_governance_contexts()
    document_placements = create_document_placements()

    results: dict[str, object] = {}

    for name, record in records.items():

        if name not in contexts:
            raise ValueError(
                f"No GovernanceContext configured "
                f"for record '{name}'"
            )

        document_id = document_placements.get(name)

        if document_id is None:
            raise ValueError(
                f"No document placement configured "
                f"for record '{name}'"
            )

        results[name] = governed_service.create(
            record=record,
            context=contexts[name],
            document_id=document_id,
            source_type=ProvenanceSourceType.USER_INPUT,
            source_id="demo-user-input",
            provenance_method=ProvenanceMethod.DIRECT_INPUT,
            provenance_description=(
                f"Demo user-provided "
                f"{type(record).__name__}"
            ),
            actor_id="demo-user",
            confidence=1.0,
        )

    return results


# ============================================================================
# Explicit business relationships
# ============================================================================


def create_business_relationships(
    *,
    graph_service: GraphService,
    records: dict[str, object],
) -> None:
    """
    Create explicit semantic relationships.

    GovernedRecordService deliberately does NOT own these
    relationships.
    """

    # ------------------------------------------------------------------
    # Requirement -> Acceptance Criterion
    # ------------------------------------------------------------------

    graph_service.create_edge(
        edge_id="EDGE-001",
        source_revision_id=records[
            "fr"
        ].meta.revision_id,
        target_revision_id=records[
            "acceptance"
        ].meta.revision_id,
        edge_type=EdgeType.HAS_ACCEPTANCE,
    )

    # ------------------------------------------------------------------
    # Platform Constraint -> Functional Requirement
    # ------------------------------------------------------------------

    graph_service.create_edge(
        edge_id="EDGE-002",
        source_revision_id=records[
            "platform_constraint"
        ].meta.revision_id,
        target_revision_id=records[
            "fr"
        ].meta.revision_id,
        edge_type=EdgeType.CONSTRAINS,
    )

    # ------------------------------------------------------------------
    # Performance Constraint -> NFR
    # ------------------------------------------------------------------

    graph_service.create_edge(
        edge_id="EDGE-003",
        source_revision_id=records[
            "performance_constraint"
        ].meta.revision_id,
        target_revision_id=records[
            "nfr"
        ].meta.revision_id,
        edge_type=EdgeType.CONSTRAINS,
    )

    # ------------------------------------------------------------------
    # Design -> Functional Requirement
    # ------------------------------------------------------------------

    graph_service.create_edge(
        edge_id="EDGE-004",
        source_revision_id=records[
            "design"
        ].meta.revision_id,
        target_revision_id=records[
            "fr"
        ].meta.revision_id,
        edge_type=EdgeType.REALIZES,
    )

    # ------------------------------------------------------------------
    # Design -> Decision
    # ------------------------------------------------------------------

    graph_service.create_edge(
        edge_id="EDGE-005",
        source_revision_id=records[
            "design"
        ].meta.revision_id,
        target_revision_id=records[
            "decision"
        ].meta.revision_id,
        edge_type=EdgeType.SPECIFIED_BY,
    )

    # ------------------------------------------------------------------
    # Design -> Interface
    # ------------------------------------------------------------------

    graph_service.create_edge(
        edge_id="EDGE-006",
        source_revision_id=records[
            "design"
        ].meta.revision_id,
        target_revision_id=records[
            "interface"
        ].meta.revision_id,
        edge_type=EdgeType.EXPOSES,
    )

    # ------------------------------------------------------------------
    # NFR -> Assessment
    # ------------------------------------------------------------------

    graph_service.create_edge(
        edge_id="EDGE-007",
        source_revision_id=records[
            "nfr"
        ].meta.revision_id,
        target_revision_id=records[
            "assessment"
        ].meta.revision_id,
        edge_type=EdgeType.ASSESSED_BY,
    )

    # ------------------------------------------------------------------
    # Test -> Functional Requirement
    # ------------------------------------------------------------------

    graph_service.create_edge(
        edge_id="EDGE-008",
        source_revision_id=records[
            "test_case"
        ].meta.revision_id,
        target_revision_id=records[
            "fr"
        ].meta.revision_id,
        edge_type=EdgeType.VERIFIES,
    )

    # ------------------------------------------------------------------
    # Assessment -> Evidence
    # ------------------------------------------------------------------

    graph_service.create_edge(
        edge_id="EDGE-009",
        source_revision_id=records[
            "assessment"
        ].meta.revision_id,
        target_revision_id=records[
            "evidence"
        ].meta.revision_id,
        edge_type=EdgeType.PRODUCED,
    )

    # ------------------------------------------------------------------
    # Evidence -> Assessment
    # ------------------------------------------------------------------

    graph_service.create_edge(
        edge_id="EDGE-010",
        source_revision_id=records[
            "evidence"
        ].meta.revision_id,
        target_revision_id=records[
            "assessment"
        ].meta.revision_id,
        edge_type=EdgeType.CONFIRMS,
    )


# ============================================================================
# Output helpers
# ============================================================================


def print_graph(
    graph_service: GraphService,
) -> None:

    graph = graph_service.graph

    print()
    print("=" * 80)
    print("GRAPH")
    print("=" * 80)

    print()
    print(f"Nodes: {len(graph.nodes)}")
    print(f"Edges: {len(graph.edges)}")

    print()
    print("NODES")
    print("-" * 80)

    for revision_id, node in sorted(
        graph.nodes.items()
    ):
        record = node.record

        print(
            f"{revision_id:<22} "
            f"{node.kind:<24} "
            f"{record.meta.title}"
        )

    print()
    print("EDGES")
    print("-" * 80)

    for edge_id, edge in sorted(
        graph.edges.items()
    ):
        print(
            f"{edge_id:<12} "
            f"{edge.source_revision_id:<22} "
            f"--{edge.edge_type.value}--> "
            f"{edge.target_revision_id:<22}"
        )


def print_documents(
    *,
    document_service: DocumentService,
    document_ids: list[str],
) -> None:

    print()
    print("=" * 80)
    print("MARKDOWN DOCUMENTS")
    print("=" * 80)

    for document_id in document_ids:

        try:
            document = document_service.require(
                document_id
            )
        except Exception as exc:
            print()
            print(
                f"[{document_id}] unavailable: {exc}"
            )
            continue

        content = document_service.read(
            document_id
        )

        revisions = document_service.get_revisions(
            document_id
        )

        print()
        print(
            f"[{document.id}] "
            f"{document.path}"
        )

        print(
            f"Revisions: {len(revisions)}"
        )

        print("-" * 80)
        print(content.rstrip())


# ============================================================================
# Validation
# ============================================================================


def validate_graph(
    graph_service: GraphService,
) -> None:

    reloaded_graph = graph_service.load()

    print()
    print("=" * 80)
    print("SEMANTIC VALIDATION")
    print("=" * 80)

    validator = GraphSemanticValidator()

    findings = validator.validate(
        reloaded_graph
    )

    errors = [
        finding
        for finding in findings
        if finding.severity
        is ValidationSeverity.ERROR
    ]

    warnings = [
        finding
        for finding in findings
        if finding.severity
        is ValidationSeverity.WARNING
    ]

    if not findings:
        print("Status: PASS")
        print("Errors: 0")
        print("Warnings: 0")

    else:
        print(
            "Status:",
            "FAIL" if errors else "PASS WITH WARNINGS",
        )

        print(
            f"Errors: {len(errors)}"
        )

        print(
            f"Warnings: {len(warnings)}"
        )

        for finding in findings:

            print()

            print(
                f"[{finding.severity.value}] "
                f"{finding.code}: "
                f"{finding.message}"
            )

            if finding.edge_id:
                print(
                    f"  Edge: {finding.edge_id}"
                )

            if finding.source_revision_id:
                print(
                    f"  Source: "
                    f"{finding.source_revision_id}"
                )

            if finding.target_revision_id:
                print(
                    f"  Target: "
                    f"{finding.target_revision_id}"
                )


# ============================================================================
# Main
# ============================================================================


def main() -> None:

    # ------------------------------------------------------------------
    # Reset demo environment
    # ------------------------------------------------------------------


    # ------------------------------------------------------------------
    # Repositories
    # ------------------------------------------------------------------

    graph_repository = SQLiteGraphRepository(
        database_path=DATABASE_PATH,
    )

    document_repository = SQLiteDocumentRepository(
        database_path=DATABASE_PATH,
        document_root=DOCUMENT_ROOT,
    )

    # ------------------------------------------------------------------
    # Services
    # ------------------------------------------------------------------

    graph_service = GraphService(
        repository=graph_repository,
    )

    document_service = DocumentService(
        repository=document_repository,
    )

    provenance_service = DemoProvenanceService()

    renderer = DemoRecordRenderer()

    policy_registry = create_demo_policy_registry(
        renderer=renderer,
    )

    governed_record_service = GovernedRecordService(
        graph_service=graph_service,
        document_service=document_service,
        provenance_service=provenance_service,
        policy_registry=policy_registry,
    )

    # ------------------------------------------------------------------
    # Explicitly create logical documents
    # ------------------------------------------------------------------

    create_demo_documents(
        document_service=document_service,
    )

    # ------------------------------------------------------------------
    # Create domain records
    # ------------------------------------------------------------------

    records = create_demo_records()

    # ------------------------------------------------------------------
    # Governed creation
    # ------------------------------------------------------------------

    results = create_governed_records(
        governed_service=governed_record_service,
        records=records,
    )

    print()
    print("=" * 80)
    print("GOVERNED RECORD CREATION")
    print("=" * 80)

    document_placements = (
        create_document_placements()
    )

    for name, result in results.items():

        document_id = document_placements[
            name
        ]

        document_revision_id = (
            result.document_revision.id
            if result.document_revision
            else "-"
        )

        provenance_id = (
            result.provenance.meta.revision_id
            if result.provenance
            else "-"
        )

        print(
            f"{name:<24} "
            f"record={result.record.meta.revision_id:<18} "
            f"document={document_id:<12} "
            f"doc-revision={document_revision_id:<30} "
            f"provenance={provenance_id}"
        )

    # ------------------------------------------------------------------
    # Explicit business relationships
    # ------------------------------------------------------------------

    create_business_relationships(
        graph_service=graph_service,
        records=records,
    )

    # ------------------------------------------------------------------
    # Save graph
    # ------------------------------------------------------------------

    graph_service.save()

    # ------------------------------------------------------------------
    # Print in-memory graph
    # ------------------------------------------------------------------

    print_graph(
        graph_service
    )

    # ------------------------------------------------------------------
    # Print documents
    # ------------------------------------------------------------------

    print_documents(
        document_service=document_service,
        document_ids=[
            "FRD-001",
            "NFRD-001",
            "HLD-001",
            "VER-001",
        ],
    )

    # ------------------------------------------------------------------
    # Reload graph from SQLite
    # ------------------------------------------------------------------

    print()
    print("=" * 80)
    print("RELOAD FROM SQLITE")
    print("=" * 80)

    reloaded_graph_service = GraphService(
        repository=graph_repository,
    )

    reloaded_graph_service.load()

    print(
        f"Reloaded nodes: "
        f"{len(reloaded_graph_service.graph.nodes)}"
    )

    print(
        f"Reloaded edges: "
        f"{len(reloaded_graph_service.graph.edges)}"
    )

    # ------------------------------------------------------------------
    # Validate reloaded graph
    # ------------------------------------------------------------------

    validate_graph(
        reloaded_graph_service
    )

    # ------------------------------------------------------------------
    # Final locations
    # ------------------------------------------------------------------

    print()
    print("=" * 80)
    print("DEMO OUTPUT")
    print("=" * 80)

    print(
        f"Database : {DATABASE_PATH}"
    )

    print(
        f"Documents: {DOCUMENT_ROOT}"
    )


if __name__ == "__main__":
    main()
