from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker


from app.database.repositories.graph_repository import GraphRepository
from app.database.sqlalchemy.models import (
    GraphEdgeModel,
    GraphNodeModel,
)
from app.models.graph.edge import GraphEdge
from app.models.graph.enums import (
    AssertionKind,
    EdgeBasis,
    EdgeType,
    RevisionStatus,
)
from app.models.graph.graph import Graph
from app.models.graph.node import GraphNode
from app.models.graph.records import (
    AcceptanceCriterion,
    ArtifactRevision,
    Assessment,
    AssessmentRun,
    Constraint,
    Decision,
    DesignElement,
    Evidence,
    InterfaceContract,
    Provenance,
    Requirement,
    RevisionMeta,
    TestCase,
    Record
)


class SQLAlchemyGraphRepository(GraphRepository):
    """
    SQLAlchemy-backed graph repository.

    SQLAlchemy stores:
        - graph nodes
        - graph edges
        - serialized domain records

    Markdown document content is NOT stored here.
    Document metadata/content is handled by DocumentRepository.

    Database schema is managed by Alembic.
    """
    
        

    def __init__(
        self,
        session_factory: sessionmaker[Session],
    ) -> None:
        self._session_factory = session_factory

    # ------------------------------------------------------------------
    # Graph persistence
    # ------------------------------------------------------------------

    def save_graph(
        self,
        graph: Graph,
    ) -> None:
        """
        Persist the complete graph atomically.

        Existing graph nodes and edges are replaced by the supplied
        graph within a single database transaction.
        """

        with self._session_factory() as session:
            session.execute(
                delete(GraphEdgeModel)
            )

            session.execute(
                delete(GraphNodeModel)
            )

            for node in graph.nodes.values():
                session.add(
                    self._to_node_model(node)
                )
                
            # Nodes must exist in the database before edges referencing
            # graph_nodes.revision_id are flushed.
            session.flush()

            for edge in graph.edges.values():
                session.add(
                    self._to_edge_model(edge)
                )

            session.commit()

    def list_node_revision_ids(self) -> list[str]:
        with self._session_factory() as session:
            stmt = (
                select(GraphNodeModel.revision_id)
                .order_by(GraphNodeModel.revision_id.asc())
            )
            return list(session.scalars(stmt).all())


    def list_edges(self) -> list[GraphEdge]:
        with self._session_factory() as session:
            stmt = (
                select(GraphEdgeModel)
                .order_by(GraphEdgeModel.id.asc())
            )

            rows = session.scalars(stmt).all()

            return [
                self._row_to_edge(row)
                for row in rows
            ]

    # ------------------------------------------------------------------
    # Node operations
    # ------------------------------------------------------------------

    def add_node(
        self,
        node: GraphNode,
    ) -> None:
        with self._session_factory() as session:
            session.add(
                self._to_node_model(node)
            )
            session.commit()

    def get_node(
        self,
        revision_id: str,
    ) -> GraphNode | None:
        with self._session_factory() as session:
            row = session.get(
                GraphNodeModel,
                revision_id,
            )

            if row is None:
                return None

            return self._row_to_node(row)

    def delete_node(
        self,
        revision_id: str,
    ) -> None:
        with self._session_factory() as session:
            row = session.get(
                GraphNodeModel,
                revision_id,
            )

            if row is not None:
                session.delete(row)
                session.commit()

    # ------------------------------------------------------------------
    # Edge operations
    # ------------------------------------------------------------------

    def add_edge(
        self,
        edge: GraphEdge,
    ) -> None:
        with self._session_factory() as session:
            session.add(
                self._to_edge_model(edge)
            )
            session.commit()

    def get_edge(
        self,
        edge_id: str,
    ) -> GraphEdge | None:
        with self._session_factory() as session:
            row = session.get(
                GraphEdgeModel,
                edge_id,
            )

            if row is None:
                return None

            return self._row_to_edge(row)

    def delete_edge(
        self,
        edge_id: str,
    ) -> None:
        with self._session_factory() as session:
            row = session.get(
                GraphEdgeModel,
                edge_id,
            )

            if row is not None:
                session.delete(row)
                session.commit()

    # ------------------------------------------------------------------
    # Edge traversal
    # ------------------------------------------------------------------

    def get_outgoing_edges(
        self,
        revision_id: str,
    ) -> list[GraphEdge]:
        stmt = (
            select(GraphEdgeModel)
            .where(
                GraphEdgeModel.source_revision_id
                == revision_id
            )
            .order_by(
                GraphEdgeModel.id.asc()
            )
        )

        with self._session_factory() as session:
            rows = session.scalars(stmt).all()

            return [
                self._row_to_edge(row)
                for row in rows
            ]

    def get_incoming_edges(
        self,
        revision_id: str,
    ) -> list[GraphEdge]:
        stmt = (
            select(GraphEdgeModel)
            .where(
                GraphEdgeModel.target_revision_id
                == revision_id
            )
            .order_by(
                GraphEdgeModel.id.asc()
            )
        )

        with self._session_factory() as session:
            rows = session.scalars(stmt).all()

            return [
                self._row_to_edge(row)
                for row in rows
            ]

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def clear(self) -> None:
        with self._session_factory() as session:
            session.execute(
                delete(GraphEdgeModel)
            )

            session.execute(
                delete(GraphNodeModel)
            )

            session.commit()

    # ------------------------------------------------------------------
    # Internal node persistence
    # ------------------------------------------------------------------

    @classmethod
    def _to_node_model(
        cls,
        node: GraphNode,
    ) -> GraphNodeModel:
        return GraphNodeModel(
            revision_id=node.id,
            entity_id=node.entity_id,
            record_type=node.kind,
            version=node.version,
            status=cls._enum_value(node.status),
            owner_id=node.owner_id,
            assertion_kind=cls._enum_value(
                node.record.meta.assertion_kind
            ),
        )

    

    # ------------------------------------------------------------------
    # Internal edge persistence
    # ------------------------------------------------------------------

    @staticmethod
    def _to_edge_model(
        edge: GraphEdge,
    ) -> GraphEdgeModel:
        return GraphEdgeModel(
            id=edge.id,
            source_revision_id=edge.source_revision_id,
            target_revision_id=edge.target_revision_id,
            edge_type=edge.edge_type.value,
            status=edge.status.value,
            basis=edge.basis.value,
        )

    @staticmethod
    def _row_to_edge(
        row: GraphEdgeModel,
    ) -> GraphEdge:
        return GraphEdge(
            id=row.id,
            source_revision_id=row.source_revision_id,
            target_revision_id=row.target_revision_id,
            edge_type=EdgeType(
                row.edge_type
            ),
            status=RevisionStatus(
                row.status
            ),
            basis=EdgeBasis(
                row.basis
            ),
        )


    @classmethod
    def _deserialize_record(
        cls,
        record_class: type,
        payload: dict[str, Any],
    ):
        """
        Reconstruct a domain record from JSON.

        RevisionMeta is nested inside every Record.
        """

        # Do not mutate the dictionary returned by json.loads().
        payload = dict(payload)

        meta_payload = payload.pop("meta")

        meta = RevisionMeta(
            entity_id=meta_payload["entity_id"],
            revision_id=meta_payload[
                "revision_id"
            ],
            version=meta_payload["version"],
            title=meta_payload["title"],
            status=RevisionStatus(
                meta_payload["status"]
            ),
            owner_id=meta_payload["owner_id"],
            assertion_kind=AssertionKind(
                meta_payload["assertion_kind"]
            ),
        )

        converted: dict[str, Any] = {
            "meta": meta
        }

        for key, value in payload.items():
            converted[key] = value

        # Restore enum fields specific to records.
        if record_class is ArtifactRevision:
            from app.models.graph.enums import ArtifactType

            converted["artifact_type"] = ArtifactType(
                converted["artifact_type"]
            )

        elif record_class is Requirement:
            from app.models.graph.enums import Priority

            converted["priority"] = Priority(
                converted["priority"]
            )

        elif record_class is Constraint:
            from app.models.graph.enums import (
                ConstraintType,
                QualityCategory,
            )

            converted["constraint_type"] = ConstraintType(
                converted["constraint_type"]
            )

            if converted.get("quality_category"):
                converted["quality_category"] = (
                    QualityCategory(
                        converted["quality_category"]
                    )
                )

        elif record_class is Assessment:
            from app.models.graph.enums import (
                AssessmentStage,
                EvidenceType,
                ExecutionMode,
            )

            converted["execution_mode"] = ExecutionMode(
                converted["execution_mode"]
            )

            converted["assessment_stage"] = (
                AssessmentStage(
                    converted["assessment_stage"]
                )
            )

            converted["expected_evidence"] = EvidenceType(
                converted["expected_evidence"]
            )

        elif record_class is Evidence:
            from app.models.graph.enums import EvidenceType

            converted["evidence_type"] = EvidenceType(
                converted["evidence_type"]
            )

        return record_class(**converted)

    @staticmethod
    def _enum_value(
        value: Any,
    ) -> Any:
        if isinstance(value, Enum):
            return value.value

        return value