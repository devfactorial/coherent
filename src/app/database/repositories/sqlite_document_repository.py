from __future__ import annotations

import sqlite3
from pathlib import Path

from app.database.repositories.document_repository import DocumentRepository
from app.models.graph.records import (
    Document,
    DocumentLocation,
    DocumentMembership,
    DocumentRevision,
)


class SQLiteDocumentRepository(DocumentRepository):
    """
   SQLite-backed document repository.

    SQLite stores:
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
    """

    def __init__(
        self,
        database_path: str | Path,
        document_root: str | Path,
    ) -> None:
        self._database_path = Path(database_path)
        self.document_root = Path(document_root).resolve()

        self._database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.document_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    # ================================================================
    # Initialization
    # ================================================================

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self._database_path
        )

        connection.row_factory = sqlite3.Row

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection

    def _initialize_database(self) -> None:
        with self._connect() as connection:

            # --------------------------------------------------------
            # Logical documents
            # --------------------------------------------------------

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    path TEXT NOT NULL UNIQUE,
                    format TEXT NOT NULL
                )
                """
            )

            # --------------------------------------------------------
            # Document revisions
            #
            # A revision is an immutable snapshot.
            #
            # SQLite rowid provides deterministic insertion ordering,
            # which is used when retrieving revisions.
            # --------------------------------------------------------

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS document_revisions (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    baseline_id TEXT NOT NULL,
                    path TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    format TEXT NOT NULL,

                    FOREIGN KEY (document_id)
                        REFERENCES documents(id)
                        ON DELETE CASCADE
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_document_revisions_document
                ON document_revisions (
                    document_id
                )
                """
            )

            # --------------------------------------------------------
            # Document membership
            # --------------------------------------------------------

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS document_memberships (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    record_entity_id TEXT NOT NULL,

                    FOREIGN KEY (document_id)
                        REFERENCES documents(id)
                        ON DELETE CASCADE,

                    UNIQUE (
                        document_id,
                        record_entity_id
                    )
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_document_memberships_document
                ON document_memberships (
                    document_id
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_document_memberships_record
                ON document_memberships (
                    record_entity_id
                )
                """
            )

            # --------------------------------------------------------
            # Rendered record locations
            # --------------------------------------------------------

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS document_locations (
                    id TEXT PRIMARY KEY,
                    document_revision_id TEXT NOT NULL,
                    record_revision_id TEXT NOT NULL,
                    anchor TEXT NOT NULL,
                    line_start INTEGER NOT NULL,
                    line_end INTEGER NOT NULL,

                    FOREIGN KEY (document_revision_id)
                        REFERENCES document_revisions(id)
                        ON DELETE CASCADE,

                    UNIQUE (
                        document_revision_id,
                        record_revision_id
                    )
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_document_locations_revision
                ON document_locations (
                    document_revision_id
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_document_locations_anchor
                ON document_locations (
                    document_revision_id,
                    anchor
                )
                """
            )

            connection.commit()

    # ================================================================
    # Logical documents
    # ================================================================

    def save_document(
        self,
        document: Document,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    id,
                    path,
                    format
                )
                VALUES (?, ?, ?)

                ON CONFLICT(id) DO UPDATE SET
                    path = excluded.path,
                    format = excluded.format
                """,
                (
                    document.id,
                    document.path,
                    document.format,
                ),
            )

            connection.commit()

    def get_document(
        self,
        document_id: str,
    ) -> Document | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    path,
                    format
                FROM documents
                WHERE id = ?
                """,
                (document_id,),
            ).fetchone()

        if row is None:
            return None

        return Document(
            id=row["id"],
            path=row["path"],
            format=row["format"],
        )

    def delete_document(
        self,
        document_id: str,
    ) -> None:
        document = self.get_document(
            document_id
        )

        if document is None:
            return

        with self._connect() as connection:
            connection.execute(
                """
                DELETE FROM documents
                WHERE id = ?
                """,
                (document_id,),
            )

            connection.commit()

        path = self._resolve_path(
            document.path
        )

        if path.exists():
            path.unlink()

    def document_exists(
        self,
        document_id: str,
    ) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM documents
                WHERE id = ?
                LIMIT 1
                """,
                (document_id,),
            ).fetchone()

        return row is not None

    # ================================================================
    # Document revisions
    # ================================================================

    def save_revision(
        self,
        revision: DocumentRevision,
    ) -> None:
        """
        Persist an immutable document revision.

        Revisions are insert-only. Attempting to reuse an existing
        revision ID raises sqlite3.IntegrityError.
        """

        self._require_document(
            revision.document_id
        )

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO document_revisions (
                    id,
                    document_id,
                    baseline_id,
                    path,
                    content_hash,
                    format
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    revision.id,
                    revision.document_id,
                    revision.baseline_id,
                    revision.path,
                    revision.content_hash,
                    revision.format,
                ),
            )

            connection.commit()

    def get_revision(
        self,
        document_revision_id: str,
    ) -> DocumentRevision | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    document_id,
                    baseline_id,
                    path,
                    content_hash,
                    format
                FROM document_revisions
                WHERE id = ?
                """,
                (document_revision_id,),
            ).fetchone()

        if row is None:
            return None

        return self._to_document_revision(
            row
        )

    def get_revisions(
        self,
        document_id: str,
    ) -> list[DocumentRevision]:
        self._require_document(
            document_id
        )

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    document_id,
                    baseline_id,
                    path,
                    content_hash,
                    format
                FROM document_revisions
                WHERE document_id = ?
                ORDER BY rowid ASC
                """,
                (document_id,),
            ).fetchall()

        return [
            self._to_document_revision(row)
            for row in rows
        ]

    def delete_revision(
        self,
        document_revision_id: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                DELETE FROM document_revisions
                WHERE id = ?
                """,
                (document_revision_id,),
            )

            connection.commit()

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

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO document_memberships (
                    id,
                    document_id,
                    record_entity_id
                )
                VALUES (?, ?, ?)

                ON CONFLICT(
                    document_id,
                    record_entity_id
                )
                DO NOTHING
                """,
                (
                    membership.id,
                    membership.document_id,
                    membership.record_entity_id,
                ),
            )

            connection.commit()

    def get_membership(
        self,
        document_id: str,
        record_entity_id: str,
    ) -> DocumentMembership | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    document_id,
                    record_entity_id
                FROM document_memberships
                WHERE document_id = ?
                  AND record_entity_id = ?
                """,
                (
                    document_id,
                    record_entity_id,
                ),
            ).fetchone()

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

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    document_id,
                    record_entity_id
                FROM document_memberships
                WHERE document_id = ?
                ORDER BY record_entity_id, id
                """,
                (document_id,),
            ).fetchall()

        return [
            self._to_membership(row)
            for row in rows
        ]

    def delete_membership(
        self,
        document_id: str,
        record_entity_id: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                DELETE FROM document_memberships
                WHERE document_id = ?
                  AND record_entity_id = ?
                """,
                (
                    document_id,
                    record_entity_id,
                ),
            )

            connection.commit()

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

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO document_locations (
                    id,
                    document_revision_id,
                    record_revision_id,
                    anchor,
                    line_start,
                    line_end
                )
                VALUES (?, ?, ?, ?, ?, ?)

                ON CONFLICT(
                    document_revision_id,
                    record_revision_id
                )
                DO UPDATE SET
                    id = excluded.id,
                    anchor = excluded.anchor,
                    line_start = excluded.line_start,
                    line_end = excluded.line_end
                """,
                (
                    location.id,
                    location.document_revision_id,
                    location.record_revision_id,
                    location.anchor,
                    location.line_start,
                    location.line_end,
                ),
            )

            connection.commit()

    def get_location(
        self,
        document_revision_id: str,
        record_revision_id: str,
    ) -> DocumentLocation | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    document_revision_id,
                    record_revision_id,
                    anchor,
                    line_start,
                    line_end
                FROM document_locations
                WHERE document_revision_id = ?
                  AND record_revision_id = ?
                """,
                (
                    document_revision_id,
                    record_revision_id,
                ),
            ).fetchone()

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

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    document_revision_id,
                    record_revision_id,
                    anchor,
                    line_start,
                    line_end
                FROM document_locations
                WHERE document_revision_id = ?
                ORDER BY line_start, id
                """,
                (document_revision_id,),
            ).fetchall()

        return [
            self._to_location(row)
            for row in rows
        ]

    def delete_location(
        self,
        document_revision_id: str,
        record_revision_id: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                DELETE FROM document_locations
                WHERE document_revision_id = ?
                  AND record_revision_id = ?
                """,
                (
                    document_revision_id,
                    record_revision_id,
                ),
            )

            connection.commit()

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
    def _to_document_revision(
        row: sqlite3.Row,
    ) -> DocumentRevision:
        return DocumentRevision(
            id=row["id"],
            document_id=row["document_id"],
            baseline_id=row["baseline_id"],
            path=row["path"],
            content_hash=row["content_hash"],
            format=row["format"],
        )

    @staticmethod
    def _to_membership(
        row: sqlite3.Row,
    ) -> DocumentMembership:
        return DocumentMembership(
            id=row["id"],
            document_id=row["document_id"],
            record_entity_id=row["record_entity_id"],
        )

    @staticmethod
    def _to_location(
        row: sqlite3.Row,
    ) -> DocumentLocation:
        return DocumentLocation(
            id=row["id"],
            document_revision_id=row[
                "document_revision_id"
            ],
            record_revision_id=row[
                "record_revision_id"
            ],
            anchor=row["anchor"],
            line_start=row["line_start"],
            line_end=row["line_end"],
        )