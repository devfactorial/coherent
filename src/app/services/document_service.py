from __future__ import annotations

import hashlib
from uuid import uuid4

from app.database.repositories.document_repository import DocumentRepository
from app.models.graph.records import (
    Document,
    DocumentLocation,
    DocumentMembership,
    DocumentRevision,
    Record,
)


class DocumentService:
    """
    Application service for managing logical documents, document
    revisions, record membership, and record locations.

    Responsibilities:
        - Manage logical Document identity.
        - Create immutable DocumentRevision metadata.
        - Persist the current document projection.
        - Maintain DocumentMembership.
        - Maintain DocumentLocation mappings.
        - Perform Markdown section manipulation.
        - Verify integrity of the current document projection.

    Architectural model:

        Document
            |
            +-- DocumentRevision
            |       |
            |       +-- DocumentLocation
            |
            +-- DocumentMembership

    The Markdown file is a projection of governed records.

    Important distinction:

        RecordRevision
            = governed semantic revision of a record.

        DocumentRevision
            = snapshot of the rendered document projection.

    This service does not own:
        - Graph relationships.
        - Provenance relationships.
        - Workflow approval.
        - Record lifecycle/state transitions.
        - Record revision storage.
        - Semantic record versioning.

    Document revision IDs identify projection snapshots. They are not
    semantic versions such as v1, v2, or v3.
    """

    SUPPORTED_FORMAT = "markdown"

    def __init__(
        self,
        repository: DocumentRepository,
    ) -> None:
        self._repository = repository

    # =========================================================
    # Logical document lifecycle
    # =========================================================

    def create(
        self,
        *,
        document_id: str,
        baseline_id: str,
        path: str,
        content: str = "",
        format: str = SUPPORTED_FORMAT,
        document_revision_id: str | None = None,
    ) -> DocumentRevision:
        """
        Create a logical document and its initial projection revision.

        The logical document identity remains stable across revisions.

        The current Markdown projection is stored at Document.path.

        Args:
            document_id:
                Stable logical document identity.

            baseline_id:
                Governance baseline associated with this projection.

            path:
                Project-relative filesystem path.

            content:
                Initial Markdown projection.

            format:
                Document format. Currently only Markdown is supported.

            document_revision_id:
                Optional explicit revision ID. Normally the service
                generates this automatically. Supplying one is useful
                for deterministic imports, replay, or testing.

        Returns:
            The initial DocumentRevision.

        Raises:
            ValueError:
                If the document already exists or the format is
                unsupported.
        """

        self._validate_format(format)

        if self._repository.document_exists(document_id):
            raise ValueError(
                f"Document already exists: {document_id}"
            )

        document = Document(
            id=document_id,
            path=path,
            format=format,
        )

        self._repository.save_document(
            document
        )

        revision_id = (
            document_revision_id
            or self._generate_revision_id(
                document_id
            )
        )

        content_hash = self._calculate_hash(
            content
        )

        revision = DocumentRevision(
            id=revision_id,
            document_id=document_id,
            baseline_id=baseline_id,
            path=path,
            content_hash=content_hash,
            format=format,
        )

        self._repository.save_revision(
            revision
        )

        self._repository.write_content(
            document_id,
            content,
        )

        return revision

    def get(
        self,
        document_id: str,
    ) -> Document | None:
        """Return a logical document, or None if it does not exist."""

        return self._repository.get_document(
            document_id
        )

    def require(
        self,
        document_id: str,
    ) -> Document:
        """Return a logical document or raise KeyError."""

        document = self.get(
            document_id
        )

        if document is None:
            raise KeyError(
                f"Document not found: {document_id}"
            )

        return document

    def read(
        self,
        document_id: str,
    ) -> str:
        """Read the current document projection."""

        self.require(document_id)

        return self._repository.read_content(
            document_id
        )

    def delete(
        self,
        document_id: str,
    ) -> None:
        """
        Delete a logical document and its associated metadata.

        Repository-level foreign-key relationships are responsible
        for deleting dependent revisions, memberships, and locations.

        The repository also removes the current projection file.
        """

        self._repository.delete_document(
            document_id
        )

    # =========================================================
    # Document revisions
    # =========================================================

    def get_revision(
        self,
        document_revision_id: str,
    ) -> DocumentRevision | None:
        """Return a document revision by ID."""

        return self._repository.get_revision(
            document_revision_id
        )

    def require_revision(
        self,
        document_revision_id: str,
    ) -> DocumentRevision:
        """Return a document revision or raise KeyError."""

        revision = self.get_revision(
            document_revision_id
        )

        if revision is None:
            raise KeyError(
                f"Document revision not found: "
                f"{document_revision_id}"
            )

        return revision

    def get_revisions(
        self,
        document_id: str,
    ) -> list[DocumentRevision]:
        """
        Return all document revisions in creation order.

        The repository guarantees that the returned list is ordered
        from oldest to newest.
        """

        self.require(document_id)

        return self._repository.get_revisions(
            document_id
        )

    def update(
        self,
        *,
        document_id: str,
        baseline_id: str,
        content: str,
        document_revision_id: str | None = None,
    ) -> DocumentRevision:
        """
        Create a new immutable document revision and make its content
        the current document projection.

        The logical Document identity is preserved.

        Existing DocumentRevision records are never overwritten.

        The document revision represents the complete rendered
        document state at this point in time. It is not a semantic
        version of an individual governed record.
        """

        document = self.require(
            document_id
        )

        content_hash = self._calculate_hash(
            content
        )

        revision_id = (
            document_revision_id
            or self._generate_revision_id(
                document_id
            )
        )

        revision = DocumentRevision(
            id=revision_id,
            document_id=document.id,
            baseline_id=baseline_id,
            path=document.path,
            content_hash=content_hash,
            format=document.format,
        )

        self._repository.save_revision(
            revision
        )

        self._repository.write_content(
            document_id,
            content,
        )

        return revision

    def content_hash(
        self,
        document_id: str,
    ) -> str:
        """
        Return the hash of the current document projection.

        The current projection is represented by the most recently
        created DocumentRevision.

        Returns an empty string when the document exists but has no
        recorded revision.
        """

        self.require(document_id)

        revisions = self._repository.get_revisions(
            document_id
        )

        if not revisions:
            return ""

        return revisions[-1].content_hash

    # =========================================================
    # Projection integrity
    # =========================================================

    def verify_integrity(
        self,
        document_id: str,
    ) -> bool:
        """
        Verify that the current filesystem projection matches the
        latest governed DocumentRevision.

        This detects changes made directly to the Markdown file by
        humans, coding agents, editors, or other processes without
        going through DocumentService.

        Returns:
            True when the current projection matches the latest
            DocumentRevision hash.

        Raises:
            KeyError:
                If the document does not exist.

            FileNotFoundError:
                If the current projection file does not exist.

            ValueError:
                If the document has no recorded revision.
        """

        self.require(document_id)

        revisions = self._repository.get_revisions(
            document_id
        )

        if not revisions:
            raise ValueError(
                f"Document has no recorded revision: "
                f"{document_id}"
            )

        actual_content = self._repository.read_content(
            document_id
        )

        actual_hash = self._calculate_hash(
            actual_content
        )

        expected_hash = revisions[-1].content_hash

        return actual_hash == expected_hash

    def verify_integrity_details(
        self,
        document_id: str,
    ) -> tuple[str, str]:
        """
        Return the expected and actual hashes for the current
        document projection.

        Returns:
            (expected_hash, actual_hash)

        This method is useful to callers that need to explain
        integrity drift rather than only receive a boolean result.
        """

        self.require(document_id)

        revisions = self._repository.get_revisions(
            document_id
        )

        if not revisions:
            raise ValueError(
                f"Document has no recorded revision: "
                f"{document_id}"
            )

        actual_content = self._repository.read_content(
            document_id
        )

        actual_hash = self._calculate_hash(
            actual_content
        )

        expected_hash = revisions[-1].content_hash

        return expected_hash, actual_hash

    # =========================================================
    # Record membership
    # =========================================================

    def add_membership(
        self,
        *,
        document_id: str,
        record_entity_id: str,
        membership_id: str | None = None,
    ) -> DocumentMembership:
        """
        Add a governed record to a logical document.

        Membership is based on the stable record entity ID, not a
        particular record revision.

        A record may legitimately belong to multiple documents.
        Therefore uniqueness is scoped to:

            document_id + record_entity_id
        """

        self.require(document_id)

        if not record_entity_id.strip():
            raise ValueError(
                "Record entity ID cannot be empty"
            )

        existing = self._repository.get_membership(
            document_id,
            record_entity_id,
        )

        if existing is not None:
            return existing

        membership = DocumentMembership(
            id=(
                membership_id
                or self._membership_id(
                    document_id=document_id,
                    record_entity_id=record_entity_id,
                )
            ),
            document_id=document_id,
            record_entity_id=record_entity_id,
        )

        self._repository.save_membership(
            membership
        )

        return membership

    def get_membership(
        self,
        *,
        document_id: str,
        record_entity_id: str,
    ) -> DocumentMembership | None:
        """Return membership for a record in a document."""

        return self._repository.get_membership(
            document_id,
            record_entity_id,
        )

    def get_memberships(
        self,
        document_id: str,
    ) -> list[DocumentMembership]:
        """Return all governed records belonging to a document."""

        self.require(document_id)

        return self._repository.get_memberships(
            document_id
        )

    def remove_membership(
        self,
        *,
        document_id: str,
        record_entity_id: str,
    ) -> None:
        """Remove a governed record from a logical document."""

        self._repository.delete_membership(
            document_id,
            record_entity_id,
        )

    # =========================================================
    # Record projection
    # =========================================================

    def upsert_record(
        self,
        *,
        document_id: str,
        baseline_id: str,
        record: Record,
        section_content: str,
        anchor: str,
        format: str = SUPPORTED_FORMAT,
        document_revision_id: str | None = None,
    ) -> tuple[DocumentRevision, DocumentLocation]:
        """
        Add or update a record's projection inside an existing
        logical document.

        The logical document must already exist.

        The record's stable entity ID becomes document membership.

        The record revision ID is used only for the location mapping.

        Workflow:

            record
                |
                +-- stable entity ID
                |       |
                |       +--> DocumentMembership
                |
                +-- revision ID
                        |
                        +--> DocumentLocation

        A new DocumentRevision represents the complete document
        projection after the record has been rendered.

        The document itself is not created by this method.
        """

        self._validate_format(format)
        self._validate_anchor(anchor)

        document = self.require(
            document_id
        )

        if document.format != format:
            raise ValueError(
                f"Document {document.id} uses format "
                f"{document.format}, not {format}"
            )

        record_entity_id = record.meta.entity_id
        record_revision_id = record.meta.revision_id

        if not record_entity_id.strip():
            raise ValueError(
                "Record entity ID cannot be empty"
            )

        if not record_revision_id.strip():
            raise ValueError(
                "Record revision ID cannot be empty"
            )

        # ---------------------------------------------------------
        # Update current document projection
        # ---------------------------------------------------------

        current_content = self.read(
            document_id
        )

        updated_content = self._upsert_section(
            content=current_content,
            anchor=anchor,
            section_content=section_content,
        )

        revision = self.update(
            document_id=document_id,
            baseline_id=baseline_id,
            content=updated_content,
            document_revision_id=document_revision_id,
        )

        # ---------------------------------------------------------
        # Maintain explicit document membership
        # ---------------------------------------------------------

        self.add_membership(
            document_id=document_id,
            record_entity_id=record_entity_id,
        )

        # ---------------------------------------------------------
        # Create location against the new document revision
        # ---------------------------------------------------------

        location = self._create_location(
            document_revision_id=revision.id,
            record_revision_id=record_revision_id,
            anchor=anchor,
            content=updated_content,
        )

        self._repository.save_location(
            location
        )

        return revision, location

    # =========================================================
    # Document location helpers
    # =========================================================

    def get_location(
        self,
        *,
        document_revision_id: str,
        record_revision_id: str,
    ) -> DocumentLocation | None:
        """
        Return the location of a record revision within a document
        revision.
        """

        return self._repository.get_location(
            document_revision_id,
            record_revision_id,
        )

    def get_locations(
        self,
        document_revision_id: str,
    ) -> list[DocumentLocation]:
        """Return all record locations in a document revision."""

        self.require_revision(
            document_revision_id
        )

        return self._repository.get_locations(
            document_revision_id
        )

    def delete_location(
        self,
        *,
        document_revision_id: str,
        record_revision_id: str,
    ) -> None:
        """Delete a record location from a document revision."""

        self._repository.delete_location(
            document_revision_id,
            record_revision_id,
        )

    # =========================================================
    # Markdown manipulation
    # =========================================================

    @staticmethod
    def _upsert_section(
        *,
        content: str,
        anchor: str,
        section_content: str,
    ) -> str:
        """
        Replace an existing Markdown section identified by anchor,
        or append the section if the anchor does not exist.
        """

        current = content.rstrip()

        start = DocumentService._find_section_start(
            content=current,
            anchor=anchor,
        )

        replacement = DocumentService._normalize_section(
            section_content
        )

        if start is None:
            if not current:
                return replacement

            return (
                current
                + "\n\n"
                + replacement
            )

        end = DocumentService._find_section_end(
            content=current,
            start=start,
        )

        return (
            current[:start]
            + replacement
            + current[end:]
        )

    @staticmethod
    def _find_section_start(
        *,
        content: str,
        anchor: str,
    ) -> int | None:
        """Return the character offset where an anchor begins."""

        lines = content.splitlines(
            keepends=True
        )

        offset = 0

        for line in lines:
            line_without_newline = (
                line.rstrip("\n\r")
            )

            if line_without_newline.strip() == anchor:
                return offset

            offset += len(line)

        return None

    @staticmethod
    def _find_section_end(
        *,
        content: str,
        start: int,
    ) -> int:
        """
        Return the character offset where the section ends.

        A section ends immediately before the next Markdown heading
        at the same or higher level.
        """

        lines = content[start:].splitlines(
            keepends=True
        )

        if not lines:
            return len(content)

        first_line = lines[0].strip()

        heading_level = (
            DocumentService._heading_level(
                first_line
            )
        )

        if heading_level is None:
            return len(content)

        offset = start + len(lines[0])

        for line in lines[1:]:
            stripped = line.strip()

            current_level = (
                DocumentService._heading_level(
                    stripped
                )
            )

            if (
                current_level is not None
                and current_level <= heading_level
            ):
                return offset

            offset += len(line)

        return len(content)

    @staticmethod
    def _find_anchor_lines(
        *,
        content: str,
        anchor: str,
    ) -> tuple[int, int]:
        """Return 1-based start/end line numbers for a section."""

        lines = content.splitlines()

        start_index: int | None = None

        for index, line in enumerate(lines):
            if line.strip() == anchor:
                start_index = index
                break

        if start_index is None:
            raise ValueError(
                f"Anchor not found in document: {anchor}"
            )

        heading_level = (
            DocumentService._heading_level(
                lines[start_index].strip()
            )
        )

        if heading_level is None:
            raise ValueError(
                f"Anchor is not a valid Markdown heading: "
                f"{anchor}"
            )

        end_index = len(lines) - 1

        for index in range(
            start_index + 1,
            len(lines),
        ):
            current_level = (
                DocumentService._heading_level(
                    lines[index].strip()
                )
            )

            if (
                current_level is not None
                and current_level <= heading_level
            ):
                end_index = index - 1
                break

        return (
            start_index + 1,
            end_index + 1,
        )

    @staticmethod
    def _heading_level(
        line: str,
    ) -> int | None:
        """Return the Markdown ATX heading level."""

        stripped = line.strip()

        if not stripped:
            return None

        level = 0

        for character in stripped:
            if character != "#":
                break

            level += 1

        if level == 0 or level > 6:
            return None

        if len(stripped) > level:
            if not stripped[level].isspace():
                return None

        return level

    # =========================================================
    # Validation
    # =========================================================

    @staticmethod
    def _validate_anchor(
        anchor: str,
    ) -> None:
        if not anchor or not anchor.strip():
            raise ValueError(
                "Document anchor cannot be empty"
            )

        if (
            DocumentService._heading_level(
                anchor.strip()
            )
            is None
        ):
            raise ValueError(
                f"Invalid Markdown heading anchor: {anchor}"
            )

    @staticmethod
    def _validate_format(
        format: str,
    ) -> None:
        if format != DocumentService.SUPPORTED_FORMAT:
            raise ValueError(
                f"Unsupported document format: {format}"
            )

    # =========================================================
    # Location construction
    # =========================================================

    @staticmethod
    def _create_location(
        *,
        document_revision_id: str,
        record_revision_id: str,
        anchor: str,
        content: str,
    ) -> DocumentLocation:
        line_start, line_end = (
            DocumentService._find_anchor_lines(
                content=content,
                anchor=anchor,
            )
        )

        return DocumentLocation(
            id=DocumentService._location_id(
                document_revision_id=document_revision_id,
                record_revision_id=record_revision_id,
            ),
            document_revision_id=document_revision_id,
            record_revision_id=record_revision_id,
            anchor=anchor,
            line_start=line_start,
            line_end=line_end,
        )

    @staticmethod
    def _location_id(
        *,
        document_revision_id: str,
        record_revision_id: str,
    ) -> str:
        return (
            f"LOC-{document_revision_id}-"
            f"{record_revision_id}"
        )

    # =========================================================
    # ID helpers
    # =========================================================

    @staticmethod
    def _generate_revision_id(
        document_id: str,
    ) -> str:
        """
        Generate a unique document projection revision ID.

        This is deliberately not a semantic version such as v1/v2.
        Semantic versioning belongs to governed record revisions.
        """

        return (
            f"DOCREV-{document_id}-"
            f"{uuid4().hex[:12]}"
        )

    @staticmethod
    def _membership_id(
        *,
        document_id: str,
        record_entity_id: str,
    ) -> str:
        return (
            f"MEM-{document_id}-{record_entity_id}"
        )

    # =========================================================
    # General helpers
    # =========================================================

    @staticmethod
    def _normalize_section(
        content: str,
    ) -> str:
        normalized = content.strip()

        if not normalized:
            raise ValueError(
                "Section content cannot be empty"
            )

        return normalized + "\n"

    @staticmethod
    def _calculate_hash(
        content: str,
    ) -> str:
        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()