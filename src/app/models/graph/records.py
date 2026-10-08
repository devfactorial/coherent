from __future__ import annotations

from dataclasses import dataclass

from .enums import (
    ArtifactType,
    AssertionKind,
    AssessmentStage,
    ConstraintType,
    ExecutionMode,
    EvidenceType,
    Priority,
    QualityCategory,
    RevisionStatus,
)
from .provenance import Provenance


@dataclass(frozen=True, kw_only=True)
class RevisionMeta:
    """
    Common metadata associated with every versioned domain record.

    entity_id:
        Stable identity of the logical entity across revisions.

    revision_id:
        Unique identity of this particular revision.

    version:
        Human-readable revision version, e.g. "v1", "v2".

    title:
        Human-readable title of the record.

    status:
        Lifecycle status of this revision.

    owner_id:
        Identifier of the person or system responsible for the record.

    assertion_kind:
        Classification of how the record's content was established.
    """

    entity_id: str
    revision_id: str
    version: str
    title: str
    status: RevisionStatus
    owner_id: str
    assertion_kind: AssertionKind


@dataclass(frozen=True, kw_only=True)
class ArtifactRevision:
    """
    Base representation of a versioned governance artifact.
    """

    meta: RevisionMeta
    artifact_type: ArtifactType
    stage: str


@dataclass(frozen=True, kw_only=True)
class Requirement:
    """
    Functional or domain requirement.

    A Requirement instance represents one specific revision of the
    logical requirement identified by meta.entity_id.
    """

    meta: RevisionMeta
    statement: str
    priority: Priority


@dataclass(frozen=True, kw_only=True)
class AcceptanceCriterion:
    """
    Acceptance criterion expressed using Given/When/Then semantics.
    """

    meta: RevisionMeta
    given: str
    when: str
    then: str


@dataclass(frozen=True, kw_only=True)
class Constraint:
    """
    Constraint imposed on the solution or delivery.

    Quality constraints may optionally specify a quality category.
    Non-quality constraints must not specify one.
    """

    meta: RevisionMeta
    constraint_type: ConstraintType
    statement: str
    quality_category: QualityCategory | None = None

    def __post_init__(self) -> None:
        if (
            self.constraint_type is ConstraintType.QUALITY
            and self.quality_category is None
        ):
            raise ValueError(
                "Quality constraints require quality_category"
            )

        if (
            self.constraint_type is not ConstraintType.QUALITY
            and self.quality_category is not None
        ):
            raise ValueError(
                "Only quality constraints may have quality_category"
            )


@dataclass(frozen=True, kw_only=True)
class Assessment:
    """
    Definition of an assessment used to verify or evaluate something.
    """

    meta: RevisionMeta
    method_description: str
    execution_mode: ExecutionMode
    assessment_stage: AssessmentStage
    expected_evidence: EvidenceType


@dataclass(frozen=True, kw_only=True)
class Decision:
    """
    Architectural, product, governance, or implementation decision.
    """

    meta: RevisionMeta
    decision: str
    rationale: str


@dataclass(frozen=True, kw_only=True)
class DesignElement:
    """
    A logical element of a system design.
    """

    meta: RevisionMeta
    element_type: str
    responsibility: str


@dataclass(frozen=True, kw_only=True)
class InterfaceContract:
    """
    Contract describing an externally exposed interface.
    """

    meta: RevisionMeta
    method: str
    path: str
    response_status: str
    idempotency_required: bool


@dataclass(frozen=True, kw_only=True)
class TestCase:
    """
    Definition of a test case.
    """

    meta: RevisionMeta
    test_type: str
    automated: bool


@dataclass(frozen=True, kw_only=True)
class AssessmentRun:
    """
    Execution of an assessment against a particular environment.
    """

    meta: RevisionMeta
    environment: str
    passed: bool


@dataclass(frozen=True, kw_only=True)
class Evidence:
    """
    Evidence produced by a test, assessment, audit, review, or benchmark.
    """

    meta: RevisionMeta
    evidence_type: EvidenceType
    observation: str
    source_hash: str


Record = (
    ArtifactRevision
    | Requirement
    | AcceptanceCriterion
    | Constraint
    | Assessment
    | Decision
    | DesignElement
    | InterfaceContract
    | TestCase
    | AssessmentRun
    | Evidence
    | Provenance
)


@dataclass(frozen=True, kw_only=True)
class Baseline:
    """
    Immutable logical snapshot of governed specification revisions.

    A baseline identifies the exact set of governed revisions that were
    approved together and can therefore be used as an authoritative
    specification boundary for downstream consumers such as Context Packs.
    """

    id: str
    title: str
    scope: str
    status: RevisionStatus = RevisionStatus.DRAFT


@dataclass(frozen=True, kw_only=True)
class Document:
    """
    Logical document identity.

    A Document is stable across document revisions.

    Example:
        id   = "FRD-ORDERS"
        path = "requirements/FRD/orders.md"
    """

    id: str
    path: str
    format: str = "markdown"

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Document id cannot be empty")

        if not self.path.strip():
            raise ValueError("Document path cannot be empty")

        if not self.format.strip():
            raise ValueError("Document format cannot be empty")


@dataclass(frozen=True, kw_only=True)
class DocumentRevision:
    """
    Revision of a rendered document projection.

    A document revision represents the state of an entire document,
    which may contain multiple governed record revisions.

    It is deliberately not tied to a single artifact revision.

    Example:

        FRD-ORDERS
            document revision 7
            contains:
                FR-001 v3
                FR-004 v1
                FR-007 v2
    """

    id: str
    document_id: str
    baseline_id: str
    path: str
    content_hash: str
    format: str = "markdown"

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Document revision id cannot be empty")

        if not self.document_id.strip():
            raise ValueError("Document revision document_id cannot be empty")

        if not self.baseline_id.strip():
            raise ValueError("Document revision baseline_id cannot be empty")

        if not self.path.strip():
            raise ValueError("Document revision path cannot be empty")

        if not self.content_hash.strip():
            raise ValueError("Document revision content_hash cannot be empty")

        if not self.format.strip():
            raise ValueError("Document revision format cannot be empty")


@dataclass(frozen=True, kw_only=True)
class DocumentMembership:
    """
    Governed membership of a record in a logical document.

    This answers:

        "Which governed records belong in this document?"

    Membership is independent of the physical Markdown file.

    Example:

        FR-001 -> FRD-ORDERS
        FR-004 -> FRD-ORDERS

    The membership identifies the logical record entity, while the
    record's revision determines which version is rendered for a
    particular document revision.
    """

    id: str
    document_id: str
    record_entity_id: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Document membership id cannot be empty")

        if not self.document_id.strip():
            raise ValueError(
                "Document membership document_id cannot be empty"
            )

        if not self.record_entity_id.strip():
            raise ValueError(
                "Document membership record_entity_id cannot be empty"
            )


@dataclass(frozen=True, kw_only=True)
class DocumentLocation:
    """
    Location of a particular record revision inside a document revision.

    This represents the rendered occurrence of a specific record
    revision in a specific document revision.
    """

    id: str
    document_revision_id: str
    record_revision_id: str
    anchor: str
    line_start: int
    line_end: int

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Document location id cannot be empty")

        if not self.document_revision_id.strip():
            raise ValueError(
                "Document location document_revision_id cannot be empty"
            )

        if not self.record_revision_id.strip():
            raise ValueError(
                "Document location record_revision_id cannot be empty"
            )

        if not self.anchor.strip():
            raise ValueError("Document location anchor cannot be empty")

        if self.line_start < 1:
            raise ValueError("Document location line_start must be >= 1")

        if self.line_end < self.line_start:
            raise ValueError(
                "Document location line_end must be >= line_start"
            )


def kind_of(record: Record) -> str:
    """
    Return the canonical graph kind for a domain record.

    Example:
        kind_of(requirement) == "REQUIREMENT"
    """
    return type(record).__name__.upper()