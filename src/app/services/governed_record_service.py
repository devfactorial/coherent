from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.database.repositories.record_repository import (
    RecordRepository,
)
from app.governance.record_policy import (
    RecordPolicy,
    RecordPolicyRegistry,
)
from app.models.graph.approval import Approval
from app.models.graph.enums import (
    ActorType,
    EdgeType,
    GovernanceOperation,
)
from app.models.graph.node import GraphNode
from app.models.graph.provenance import (
    ProvenanceMethod,
    ProvenanceSourceType,
)
from app.models.graph.provenance_event import (
    ProvenanceEvent,
)
from app.models.graph.records import (
    DocumentLocation,
    DocumentRevision,
    Provenance,
    Record,
)
from app.services.approval_service import ApprovalService
from app.services.graph_service import GraphService
from app.services.provenance_event_service import (
    ProvenanceEventService,
)


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
    ) -> tuple[
        DocumentRevision,
        DocumentLocation,
    ]:
        ...


class ProvenanceService(Protocol):
    """
    Application boundary for source provenance creation.

    This represents provenance such as:

        USER_INPUT
        DOCUMENT
        FILE
        LLM
        TOOL
        TEST_RUN
        EXTERNAL_SOURCE

    It is distinct from ProvenanceEvent, which represents
    aigov-owned governance/audit history.
    """

    def approve(
        self,
        *,
        revision_id: str,
        actor_id: str,
        actor_type: ActorType = ActorType.USER,
        comment: str | None = None,
    ) -> ApprovalResult:
        """
        Approve one specific immutable record revision.

        Approval does not create or mutate a record revision. The exact
        revision is loaded from the canonical RecordRepository and the
        resulting Approval is persisted separately. The audit event
        references that Approval through approval_id.
        """
        if self._approval_service is None:
            raise RuntimeError(
                "ApprovalService is required for approval operations"
            )

        if not revision_id:
            raise ValueError("revision_id cannot be empty")

        self._validate_actor(
            actor_id=actor_id,
            actor_type=actor_type,
        )

        record = self._record_repository.get(revision_id)

        if record is None:
            raise KeyError(
                f"Governed record revision not found: {revision_id}"
            )

        approval = self._approval_service.approve(
            record=record,
            actor=actor_id,
            actor_type=actor_type,
            comment=comment,
        )

        provenance_event = self._provenance_event_service.record(
            record=record,
            actor=actor_id,
            actor_type=actor_type,
            operation=GovernanceOperation.APPROVE,
            approval_id=approval.approval_id,
        )

        return ApprovalResult(
            approval=approval,
            provenance_event=provenance_event,
        )

    def reject(
        self,
        *,
        revision_id: str,
        actor_id: str,
        actor_type: ActorType = ActorType.USER,
        comment: str | None = None,
    ) -> ApprovalResult:
        """Record a rejection against one specific immutable revision."""
        if self._approval_service is None:
            raise RuntimeError(
                "ApprovalService is required for approval operations"
            )

        if not revision_id:
            raise ValueError("revision_id cannot be empty")

        self._validate_actor(
            actor_id=actor_id,
            actor_type=actor_type,
        )

        record = self._record_repository.get(revision_id)

        if record is None:
            raise KeyError(
                f"Governed record revision not found: {revision_id}"
            )

        approval = self._approval_service.reject(
            record=record,
            actor=actor_id,
            actor_type=actor_type,
            comment=comment,
        )

        provenance_event = self._provenance_event_service.record(
            record=record,
            actor=actor_id,
            actor_type=actor_type,
            operation=GovernanceOperation.REJECT,
            approval_id=approval.approval_id,
        )

        return ApprovalResult(
            approval=approval,
            provenance_event=provenance_event,
        )

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

    format:
        Representation format requested for the document projection.
    """

    baseline_id: str
    artifact_revision_id: str
    format: str = "markdown"


@dataclass(frozen=True, kw_only=True)
class GovernedRecordResult:
    """
    Result of a governed-record operation.

    The result contains the canonical record plus every representation
    produced by the operation.
    """

    record: Record

    document_revision: DocumentRevision | None

    document_location: DocumentLocation | None

    provenance: Provenance | None

    provenance_event: ProvenanceEvent


@dataclass(frozen=True, kw_only=True)
class ApprovalResult:
    """Result of an approval decision against one immutable revision."""

    approval: Approval
    provenance_event: ProvenanceEvent


class GovernedRecordService:
    """
    Application service responsible for governed-record operations.

    A governed record consists of:

        Canonical Record
            +
        Document Projection
            +
        Source Provenance
            +
        Graph Projection
            +
        Governance Audit Event

    Persistence ownership:

        RecordRepository
            -> canonical governed record state

        DocumentService
            -> Markdown/document projection

        ProvenanceService
            -> source provenance

        GraphService
            -> graph projection

        ProvenanceEventService
            -> immutable governance/audit history

    This service is the orchestration boundary through which governed
    record mutations enter aigov.

    It does NOT:

        - define graph semantics
        - create arbitrary business relationships
        - render records itself
        - persist Markdown directly
        - persist source provenance directly
        - implement approval workflow
        - implement record-specific business logic

    Business relationships such as:

        FR-001 --HAS_ACCEPTANCE--> AC-001
        CON-001 --CONSTRAINS--> FR-001
        DES-001 --REALIZES--> FR-001

    must be created explicitly through GraphService.

    Governance audit events are NOT graph nodes.
    """

    def __init__(
        self,
        *,
        record_repository: RecordRepository,
        graph_service: GraphService,
        document_service: DocumentService,
        provenance_service: ProvenanceService,
        provenance_event_service: ProvenanceEventService,
        policy_registry: RecordPolicyRegistry,
        approval_service: ApprovalService | None = None,
    ) -> None:
        self._record_repository = record_repository
        self._graph_service = graph_service
        self._document_service = document_service
        self._provenance_service = provenance_service
        self._provenance_event_service = (
            provenance_event_service
        )
        self._policy_registry = policy_registry
        self._approval_service = approval_service

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
        actor_type: ActorType = ActorType.USER,
        confidence: float | None = None,
        operation: GovernanceOperation = GovernanceOperation.CREATE,
        approval_id: str | None = None,
    ) -> GovernedRecordResult:
        """
        Create a governed record revision and all required projections.

        Despite the historical method name `create`, this method can
        also persist a new immutable revision of an existing logical
        record.

        The distinction is expressed through `operation`:

            CREATE
            UPDATE
            APPROVE
            REJECT
            SUPERSEDE

        The canonical record repository is queried before persistence
        to determine the previous revision.

        Previous revision information is never obtained from:

            - Markdown
            - graph state
            - caller-supplied values
        """

        self._validate_record(record)

        self._validate_actor(
            actor_id=actor_id,
            actor_type=actor_type,
        )

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

        # --------------------------------------------------------------
        # Determine previous canonical revision
        # --------------------------------------------------------------

        previous_record = (
            self._record_repository.get_latest(
                record.meta.entity_id
            )
        )

        self._validate_operation(
            record=record,
            previous_record=previous_record,
            operation=operation,
        )

        # --------------------------------------------------------------
        # Canonical record persistence
        # --------------------------------------------------------------

        self._record_repository.save(
            record
        )

        # --------------------------------------------------------------
        # Document representation
        # --------------------------------------------------------------

        document_revision = None
        document_location = None

        if policy.document_required:

            if document_id is None:
                raise ValueError(
                    "document_id is required when the record policy "
                    "requires document representation"
                )

            (
                document_revision,
                document_location,
            ) = self._document_service.upsert_record(
                document_id=document_id,
                baseline_id=context.baseline_id,
                record=record,
                section_content=policy.render(record),
                anchor=policy.anchor(record),
                format=context.format,
            )

        # --------------------------------------------------------------
        # Source provenance
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
            # Provenance is itself a governed Record.
            # Persist it through the canonical RecordRepository so that
            # every graph node has a corresponding governed record.
            self._record_repository.save(
                provenance
            )

        # --------------------------------------------------------------
        # Graph representation
        # --------------------------------------------------------------

        if policy.graph_required:

            record_node = self._graph_node_from_record(
                record
            )

            self._graph_service.add_node(
                record_node
            )

            if provenance is not None:

                provenance_node = (
                    self._graph_node_from_record(
                        provenance
                    )
                )

                self._graph_service.add_node(
                    provenance_node
                )

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

        # --------------------------------------------------------------
        # Governance audit
        # --------------------------------------------------------------

        if not actor_id:
            raise ValueError(
                "actor_id is required for governance audit"
            )

        provenance_event = (
            self._provenance_event_service.record(
                record=record,
                actor=actor_id,
                actor_type=actor_type,
                operation=operation,
                previous_record=previous_record,
                approval_id=approval_id,
            )
        )

        return GovernedRecordResult(
            record=record,
            document_revision=document_revision,
            document_location=document_location,
            provenance=provenance,
            provenance_event=provenance_event,
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
    def _validate_actor(
        *,
        actor_id: str | None,
        actor_type: ActorType,
    ) -> None:
        """
        Validate the actor responsible for the governed operation.
        """

        if not actor_id:
            raise ValueError(
                "actor_id is required for a governed operation"
            )

        if actor_type is None:
            raise ValueError(
                "actor_type is required for a governed operation"
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

    @staticmethod
    def _validate_operation(
        *,
        record: Record,
        previous_record: Record | None,
        operation: GovernanceOperation,
    ) -> None:
        """
        Validate consistency between the requested operation and
        canonical record history.

        CREATE:
            Must not already have a previous revision.

        UPDATE:
            Must have a previous revision.

        APPROVE / REJECT / SUPERSEDE:
            Must operate on an existing logical record.

        Note:
            Approval/rejection workflow semantics will become more
            sophisticated once the approval model is introduced.
        """

        if operation is None:
            raise ValueError(
                "operation cannot be None"
            )

        if operation is GovernanceOperation.CREATE:
            if previous_record is not None:
                raise ValueError(
                    "CREATE operation is invalid because a previous "
                    "revision already exists for record: "
                    f"{record.meta.entity_id}"
                )

            return

        if operation is GovernanceOperation.UPDATE:
            if previous_record is None:
                raise ValueError(
                    "UPDATE operation is invalid because no previous "
                    "revision exists for record: "
                    f"{record.meta.entity_id}"
                )

            return

        if operation in {
            GovernanceOperation.APPROVE,
            GovernanceOperation.REJECT,
            GovernanceOperation.SUPERSEDE,
        }:
            if previous_record is None:
                raise ValueError(
                    f"{operation.value} operation is invalid because "
                    "no previous revision exists for record: "
                    f"{record.meta.entity_id}"
                )

    # ------------------------------------------------------------------
    # Graph
    # ------------------------------------------------------------------

    @staticmethod
    def _graph_node_from_record(
        record: Record,
    ) -> GraphNode:
        """
        Create the graph projection for a governed record revision.

        GraphNode wraps the canonical governed record. The record's
        revision metadata remains the source of truth for graph identity
        and metadata.
        """
        return GraphNode(record=record)

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