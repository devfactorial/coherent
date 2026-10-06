from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.graph.edge import GraphEdge
from app.models.graph.graph import Graph
from app.models.graph.node import GraphNode


class GraphRepository(ABC):
    """
    Persistence abstraction for the governance graph.

    This interface deliberately knows about the domain graph but does not
    prescribe how the graph is stored.
    """

    @abstractmethod
    def save_graph(self, graph: Graph) -> None:
        """
        Persist the complete graph.

        Implementations may use SQLite, PostgreSQL, or another persistence
        mechanism.
        """
        raise NotImplementedError

    @abstractmethod
    def load_graph(self) -> Graph:
        """
        Load the complete graph from persistence.
        """
        raise NotImplementedError

    @abstractmethod
    def add_node(self, node: GraphNode) -> None:
        """Persist a graph node."""
        raise NotImplementedError

    @abstractmethod
    def get_node(self, revision_id: str) -> GraphNode | None:
        """Retrieve a graph node by revision ID."""
        raise NotImplementedError

    @abstractmethod
    def delete_node(self, revision_id: str) -> None:
        """
        Delete a graph node.

        Implementations should also remove relationships that reference
        the deleted node.
        """
        raise NotImplementedError

    @abstractmethod
    def add_edge(self, edge: GraphEdge) -> None:
        """Persist a graph edge."""
        raise NotImplementedError

    @abstractmethod
    def get_edge(self, edge_id: str) -> GraphEdge | None:
        """Retrieve an edge by ID."""
        raise NotImplementedError

    @abstractmethod
    def delete_edge(self, edge_id: str) -> None:
        """Delete an edge."""
        raise NotImplementedError

    @abstractmethod
    def get_outgoing_edges(
        self,
        revision_id: str,
    ) -> list[GraphEdge]:
        """Return all outgoing edges for a node."""
        raise NotImplementedError

    @abstractmethod
    def get_incoming_edges(
        self,
        revision_id: str,
    ) -> list[GraphEdge]:
        """Return all incoming edges for a node."""
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Delete all graph data."""
        raise NotImplementedError