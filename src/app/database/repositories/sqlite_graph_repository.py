from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from app.database.repositories.graph_repository import GraphRepository
from app.models.graph.edge import GraphEdge
from app.models.graph.enums import (
    EdgeBasis,
    EdgeType,
    RevisionStatus,
)
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
    Requirement,
    RevisionMeta,
    TestCase,
    Provenance
)


class SQLiteGraphRepository(GraphRepository):
    """
    SQLite persistence for the domain graph.

    SQLite stores:
      - graph nodes
      - graph edges
      - serialized domain records

    Markdown document content is NOT stored here.
    Document metadata/content is handled by DocumentRepository.
    """

    _RECORD_TYPES: dict[str, type] = {
        "ARTIFACTREVISION": ArtifactRevision,
        "ACCEPTANCECRITERION": AcceptanceCriterion,
        "REQUIREMENT": Requirement,
        "CONSTRAINT": Constraint,
        "ASSESSMENT": Assessment,
        "DECISION": Decision,
        "DESIGNELEMENT": DesignElement,
        "INTERFACECONTRACT": InterfaceContract,
        "TESTCASE": TestCase,
        "ASSESSMENTRUN": AssessmentRun,
        "EVIDENCE": Evidence,
        "PROVENANCE": Provenance,
    }

    def __init__(
        self,
        database_path: str | Path,
    ) -> None:
        self._database_path = Path(database_path)

        self._database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    # ------------------------------------------------------------------
    # Connection / initialization
    # ------------------------------------------------------------------

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
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS graph_nodes (
                    revision_id TEXT PRIMARY KEY,
                    entity_id TEXT NOT NULL,
                    record_type TEXT NOT NULL,
                    version TEXT NOT NULL,
                    status TEXT NOT NULL,
                    owner_id TEXT NOT NULL,
                    assertion_kind TEXT NOT NULL,
                    record_json TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_graph_nodes_entity_id
                ON graph_nodes(entity_id)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_graph_nodes_record_type
                ON graph_nodes(record_type)
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS graph_edges (
                    id TEXT PRIMARY KEY,
                    source_revision_id TEXT NOT NULL,
                    target_revision_id TEXT NOT NULL,
                    edge_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    basis TEXT NOT NULL,

                    FOREIGN KEY(source_revision_id)
                        REFERENCES graph_nodes(revision_id)
                        ON DELETE CASCADE,

                    FOREIGN KEY(target_revision_id)
                        REFERENCES graph_nodes(revision_id)
                        ON DELETE CASCADE
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_graph_edges_source
                ON graph_edges(source_revision_id)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_graph_edges_target
                ON graph_edges(target_revision_id)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_graph_edges_type
                ON graph_edges(edge_type)
                """
            )

            connection.commit()

    # ------------------------------------------------------------------
    # Graph persistence
    # ------------------------------------------------------------------

    def save_graph(
        self,
        graph: Graph,
    ) -> None:
        """
        Persist the complete graph.

        This is intentionally implemented as a transaction so the
        database cannot end up with only half of the graph.
        """

        with self._connect() as connection:
            try:
                connection.execute("BEGIN")

                connection.execute(
                    "DELETE FROM graph_edges"
                )

                connection.execute(
                    "DELETE FROM graph_nodes"
                )

                for node in graph.nodes.values():
                    self._insert_node(
                        connection,
                        node,
                    )

                for edge in graph.edges.values():
                    self._insert_edge(
                        connection,
                        edge,
                    )

                connection.commit()

            except Exception:
                connection.rollback()
                raise

    def load_graph(self) -> Graph:
        graph = Graph()

        with self._connect() as connection:
            node_rows = connection.execute(
                """
                SELECT *
                FROM graph_nodes
                ORDER BY revision_id
                """
            ).fetchall()

            edge_rows = connection.execute(
                """
                SELECT *
                FROM graph_edges
                ORDER BY id
                """
            ).fetchall()

        for row in node_rows:
            node = self._row_to_node(row)
            graph.add_node(node)

        for row in edge_rows:
            edge = self._row_to_edge(row)
            graph.add_edge(edge)

        return graph

    # ------------------------------------------------------------------
    # Node operations
    # ------------------------------------------------------------------

    def add_node(
        self,
        node: GraphNode,
    ) -> None:
        with self._connect() as connection:
            self._insert_node(
                connection,
                node,
            )
            connection.commit()

    def get_node(
        self,
        revision_id: str,
    ) -> GraphNode | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM graph_nodes
                WHERE revision_id = ?
                """,
                (revision_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_node(row)

    def delete_node(
        self,
        revision_id: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                DELETE FROM graph_nodes
                WHERE revision_id = ?
                """,
                (revision_id,),
            )

            connection.commit()

    # ------------------------------------------------------------------
    # Edge operations
    # ------------------------------------------------------------------

    def add_edge(
        self,
        edge: GraphEdge,
    ) -> None:
        with self._connect() as connection:
            self._insert_edge(
                connection,
                edge,
            )
            connection.commit()

    def get_edge(
        self,
        edge_id: str,
    ) -> GraphEdge | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM graph_edges
                WHERE id = ?
                """,
                (edge_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_edge(row)

    def delete_edge(
        self,
        edge_id: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                DELETE FROM graph_edges
                WHERE id = ?
                """,
                (edge_id,),
            )

            connection.commit()

    # ------------------------------------------------------------------
    # Edge traversal
    # ------------------------------------------------------------------

    def get_outgoing_edges(
        self,
        revision_id: str,
    ) -> list[GraphEdge]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM graph_edges
                WHERE source_revision_id = ?
                ORDER BY id
                """,
                (revision_id,),
            ).fetchall()

        return [
            self._row_to_edge(row)
            for row in rows
        ]

    def get_incoming_edges(
        self,
        revision_id: str,
    ) -> list[GraphEdge]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM graph_edges
                WHERE target_revision_id = ?
                ORDER BY id
                """,
                (revision_id,),
            ).fetchall()

        return [
            self._row_to_edge(row)
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def clear(self) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM graph_edges"
            )

            connection.execute(
                "DELETE FROM graph_nodes"
            )

            connection.commit()

    # ------------------------------------------------------------------
    # Internal node persistence
    # ------------------------------------------------------------------

    def _insert_node(
        self,
        connection: sqlite3.Connection,
        node: GraphNode,
    ) -> None:
        record = node.record

        connection.execute(
            """
            INSERT INTO graph_nodes (
                revision_id,
                entity_id,
                record_type,
                version,
                status,
                owner_id,
                assertion_kind,
                record_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                node.id,
                node.entity_id,
                node.kind,
                node.version,
                self._enum_value(node.status),
                node.owner_id,
                self._enum_value(
                    record.meta.assertion_kind
                ),
                json.dumps(
                    self._serialize(record),
                    sort_keys=True,
                ),
            ),
        )

    def _row_to_node(
        self,
        row: sqlite3.Row,
    ) -> GraphNode:
        record_type = row["record_type"]

        record_class = self._RECORD_TYPES.get(
            record_type
        )

        if record_class is None:
            raise ValueError(
                f"Unknown graph record type: "
                f"{record_type}"
            )

        payload = json.loads(
            row["record_json"]
        )

        record = self._deserialize_record(
            record_class,
            payload,
        )

        return GraphNode(
            record=record
        )

    # ------------------------------------------------------------------
    # Internal edge persistence
    # ------------------------------------------------------------------

    def _insert_edge(
        self,
        connection: sqlite3.Connection,
        edge: GraphEdge,
    ) -> None:
        connection.execute(
            """
            INSERT INTO graph_edges (
                id,
                source_revision_id,
                target_revision_id,
                edge_type,
                status,
                basis
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                edge.id,
                edge.source_revision_id,
                edge.target_revision_id,
                edge.edge_type.value,
                edge.status.value,
                edge.basis.value,
            ),
        )

    @staticmethod
    def _row_to_edge(
        row: sqlite3.Row,
    ) -> GraphEdge:
        return GraphEdge(
            id=row["id"],
            source_revision_id=row[
                "source_revision_id"
            ],
            target_revision_id=row[
                "target_revision_id"
            ],
            edge_type=EdgeType(
                row["edge_type"]
            ),
            status=RevisionStatus(
                row["status"]
            ),
            basis=EdgeBasis(
                row["basis"]
            ),
        )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    @classmethod
    def _serialize(
        cls,
        value: Any,
    ) -> Any:
        """
        Convert dataclasses and enums into JSON-compatible values.
        """

        if isinstance(value, Enum):
            return value.value

        if is_dataclass(value):
            return {
                key: cls._serialize(field_value)
                for key, field_value in asdict(
                    value
                ).items()
            }

        if isinstance(value, dict):
            return {
                key: cls._serialize(field_value)
                for key, field_value in value.items()
            }

        if isinstance(value, list):
            return [
                cls._serialize(item)
                for item in value
            ]

        if isinstance(value, tuple):
            return [
                cls._serialize(item)
                for item in value
            ]

        return value

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

            converted["artifact_type"] = (
                ArtifactType(
                    converted["artifact_type"]
                )
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

            converted["constraint_type"] = (
                ConstraintType(
                    converted["constraint_type"]
                )
            )

            if converted.get(
                "quality_category"
            ):
                converted["quality_category"] = (
                    QualityCategory(
                        converted["quality_category"]
                    )
                )

        elif record_class is Assessment:
            from app.models.graph.enums import (
                AssessmentStage,
                ExecutionMode,
                EvidenceType,
            )

            converted["execution_mode"] = (
                ExecutionMode(
                    converted["execution_mode"]
                )
            )

            converted["assessment_stage"] = (
                AssessmentStage(
                    converted["assessment_stage"]
                )
            )

            converted["expected_evidence"] = (
                EvidenceType(
                    converted["expected_evidence"]
                )
            )

        elif record_class is Evidence:
            from app.models.graph.enums import EvidenceType

            converted["evidence_type"] = (
                EvidenceType(
                    converted["evidence_type"]
                )
            )

        return record_class(**converted)

    @staticmethod
    def _enum_value(
        value: Any,
    ) -> Any:
        if isinstance(value, Enum):
            return value.value

        return value