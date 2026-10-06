from __future__ import annotations

from dataclasses import dataclass

from .enums import EdgeBasis, EdgeType, RevisionStatus


@dataclass(frozen=True, kw_only=True)
class GraphEdge:
    """
    A directed relationship between two graph nodes.

    Graph relationships are revision-aware: both source and target
    identify a specific record revision.
    """

    id: str
    source_revision_id: str
    target_revision_id: str
    edge_type: EdgeType

    status: RevisionStatus = RevisionStatus.DRAFT
    basis: EdgeBasis = EdgeBasis.EXPLICIT

    def connects(
        self,
        source_revision_id: str,
        target_revision_id: str,
    ) -> bool:
        """Return True if this edge connects the supplied revisions."""
        return (
            self.source_revision_id == source_revision_id
            and self.target_revision_id == target_revision_id
        )

    def originates_from(self, revision_id: str) -> bool:
        """Return True if this edge originates from the given revision."""
        return self.source_revision_id == revision_id

    def terminates_at(self, revision_id: str) -> bool:
        """Return True if this edge terminates at the given revision."""
        return self.target_revision_id == revision_id

    def is_active(self) -> bool:
        """Return True when the relationship is not superseded/rejected."""
        return self.status not in {
            RevisionStatus.SUPERSEDED,
            RevisionStatus.REJECTED,
            RevisionStatus.DEPRECATED,
        }

    def reversed(self) -> GraphEdge:
        """
        Return a new edge with source and target reversed.

        Note:
            This only reverses the direction. It does not automatically
            convert the edge type to its inverse relationship.
        """
        return GraphEdge(
            id=self.id,
            source_revision_id=self.target_revision_id,
            target_revision_id=self.source_revision_id,
            edge_type=self.edge_type,
            status=self.status,
            basis=self.basis,
        )