from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from app.database.repositories.baseline_governance_repository import BaselineGovernanceRepository
from app.database.repositories.baseline_repository import BaselineRepository
from app.database.repositories.approval_repository import ApprovalRepository
from app.database.repositories.provenance_event_repository import ProvenanceEventRepository
from app.database.repositories.record_repository import RecordRepository
from app.database.repositories.sqlalchemy_baseline_governance_repository import SQLAlchemyBaselineGovernanceRepository
from app.database.repositories.sqlalchemy_baseline_repository import SQLAlchemyBaselineRepository
from app.database.repositories.sqlalchemy_approval_repository import SQLAlchemyApprovalRepository
from app.database.repositories.sqlalchemy_provenance_event_repository import SQLAlchemyProvenanceEventRepository
from app.database.repositories.sqlalchemy_record_repository import SQLAlchemyRecordRepository


class RepositoryFactory:
    """Application composition root for database repositories."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    @property
    def baseline_repository(self) -> BaselineRepository:
        return SQLAlchemyBaselineRepository(self._session_factory)

    @property
    def baseline_governance_repository(self) -> BaselineGovernanceRepository:
        return SQLAlchemyBaselineGovernanceRepository(self._session_factory)

    @property
    def record_repository(self) -> RecordRepository:
        return SQLAlchemyRecordRepository(self._session_factory)

    @property
    def approval_repository(self) -> ApprovalRepository:
        return SQLAlchemyApprovalRepository(self._session_factory)

    @property
    def provenance_event_repository(self) -> ProvenanceEventRepository:
        return SQLAlchemyProvenanceEventRepository(self._session_factory)
