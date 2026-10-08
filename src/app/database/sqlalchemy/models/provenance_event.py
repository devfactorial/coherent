from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.sqlalchemy.base import Base


class ProvenanceEventModel(Base):
    __tablename__ = "provenance_events"

    event_id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    actor: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    actor_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    operation: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    subject_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    subject_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    revision_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    record_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    previous_revision_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    previous_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    payload_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    approval_id: Mapped[str | None] = mapped_column(
        String(255),
        ForeignKey("approvals.approval_id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    __table_args__ = (
        Index(
            "ix_provenance_events_subject_timestamp",
            "subject_type",
            "subject_id",
            "timestamp",
        ),
        Index(
            "ix_provenance_events_record_timestamp",
            "subject_id",
            "timestamp",
        ),
        Index(
            "ix_provenance_events_actor",
            "actor",
        ),
    )
