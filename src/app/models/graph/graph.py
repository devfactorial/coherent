from __future__ import annotations

from dataclasses import dataclass, field

from .edge import GraphEdge
from .node import GraphNode


@dataclass
class Graph:
    """
    In-memory representation of the governance/context graph.

    Nodes are indexed by revision ID.
    Edges are indexed by edge ID.
    """

    nodes: dict[str, GraphNode] = field(default_factory=dict)
    edges: dict[str, GraphEdge] = field(default_factory=dict)

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""

        if node.id in self.nodes:
            raise ValueError(
                f"Node already exists: {node.id}"
            )

        self.nodes[node.id] = node

    def get_node(self, revision_id: str) -> GraphNode | None:
        """Return a node by revision ID."""
        return self.nodes.get(revision_id)

    def require_node(self, revision_id: str) -> GraphNode:
        """Return a node or raise an error if it does not exist."""
        node = self.get_node(revision_id)

        if node is None:
            raise KeyError(
                f"Graph node not found: {revision_id}"
            )

        return node

    def remove_node(self, revision_id: str) -> GraphNode:
        """
        Remove a node and all edges connected to it.
        """

        node = self.require_node(revision_id)

        connected_edges = [
            edge_id
            for edge_id, edge in self.edges.items()
            if edge.source_revision_id == revision_id
            or edge.target_revision_id == revision_id
        ]

        for edge_id in connected_edges:
            del self.edges[edge_id]

        del self.nodes[revision_id]

        return node

    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge between two existing graph nodes."""

        if edge.id in self.edges:
            raise ValueError(
                f"Edge already exists: {edge.id}"
            )

        if edge.source_revision_id not in self.nodes:
            raise KeyError(
                f"Source node not found: {edge.source_revision_id}"
            )

        if edge.target_revision_id not in self.nodes:
            raise KeyError(
                f"Target node not found: {edge.target_revision_id}"
            )

        self.edges[edge.id] = edge

    def get_edge(self, edge_id: str) -> GraphEdge | None:
        """Return an edge by ID."""
        return self.edges.get(edge_id)

    def require_edge(self, edge_id: str) -> GraphEdge:
        """Return an edge or raise an error if it does not exist."""
        edge = self.get_edge(edge_id)

        if edge is None:
            raise KeyError(
                f"Graph edge not found: {edge_id}"
            )

        return edge

    def remove_edge(self, edge_id: str) -> GraphEdge:
        """Remove an edge from the graph."""
        edge = self.require_edge(edge_id)

        del self.edges[edge_id]

        return edge

    def outgoing_edges(self, revision_id: str) -> list[GraphEdge]:
        """Return edges originating from a node."""
        return [
            edge
            for edge in self.edges.values()
            if edge.source_revision_id == revision_id
        ]

    def incoming_edges(self, revision_id: str) -> list[GraphEdge]:
        """Return edges terminating at a node."""
        return [
            edge
            for edge in self.edges.values()
            if edge.target_revision_id == revision_id
        ]

    def connected_edges(self, revision_id: str) -> list[GraphEdge]:
        """Return all incoming and outgoing edges for a node."""
        return [
            edge
            for edge in self.edges.values()
            if (
                edge.source_revision_id == revision_id
                or edge.target_revision_id == revision_id
            )
        ]

    def neighbors(self, revision_id: str) -> list[GraphNode]:
        """
        Return nodes directly connected to the supplied node.

        Both incoming and outgoing relationships are considered.
        """

        neighbor_ids: set[str] = set()

        for edge in self.connected_edges(revision_id):
            if edge.source_revision_id == revision_id:
                neighbor_ids.add(edge.target_revision_id)

            if edge.target_revision_id == revision_id:
                neighbor_ids.add(edge.source_revision_id)

        return [
            self.nodes[node_id]
            for node_id in neighbor_ids
            if node_id in self.nodes
        ]

    def has_node(self, revision_id: str) -> bool:
        """Return True if the graph contains the node."""
        return revision_id in self.nodes

    def has_edge(self, edge_id: str) -> bool:
        """Return True if the graph contains the edge."""
        return edge_id in self.edges

    def node_count(self) -> int:
        """Return the number of nodes."""
        return len(self.nodes)

    def edge_count(self) -> int:
        """Return the number of edges."""
        return len(self.edges)

    def clear(self) -> None:
        """Remove all nodes and edges."""
        self.nodes.clear()
        self.edges.clear()