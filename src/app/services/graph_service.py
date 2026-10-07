from __future__ import annotations

from app.database.repositories.graph_repository import GraphRepository
from app.database.repositories.record_repository import RecordRepository
from app.models.graph.edge import GraphEdge
from app.models.graph.enums import (
    EdgeBasis,
    EdgeType,
    RevisionStatus,
)
from app.models.graph.graph import Graph
from app.models.graph.node import GraphNode
from app.models.graph.records import Record


class GraphService:
    """
    Application service for graph operations.

    Persistence is the source of truth for mutations.

    Mutation flow:

        repository
            ↓
        successful commit
            ↓
        in-memory graph

    The in-memory graph is never mutated before the repository
    operation succeeds.
    """

    def __init__(
        self,
        repository: GraphRepository,
        record_repository: RecordRepository,
        graph: Graph | None = None,
    ) -> None:
        self._repository = repository
        self._record_repository = record_repository
        self._graph = graph or Graph()

    @property
    def graph(self) -> Graph:
        return self._graph

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def load(self) -> Graph:
        """
        Load the persisted graph.

        The graph repository provides graph persistence data.
        The service resolves canonical records and composes the
        in-memory Graph.

        The existing in-memory graph is replaced only after the
        graph has been successfully reconstructed.
        """

        graph = Graph()

        revision_ids = (
            self._repository.list_node_revision_ids()
        )

        for revision_id in revision_ids:
            record = self._record_repository.get(revision_id)

            if record is None:
                raise ValueError(
                    f"Graph node references missing governed record: "
                    f"{revision_id}"
                )

            graph.add_node(
                GraphNode(record=record)
            )

        for edge in self._repository.list_edges():
            graph.add_edge(edge)

        self._graph = graph

        return self._graph

    def save(self) -> None:
        """
        Persist the current in-memory graph.
        """

        self._repository.save_graph(
            self._graph
        )

    def clear(self) -> None:
        """
        Clear persistent state first.

        The in-memory graph is cleared only after persistence
        succeeds.
        """

        self._repository.clear()

        self._graph.clear()

    # ------------------------------------------------------------------
    # Nodes
    # ------------------------------------------------------------------

    def load_graph(self) -> Graph:
        graph = Graph()

        revision_ids = self._repository.list_node_revision_ids()

        for revision_id in revision_ids:
            record = self._record_repository.get(revision_id)

            if record is None:
                raise ValueError(
                    f"Graph node references missing governed record: "
                    f"{revision_id}"
                )

            graph.add_node(GraphNode(record=record))

        for edge in self._repository.list_edges():
            graph.add_edge(edge)

        return graph

    def add_node(
        self,
        node: GraphNode,
    ) -> GraphNode:
        """
        Persist the node first.

        The in-memory graph is updated only after the repository
        operation succeeds.
        """

        if self.has_node(node.id):
            raise ValueError(
                f"Node already exists: {node.id}"
            )

        self._repository.add_node(node)

        self._graph.add_node(node)

        return node

    def get_node(
        self,
        revision_id: str,
    ) -> GraphNode | None:
        node = self._graph.get_node(
            revision_id
        )

        if node is not None:
            return node

        node = self._repository.get_node(
            revision_id
        )

        if node is not None:
            self._graph.add_node(node)

        return node

    def require_node(
        self,
        revision_id: str,
    ) -> GraphNode:
        node = self.get_node(
            revision_id
        )

        if node is None:
            raise KeyError(
                f"Graph node not found: {revision_id}"
            )

        return node

    def remove_node(
        self,
        revision_id: str,
    ) -> GraphNode:
        """
        Persist deletion first.

        SQLite's foreign-key cascade removes connected edges.
        The in-memory graph is updated only after the database
        deletion succeeds.
        """

        node = self.require_node(
            revision_id
        )

        self._repository.delete_node(
            revision_id
        )

        self._graph.remove_node(
            revision_id
        )

        return node

    # ------------------------------------------------------------------
    # Edges
    # ------------------------------------------------------------------

    def create_edge(
        self,
        edge_id: str,
        source_revision_id: str,
        target_revision_id: str,
        edge_type: EdgeType,
        *,
        status: RevisionStatus = RevisionStatus.DRAFT,
        basis: EdgeBasis = EdgeBasis.EXPLICIT,
    ) -> GraphEdge:
        edge = GraphEdge(
            id=edge_id,
            source_revision_id=source_revision_id,
            target_revision_id=target_revision_id,
            edge_type=edge_type,
            status=status,
            basis=basis,
        )

        return self.add_edge(edge)

    def add_edge(
        self,
        edge: GraphEdge,
    ) -> GraphEdge:
        """
        Persist the edge first.

        The repository validates that both endpoint nodes exist.
        """

        if self.has_edge(edge.id):
            raise ValueError(
                f"Edge already exists: {edge.id}"
            )

        self._repository.add_edge(edge)

        self._graph.add_edge(edge)

        return edge

    def get_edge(
        self,
        edge_id: str,
    ) -> GraphEdge | None:
        edge = self._graph.get_edge(
            edge_id
        )

        if edge is not None:
            return edge

        edge = self._repository.get_edge(
            edge_id
        )

        if edge is not None:
            self._graph.edges[edge.id] = edge

        return edge

    def require_edge(
        self,
        edge_id: str,
    ) -> GraphEdge:
        edge = self.get_edge(
            edge_id
        )

        if edge is None:
            raise KeyError(
                f"Graph edge not found: {edge_id}"
            )

        return edge

    def remove_edge(
        self,
        edge_id: str,
    ) -> GraphEdge:
        edge = self.require_edge(
            edge_id
        )

        self._repository.delete_edge(
            edge_id
        )

        self._graph.remove_edge(
            edge_id
        )

        return edge

    # ------------------------------------------------------------------
    # Traversal
    # ------------------------------------------------------------------

    def outgoing_edges(
        self,
        revision_id: str,
    ) -> list[GraphEdge]:
        edges = self._repository.get_outgoing_edges(
            revision_id
        )

        for edge in edges:
            if not self._graph.has_edge(edge.id):
                self._graph.edges[edge.id] = edge

        return edges

    def incoming_edges(
        self,
        revision_id: str,
    ) -> list[GraphEdge]:
        edges = self._repository.get_incoming_edges(
            revision_id
        )

        for edge in edges:
            if not self._graph.has_edge(edge.id):
                self._graph.edges[edge.id] = edge

        return edges

    def neighbors(
        self,
        revision_id: str,
    ) -> list[GraphNode]:
        outgoing = self.outgoing_edges(
            revision_id
        )

        incoming = self.incoming_edges(
            revision_id
        )

        neighbor_ids = {
            edge.target_revision_id
            for edge in outgoing
        }

        neighbor_ids.update(
            edge.source_revision_id
            for edge in incoming
        )

        neighbor_ids.discard(
            revision_id
        )

        result: list[GraphNode] = []

        for node_id in neighbor_ids:
            node = self.get_node(node_id)

            if node is not None:
                result.append(node)

        return result

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def has_node(
        self,
        revision_id: str,
    ) -> bool:
        return (
            self.get_node(revision_id)
            is not None
        )

    def has_edge(
        self,
        edge_id: str,
    ) -> bool:
        return (
            self.get_edge(edge_id)
            is not None
        )

    def node_count(self) -> int:
        return self._graph.node_count()

    def edge_count(self) -> int:
        return self._graph.edge_count()