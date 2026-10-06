from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.governance.record_policy import (
    RecordPolicy,
    RecordPolicyRegistry,
)
from app.models.graph.enums import EdgeType
from app.models.graph.provenance import (
    ProvenanceMethod,
    ProvenanceSourceType,
)
from app.models.graph.records import (
    DocumentLocation,
    DocumentRevision,
    Provenance,
    Record,
)
from app.services.graph_service import GraphService


class DocumentService(Protocol):
    """
    Application boundary for document persistence.

    The concrete implementation is expected to be backed by
    SQLiteDocumentRepository.

    A logical document is identified by document_id.

    Each update creates a DocumentRevision while the logical
    Document identity remains stable.
    """

    def upsert_record(
        self,
        *,
        document_id: str,
        baseline_id: str,
        record: Record,
        section_content: str,
        anchor: str,
        format: str = "markdown",
        document_revision_id: str | None = None,
    ) -> tuple[DocumentRevision, DocumentLocation]:
        ...


class ProvenanceService(Protocol):
    """
    Application boundary for creating provenance records.

    The service creates the Provenance domain record. It does not
    persist the provenance record into the graph.
    """

    def create(
        self,
        *,
        record: Record,
        source_type: ProvenanceSourceType,
        source_id: str,
        method: ProvenanceMethod,
        description: str | None = None,
        source_hash: str | None = None,
        actor_id: str | None = None,
        confidence: float | None = None,
    ) -> Provenance:
        ...


@dataclass(frozen=True, kw_only=True)
class GovernanceContext:
    """
    Context required to create a governed record.

    baseline_id:
        Identifies the baseline to which the record belongs.

    artifact_revision_id:
        Identifies the artifact revision containing the record.

        This remains governance context for the record, but is not
        a property of Document or DocumentRevision.

    format:
        Representation format requested for the document projection.
    """

    baseline_id: str
    artifact_revision_id: str
    format: str = "markdown"


@dataclass(frozen=True, kw_only=True)
class GovernedRecordResult:
    """
    Result of creating a governed record.

    The result contains every representation created by the
    governed-record operation.
    """

    record: Record

    document_revision: DocumentRevision | None

    document_location: DocumentLocation | None

    provenance: Provenance | None


class GovernedRecordService:
    """
    Orchestrates creation of a governed domain record.

    A governed record consists of:

        Domain Record
            +
        Document Representation
            +
        Provenance
            +
        Graph Representation

    This service coordinates those representations.

    Responsibilities:
        - Resolve the RecordPolicy.
        - Validate governance requirements.
        - Create/update the Markdown representation.
        - Create provenance when required.
        - Add the record to the graph.
        - Add provenance to the graph.
        - Create the mandatory PROVENANCE_OF relationship.

    This service does NOT:
        - Define graph semantics.
        - Create arbitrary business relationships.
        - Render records itself.
        - Persist Markdown directly.
        - Persist provenance directly.
        - Manage workflow approval/rejection.
        - Implement record-specific business logic.

    Document placement is explicitly supplied to this operation.
    It is not determined by RecordPolicy.

    Business relationships such as:

        FR-001 --HAS_ACCEPTANCE--> AC-001
        CON-001 --CONSTRAINS--> FR-001
        DES-001 --REALIZES--> FR-001

    must be created explicitly through GraphService.
    """

    def __init__(
        self,
        *,
        graph_service: GraphService,
        document_service: DocumentService,
        provenance_service: ProvenanceService,
        policy_registry: RecordPolicyRegistry,
    ) -> None:
        self._graph_service = graph_service
        self._document_service = document_service
        self._provenance_service = provenance_service
        self._policy_registry = policy_registry

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create(
        self,
        *,
        record: Record,
        context: GovernanceContext,
        document_id: str | None = None,
        source_type: ProvenanceSourceType,
        source_id: str,
        provenance_method: ProvenanceMethod,
        provenance_description: str | None = None,
        source_hash: str | None = None,
        actor_id: str | None = None,
        confidence: float | None = None,
    ) -> GovernedRecordResult:
        """
        Create a governed record and all required representations.

        The operation is policy-driven.

        The RecordPolicy determines whether the record requires:
            - a document representation
            - provenance
            - graph representation

        The document_id determines which logical document receives
        the record.

        GovernanceContext provides execution context such as:
            - baseline
            - artifact revision
            - format
        """

        self._validate_record(record)

        policy = self._policy_registry.get(record)

        self._validate_context(
            context=context,
            policy=policy,
            document_id=document_id,
        )

        self._validate_policy(
            record=record,
            policy=policy,
        )

        document_revision = None
        document_location = None

        # --------------------------------------------------------------
        # Document representation
        # --------------------------------------------------------------

        if policy.document_required:

            if document_id is None:
                raise ValueError(
                    "document_id is required when the record policy "
                    "requires document representation"
                )

            document_revision, document_location = (
                self._document_service.upsert_record(
                    document_id=document_id,
                    baseline_id=context.baseline_id,
                    record=record,
                    section_content=policy.render(record),
                    anchor=policy.anchor(record),
                    format=context.format,
                )
            )

        # --------------------------------------------------------------
        # Provenance
        # --------------------------------------------------------------

        provenance = None

        if policy.provenance_required:

            provenance = self._provenance_service.create(
                record=record,
                source_type=source_type,
                source_id=source_id,
                method=provenance_method,
                description=provenance_description,
                source_hash=source_hash,
                actor_id=actor_id,
                confidence=confidence,
            )

        # --------------------------------------------------------------
        # Graph representation
        # --------------------------------------------------------------

        if policy.graph_required:

            self._graph_service.add_record(record)

            if provenance is not None:

                self._graph_service.add_record(provenance)

                self._graph_service.create_edge(
                    edge_id=self._provenance_edge_id(
                        provenance=provenance,
                        record=record,
                    ),
                    source_revision_id=(
                        provenance.meta.revision_id
                    ),
                    target_revision_id=(
                        record.meta.revision_id
                    ),
                    edge_type=EdgeType.PROVENANCE_OF,
                )

        return GovernedRecordResult(
            record=record,
            document_revision=document_revision,
            document_location=document_location,
            provenance=provenance,
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_record(
        record: Record,
    ) -> None:
        """
        Validate the minimum identity required by every Record.
        """

        if record is None:
            raise ValueError(
                "record cannot be None"
            )

        if not record.meta.entity_id:
            raise ValueError(
                "record entity_id cannot be empty"
            )

        if not record.meta.revision_id:
            raise ValueError(
                "record revision_id cannot be empty"
            )

        if not record.meta.version:
            raise ValueError(
                "record version cannot be empty"
            )

        if not record.meta.title:
            raise ValueError(
                "record title cannot be empty"
            )

        if not record.meta.owner_id:
            raise ValueError(
                "record owner_id cannot be empty"
            )

    @staticmethod
    def _validate_context(
        *,
        context: GovernanceContext,
        policy: RecordPolicy,
        document_id: str | None,
    ) -> None:
        """
        Validate the governance context required for the operation.

        Document identity is supplied explicitly to the operation.
        It is deliberately not part of RecordPolicy.
        """

        if context is None:
            raise ValueError(
                "GovernanceContext cannot be None"
            )

        if not context.baseline_id:
            raise ValueError(
                "GovernanceContext.baseline_id cannot be empty"
            )

        if not context.artifact_revision_id:
            raise ValueError(
                "GovernanceContext.artifact_revision_id "
                "cannot be empty"
            )

        if not context.format:
            raise ValueError(
                "GovernanceContext.format cannot be empty"
            )

        if policy.document_required and not document_id:
            raise ValueError(
                "document_id is required when the record policy "
                "requires document representation"
            )

    @staticmethod
    def _validate_policy(
        *,
        record: Record,
        policy: RecordPolicy,
    ) -> None:
        """
        Validate that the selected policy can govern the record.
        """

        if not policy.matches(record):
            raise ValueError(
                "Resolved RecordPolicy does not match record type: "
                f"{type(record).__name__}"
            )

        policy.require_document_configuration()

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    @staticmethod
    def _provenance_edge_id(
        *,
        provenance: Provenance,
        record: Record,
    ) -> str:
        """
        Generate a deterministic ID for the mandatory provenance edge.
        """

        return (
            "EDGE-PROV-"
            f"{provenance.meta.revision_id}-"
            f"{record.meta.revision_id}"
        )

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def policy_for(
        self,
        record: Record,
    ) -> RecordPolicy:
        """
        Return the policy that governs the supplied record.
        """

        self._validate_record(record)

        return self._policy_registry.get(record)