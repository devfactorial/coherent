from __future__ import annotations

from dataclasses import dataclass

from .records import Record


@dataclass(frozen=True, kw_only=True)
class GraphNode:
    """
    A node in the governance graph.

    A GraphNode wraps a domain Record and exposes the record's
    revision identity as the graph node identity.

    The domain record remains the source of truth for the node's
    business data.
    """

    record: Record

    @property
    def id(self) -> str:
        """
        Return the graph node identifier.

        Revision IDs are used as graph node identifiers because
        relationships in the governance graph are revision-aware.
        """
        return self.record.meta.revision_id

    @property
    def entity_id(self) -> str:
        """
        Return the stable logical entity identifier.

        Multiple revisions may belong to the same entity.
        """
        return self.record.meta.entity_id

    @property
    def version(self) -> str:
        """Return the record version."""
        return self.record.meta.version

    @property
    def status(self):
        """Return the revision lifecycle status."""
        return self.record.meta.status

    @property
    def owner_id(self) -> str:
        """Return the owner of the record."""
        return self.record.meta.owner_id

    @property
    def kind(self) -> str:
        """
        Return the domain record type.

        Examples:
            REQUIREMENT
            CONSTRAINT
            DECISION
            EVIDENCE
        """
        return type(self.record).__name__.upper()

    def is_same_entity(self, other: GraphNode) -> bool:
        """
        Return True when two nodes represent revisions of
        the same logical entity.
        """
        return self.entity_id == other.entity_id

    def is_same_revision(self, other: GraphNode) -> bool:
        """
        Return True when two nodes represent the same revision.
        """
        return self.id == other.id