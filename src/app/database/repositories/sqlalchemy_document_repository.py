from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.database.repositories.document_repository import (
    DocumentRepository,
)
from app.database.sqlalchemy.models import (
    DocumentLocationModel,
    DocumentMembershipModel,
    DocumentModel,
    DocumentRevisionModel,
)
from app.models.graph.records import (
    Document,
    DocumentLocation,
    DocumentMembership,
    DocumentRevision,
)


class SQLAlchemyDocumentRepository(DocumentRepository):
    """
    SQLAlchemy-backed document repository.

    SQLAlchemy stores:
        - logical document metadata
        - document revision metadata
        - document membership
        - rendered record locations

    Actual current document content is stored as Markdown
    files under document_root.

    Historical document content is represented by
    DocumentRevision metadata and is handled by the governed
    history layer rather than being stored in this repository.

    Document paths are relative to document_root.

    Database schema is managed by Alembic.
    """

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        document_root: str | Path,
    ) -> None:
        self._session_factory = session_factory
        self.document_root = Path(document_root).resolve()

        self.document_root.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ================================================================
    # Logical documents
    # ================================================================

    def save_document(
        self,
        document: Document,
    ) -> None:
        with self._session_factory() as session:
            row = session.get(
                DocumentModel,
                document.id,
            )

            if row is None:
                row = DocumentModel(
                    id=document.id,
                    path=document.path,
                    format=document.format,
                )
                session.add(row)
            else:
                row.path = document.path
                row.format = document.format

            session.commit()

    def get_document(
        self,
        document_id: str,
    ) -> Document | None:
        with self._session_factory() as session:
            row = session.get(
                DocumentModel,
                document_id,
            )

            if row is None:
                return None

            return self._to_document(row)

    def delete_document(
        self,
        document_id: str,
    ) -> None:
        document = self.get_document(
            document_id
        )

        if document is None:
            return

        with self._session_factory() as session:
            row = session.get(
                DocumentModel,
                document_id,
            )

            if row is not None:
                session.delete(row)
                session.commit()

        path = self._resolve_path(
            document.path
        )

        if path.exists():
            path.unlink()

    def document_exists(
        self,
        document_id: str,
    ) -> bool:
        with self._session_factory() as session:
            return (
                session.get(
                    DocumentModel,
                    document_id,
                )
                is not None
            )

    # ================================================================
    # Document revisions
    # ================================================================

    def save_revision(
        self,
        revision: DocumentRevision,
    ) -> None:
        row = DocumentRevisionModel(
            id=revision.id,
            document_id=revision.document_id,
            baseline_id=revision.baseline_id,
            path=revision.path,
            content_hash=revision.content_hash,
            format=revision.format,
        )

        with self._session_factory() as session:
            session.add(row)
            session.commit()

    def get_revision(
        self,
        document_revision_id: str,
    ) -> DocumentRevision | None:
        with self._session_factory() as session:
            row = session.get(
                DocumentRevisionModel,
                document_revision_id,
            )

            if row is None:
                return None

            return DocumentRevision(
                id=row.id,
                document_id=row.document_id,
                baseline_id=row.baseline_id,
                path=row.path,
                content_hash=row.content_hash,
                format=row.format,
            )

    def get_revisions(
        self,
        document_id: str,
    ) -> list[DocumentRevision]:
        self._require_document(
            document_id
        )

        stmt = (
            select(DocumentRevisionModel)
            .where(
                DocumentRevisionModel.document_id
                == document_id
            )
            .order_by(
                DocumentRevisionModel.id.asc()
            )
        )

        with self._session_factory() as session:
            rows = session.scalars(stmt).all()

            return [
                self._to_document_revision(row)
                for row in rows
            ]

    def delete_revision(
        self,
        document_revision_id: str,
    ) -> None:
        with self._session_factory() as session:
            row = session.get(
                DocumentRevisionModel,
                document_revision_id,
            )

            if row is not None:
                session.delete(row)
                session.commit()

    # ================================================================
    # Current document content
    # ================================================================

    def read_content(
        self,
        document_id: str,
    ) -> str:
        document = self._require_document(
            document_id
        )

        path = self._resolve_path(
            document.path
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Document file not found: "
                f"{document.path}"
            )

        return path.read_text(
            encoding="utf-8"
        )

    def write_content(
        self,
        document_id: str,
        content: str,
    ) -> None:
        document = self._require_document(
            document_id
        )

        path = self._resolve_path(
            document.path
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            content,
            encoding="utf-8",
        )

    # ================================================================
    # Document membership
    # ================================================================

    def save_membership(
        self,
        membership: DocumentMembership,
    ) -> None:
        self._require_document(
            membership.document_id
        )

        with self._session_factory() as session:
            stmt = (
                select(DocumentMembershipModel)
                .where(
                    DocumentMembershipModel.document_id
                    == membership.document_id,
                    DocumentMembershipModel.record_entity_id
                    == membership.record_entity_id,
                )
            )

            row = session.scalars(stmt).first()

            if row is None:
                row = DocumentMembershipModel(
                    id=membership.id,
                    document_id=membership.document_id,
                    record_entity_id=membership.record_entity_id,
                )
                session.add(row)

            session.commit()

    def get_membership(
        self,
        document_id: str,
        record_entity_id: str,
    ) -> DocumentMembership | None:
        stmt = (
            select(DocumentMembershipModel)
            .where(
                DocumentMembershipModel.document_id
                == document_id,
                DocumentMembershipModel.record_entity_id
                == record_entity_id,
            )
        )

        with self._session_factory() as session:
            row = session.scalars(stmt).first()

            if row is None:
                return None

            return self._to_membership(row)

    def get_memberships(
        self,
        document_id: str,
    ) -> list[DocumentMembership]:
        self._require_document(
            document_id
        )

        stmt = (
            select(DocumentMembershipModel)
            .where(
                DocumentMembershipModel.document_id
                == document_id
            )
            .order_by(
                DocumentMembershipModel.record_entity_id.asc(),
                DocumentMembershipModel.id.asc(),
            )
        )

        with self._session_factory() as session:
            rows = session.scalars(stmt).all()

            return [
                self._to_membership(row)
                for row in rows
            ]

    def delete_membership(
        self,
        document_id: str,
        record_entity_id: str,
    ) -> None:
        stmt = (
            select(DocumentMembershipModel)
            .where(
                DocumentMembershipModel.document_id
                == document_id,
                DocumentMembershipModel.record_entity_id
                == record_entity_id,
            )
        )

        with self._session_factory() as session:
            row = session.scalars(stmt).first()

            if row is not None:
                session.delete(row)
                session.commit()

    # ================================================================
    # Document locations
    # ================================================================

    def save_location(
        self,
        location: DocumentLocation,
    ) -> None:
        if location.line_start < 1:
            raise ValueError(
                "line_start must be >= 1"
            )

        if location.line_end < location.line_start:
            raise ValueError(
                "line_end must be >= line_start"
            )

        if not location.anchor.strip():
            raise ValueError(
                "Document location anchor cannot be empty"
            )

        self._require_document_revision(
            location.document_revision_id
        )

        stmt = (
            select(DocumentLocationModel)
            .where(
                DocumentLocationModel.document_revision_id
                == location.document_revision_id,
                DocumentLocationModel.record_revision_id
                == location.record_revision_id,
            )
        )

        with self._session_factory() as session:
            row = session.scalars(stmt).first()

            if row is None:
                row = DocumentLocationModel(
                    id=location.id,
                    document_revision_id=(
                        location.document_revision_id
                    ),
                    record_revision_id=(
                        location.record_revision_id
                    ),
                    anchor=location.anchor,
                    line_start=location.line_start,
                    line_end=location.line_end,
                )
                session.add(row)
            else:
                row.anchor = location.anchor
                row.line_start = location.line_start
                row.line_end = location.line_end

            session.commit()

    def get_location(
        self,
        document_revision_id: str,
        record_revision_id: str,
    ) -> DocumentLocation | None:
        stmt = (
            select(DocumentLocationModel)
            .where(
                DocumentLocationModel.document_revision_id
                == document_revision_id,
                DocumentLocationModel.record_revision_id
                == record_revision_id,
            )
        )

        with self._session_factory() as session:
            row = session.scalars(stmt).first()

            if row is None:
                return None

            return self._to_location(row)

    def get_locations(
        self,
        document_revision_id: str,
    ) -> list[DocumentLocation]:
        self._require_document_revision(
            document_revision_id
        )

        stmt = (
            select(DocumentLocationModel)
            .where(
                DocumentLocationModel.document_revision_id
                == document_revision_id
            )
            .order_by(
                DocumentLocationModel.line_start.asc(),
                DocumentLocationModel.id.asc(),
            )
        )

        with self._session_factory() as session:
            rows = session.scalars(stmt).all()

            return [
                self._to_location(row)
                for row in rows
            ]

    def delete_location(
        self,
        document_revision_id: str,
        record_revision_id: str,
    ) -> None:
        stmt = (
            select(DocumentLocationModel)
            .where(
                DocumentLocationModel.document_revision_id
                == document_revision_id,
                DocumentLocationModel.record_revision_id
                == record_revision_id,
            )
        )

        with self._session_factory() as session:
            row = session.scalars(stmt).first()

            if row is not None:
                session.delete(row)
                session.commit()

    # ================================================================
    # Helpers
    # ================================================================

    def _require_document(
        self,
        document_id: str,
    ) -> Document:
        document = self.get_document(
            document_id
        )

        if document is None:
            raise KeyError(
                f"Document not found: {document_id}"
            )

        return document

    def _require_document_revision(
        self,
        document_revision_id: str,
    ) -> DocumentRevision:
        revision = self.get_revision(
            document_revision_id
        )

        if revision is None:
            raise KeyError(
                f"Document revision not found: "
                f"{document_revision_id}"
            )

        return revision

    def _resolve_path(
        self,
        path: str,
    ) -> Path:
        candidate = (
            self.document_root / path
        ).resolve()

        try:
            candidate.relative_to(
                self.document_root
            )
        except ValueError as exc:
            raise ValueError(
                f"Document path escapes project root: "
                f"{path}"
            ) from exc

        return candidate

    @staticmethod
    def _to_document(
        row: DocumentModel,
    ) -> Document:
        return Document(
            id=row.id,
            path=row.path,
            format=row.format,
        )

    @staticmethod
    def _to_document_revision(
        row: DocumentRevisionModel,
    ) -> DocumentRevision:
        return DocumentRevision(
            id=row.id,
            document_id=row.document_id,
            baseline_id=row.baseline_id,
            path=row.path,
            content_hash=row.content_hash,
            format=row.format,
        )

    @staticmethod
    def _to_membership(
        row: DocumentMembershipModel,
    ) -> DocumentMembership:
        return DocumentMembership(
            id=row.id,
            document_id=row.document_id,
            record_entity_id=row.record_entity_id,
        )

    @staticmethod
    def _to_location(
        row: DocumentLocationModel,
    ) -> DocumentLocation:
        return DocumentLocation(
            id=row.id,
            document_revision_id=row.document_revision_id,
            record_revision_id=row.record_revision_id,
            anchor=row.anchor,
            line_start=row.line_start,
            line_end=row.line_end,
        )