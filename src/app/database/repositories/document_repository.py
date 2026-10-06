from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.graph.records import (
    Document,
    DocumentLocation,
    DocumentMembership,
    DocumentRevision,
)


class DocumentRepository(ABC):
    """
    Persistence abstraction for logical documents, document revisions,
    document membership, and rendered record locations.

    The repository owns persistence details. The service layer should
    not need to know whether documents are stored on a local filesystem,
    object storage, database, etc.

    Architectural model:

        Document
            |
            +-- DocumentRevision
            |
            +-- DocumentMembership
            |
            +-- DocumentLocation
    """

    # ============================================================
    # Logical documents
    # ============================================================

    @abstractmethod
    def save_document(
        self,
        document: Document,
    ) -> None:
        """Persist a logical document."""
        raise NotImplementedError

    @abstractmethod
    def get_document(
        self,
        document_id: str,
    ) -> Document | None:
        """Return a logical document by ID."""
        raise NotImplementedError

    @abstractmethod
    def delete_document(
        self,
        document_id: str,
    ) -> None:
        """
        Delete a logical document.

        The concrete repository is responsible for enforcing the
        configured cascade behavior for dependent metadata.
        """
        raise NotImplementedError

    @abstractmethod
    def document_exists(
        self,
        document_id: str,
    ) -> bool:
        """Return whether a logical document exists."""
        raise NotImplementedError

    # ============================================================
    # Document revisions
    # ============================================================

    @abstractmethod
    def save_revision(
        self,
        revision: DocumentRevision,
    ) -> None:
        """
        Persist a document revision.

        A document revision is immutable once persisted. Creating
        another state of the logical document creates another
        DocumentRevision.
        """
        raise NotImplementedError

    @abstractmethod
    def get_revision(
        self,
        document_revision_id: str,
    ) -> DocumentRevision | None:
        """Return a document revision by revision ID."""
        raise NotImplementedError

    @abstractmethod
    def get_revisions(
        self,
        document_id: str,
    ) -> list[DocumentRevision]:
        """
        Return all revisions of a logical document.

        Revisions must be returned in deterministic creation order,
        oldest first and newest last.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_revision(
        self,
        document_revision_id: str,
    ) -> None:
        """
        Delete a document revision.

        This operation should respect dependent DocumentLocation
        records according to repository integrity rules.
        """
        raise NotImplementedError

    # ============================================================
    # Current document content
    # ============================================================

    @abstractmethod
    def read_content(
        self,
        document_id: str,
    ) -> str:
        """
        Read the current physical document content.

        The logical Document determines the filesystem path.
        """
        raise NotImplementedError

    @abstractmethod
    def write_content(
        self,
        document_id: str,
        content: str,
    ) -> None:
        """
        Write the current physical document content.

        This updates the current Markdown projection.

        It does not itself create a DocumentRevision.
        """
        raise NotImplementedError

    # ============================================================
    # Document membership
    # ============================================================

    @abstractmethod
    def save_membership(
        self,
        membership: DocumentMembership,
    ) -> None:
        """
        Persist membership of a logical record in a document.

        Membership is identified by:

            document_id + record_entity_id

        and therefore represents a stable relationship between a
        logical record and a logical document.
        """
        raise NotImplementedError

    @abstractmethod
    def get_membership(
        self,
        document_id: str,
        record_entity_id: str,
    ) -> DocumentMembership | None:
        """
        Return membership of a logical record in a document.
        """
        raise NotImplementedError

    @abstractmethod
    def get_memberships(
        self,
        document_id: str,
    ) -> list[DocumentMembership]:
        """
        Return all logical records governed as members of a document.

        The returned collection should have deterministic ordering.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_membership(
        self,
        document_id: str,
        record_entity_id: str,
    ) -> None:
        """Remove a logical record from a document."""
        raise NotImplementedError

    # ============================================================
    # Rendered record locations
    # ============================================================

    @abstractmethod
    def save_location(
        self,
        location: DocumentLocation,
    ) -> None:
        """
        Persist the location of a record revision inside a particular
        document revision.

        A rendered occurrence is uniquely identified by:

            document_revision_id + record_revision_id
        """
        raise NotImplementedError

    @abstractmethod
    def get_location(
        self,
        document_revision_id: str,
        record_revision_id: str,
    ) -> DocumentLocation | None:
        """
        Return the location of a record revision inside a document
        revision.
        """
        raise NotImplementedError

    @abstractmethod
    def get_locations(
        self,
        document_revision_id: str,
    ) -> list[DocumentLocation]:
        """
        Return all rendered record locations for a document revision.

        The returned collection should have deterministic ordering.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_location(
        self,
        document_revision_id: str,
        record_revision_id: str,
    ) -> None:
        """
        Delete the location of a record revision from a document
        revision.
        """
        raise NotImplementedError