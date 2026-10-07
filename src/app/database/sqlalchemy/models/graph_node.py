from __future__ import annotations

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.sqlalchemy.base import Base


class GraphNodeModel(Base):
    __tablename__ = "graph_nodes"

    revision_id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    entity_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    record_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    owner_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    assertion_kind: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_graph_nodes_entity_version",
            "entity_id",
            "version",
        ),
    )