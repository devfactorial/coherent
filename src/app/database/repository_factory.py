from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from app.database.repositories.approval_repository import (
    ApprovalRepository,
)
from app.database.repositories.provenance_event_repository import (
    ProvenanceEventRepository,
)
from app.database.repositories.record_repository import (
    RecordRepository,
)
from app.database.repositories.sqlalchemy_approval_repository import (
    SQLAlchemyApprovalRepository,
)
from app.database.repositories.sqlalchemy_provenance_event_repository import (
    SQLAlchemyProvenanceEventRepository,
)
from app.database.repositories.sqlalchemy_record_repository import (
    SQLAlchemyRecordRepository,
)


class RepositoryFactory:
    """
    Application composition root for database repositories.

    The rest of the application should depend on repository interfaces,
    not on SQLAlchemy implementations.
    """

    def __init__(
        self,
        session_factory: sessionmaker[Session],
    ) -> None:
        self._session_factory = session_factory

    @property
    def record_repository(self) -> RecordRepository:
        return SQLAlchemyRecordRepository(
            self._session_factory,
        )

    @property
    def approval_repository(self) -> ApprovalRepository:
        return SQLAlchemyApprovalRepository(
            self._session_factory,
        )

    @property
    def provenance_event_repository(
        self,
    ) -> ProvenanceEventRepository:
        return SQLAlchemyProvenanceEventRepository(
            self._session_factory,
        )