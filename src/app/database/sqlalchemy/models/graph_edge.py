from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.sqlalchemy.base import Base


class GraphEdgeModel(Base):
    __tablename__ = "graph_edges"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    source_revision_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey(
            "graph_nodes.revision_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    target_revision_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey(
            "graph_nodes.revision_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    edge_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    basis: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_graph_edges_source",
            "source_revision_id",
        ),
        Index(
            "ix_graph_edges_target",
            "target_revision_id",
        ),
        Index(
            "ix_graph_edges_type",
            "edge_type",
        ),
    )