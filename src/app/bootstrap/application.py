from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings

from app.database.repositories.sqlalchemy_record_repository import (
    SQLAlchemyRecordRepository,
)
from app.database.repositories.sqlalchemy_approval_repository import (
    SQLAlchemyApprovalRepository,
)
from app.database.repositories.sqlalchemy_provenance_event_repository import (
    SQLAlchemyProvenanceEventRepository,
)
from app.database.repositories.sqlalchemy_graph_repository import (
    SQLAlchemyGraphRepository,
)
from app.database.repositories.sqlalchemy_document_repository import (
    SQLAlchemyDocumentRepository,
)

from app.database.repositories.sqlalchemy_baseline_repository import (
    SQLAlchemyBaselineRepository,
)
from app.database.repositories.sqlalchemy_baseline_governance_repository import (
    SQLAlchemyBaselineGovernanceRepository,
)

from app.database.sqlalchemy.session import Database

from app.governance.record_policy import (
    RecordPolicyRegistry,
)

from app.services.approval_service import ApprovalService
from app.services.document_service import DocumentService
from app.services.governed_record_service import (
    GovernedRecordService,
)
from app.services.graph_service import GraphService
from app.services.provenance_event_service import (
    ProvenanceEventService,
)
from app.services.baseline_service import BaselineService
from app.services.baseline_approval_service import BaselineApprovalService



@dataclass
class Application:
    """
    Fully wired aigov application.

    This is the composition root.

    Responsibilities:

        Settings
            |
            v
        Database infrastructure
            |
            v
        Repositories
            |
            v
        Application services

    Domain/application services should not construct repositories,
    databases, or configuration themselves.
    """

    settings: Settings

    database: Database

    record_repository: SQLAlchemyRecordRepository
    approval_repository: SQLAlchemyApprovalRepository
    provenance_event_repository: (
        SQLAlchemyProvenanceEventRepository
    )

    graph_repository: SQLAlchemyGraphRepository
    document_repository: SQLAlchemyDocumentRepository
    baseline_repository: SQLAlchemyBaselineRepository
    baseline_governance_repository: SQLAlchemyBaselineGovernanceRepository

    graph_service: GraphService
    document_service: DocumentService
    approval_service: ApprovalService
    provenance_event_service: ProvenanceEventService
    governed_record_service: GovernedRecordService
    baseline_service: BaselineService
    baseline_approval_service: BaselineApprovalService

    def close(self) -> None:
        """
        Release database resources.

        The application owns the database lifecycle.
        """
        self.database.dispose()


def create_application(
    *,
    settings: Settings | None = None,
    policy_registry: RecordPolicyRegistry,
    provenance_service,
) -> Application:
    """
    Build the complete aigov application dependency graph.

    Demo/application-specific components such as:

        - RecordPolicyRegistry
        - ProvenanceService

    are supplied by the caller.

    Infrastructure components such as:

        - Database
        - repositories
        - core services

    are constructed here.
    """

    if settings is None:
        settings = Settings()

    settings.initialize_storage()

    # ================================================================
    # Database infrastructure
    # ================================================================

    database = Database(
        database_path=settings.database_path,
    )

    # ================================================================
    # SQLAlchemy-backed canonical repositories
    # ================================================================

    record_repository = SQLAlchemyRecordRepository(
        session_factory=database.session_factory,
    )

    approval_repository = SQLAlchemyApprovalRepository(
        session_factory=database.session_factory,
    )

    provenance_event_repository = (
        SQLAlchemyProvenanceEventRepository(
            session_factory=database.session_factory,
        )
    )

    # ================================================================
    # Existing document / graph repositories
    #
    # These can later be moved to SQLAlchemy without changing the
    # application composition model.
    # ================================================================

    document_repository = SQLAlchemyDocumentRepository(
        session_factory=database.session_factory,
        document_root=settings.document_root,
    )

    graph_repository = SQLAlchemyGraphRepository(
        session_factory=database.session_factory,
    )
    baseline_repository = SQLAlchemyBaselineRepository(
        session_factory=database.session_factory,
    )

    baseline_governance_repository = SQLAlchemyBaselineGovernanceRepository(
        session_factory=database.session_factory,
    )

    # ================================================================
    # Projection / infrastructure services
    # ================================================================

    document_service = DocumentService(
        repository=document_repository,
    )

    graph_service = GraphService(
        repository=graph_repository,
        record_repository=record_repository
    )

    # ================================================================
    # Governance services
    # ================================================================

    provenance_event_service = ProvenanceEventService(
        repository=provenance_event_repository,
    )

    approval_service = ApprovalService(
        repository=approval_repository,
    )

    baseline_service = BaselineService(
        baseline_repository=baseline_repository,
        governance_repository=baseline_governance_repository,
    )

    baseline_approval_service = BaselineApprovalService(
        baseline_repository=baseline_repository,
        governance_repository=baseline_governance_repository,
    )

    governed_record_service = GovernedRecordService(
        record_repository=record_repository,
        graph_service=graph_service,
        document_service=document_service,
        provenance_service=provenance_service,
        provenance_event_service=provenance_event_service,
        approval_service=approval_service,
        policy_registry=policy_registry,
    )

    return Application(
        settings=settings,
        database=database,

        record_repository=record_repository,
        approval_repository=approval_repository,
        provenance_event_repository=(
            provenance_event_repository
        ),

        graph_repository=graph_repository,
        document_repository=document_repository,
        baseline_repository=baseline_repository,
        baseline_governance_repository=baseline_governance_repository,

        graph_service=graph_service,
        document_service=document_service,
        approval_service=approval_service,
        provenance_event_service=(
            provenance_event_service
        ),
        governed_record_service=(
            governed_record_service
        ),
        baseline_service=baseline_service,
        baseline_approval_service=baseline_approval_service,
    )