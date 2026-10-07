# src/app/database/sqlalchemy/models.py

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.sqlalchemy.base import Base


class GovernedRecordRow(Base):
    __tablename__ = "governed_records"

    revision_id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    entity_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    record_type: Mapped[str] = mapped_column(
        String(100),
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
        String(50),
        nullable=False,
    )

    record_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "idx_governed_records_entity",
            "entity_id",
        ),
        Index(
            "idx_governed_records_entity_version",
            "entity_id",
            "version",
        ),
    )


class ProvenanceEventRow(Base):
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

    record_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    revision_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    record_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
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
        String(64),
        nullable=False,
    )

    approval_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    __table_args__ = (
        Index(
            "idx_provenance_events_record",
            "record_id",
        ),
        Index(
            "idx_provenance_events_revision",
            "revision_id",
        ),
        Index(
            "idx_provenance_events_timestamp",
            "timestamp",
        ),
        Index(
            "idx_provenance_events_actor",
            "actor",
        ),
    )


class ApprovalRow(Base):
    __tablename__ = "approvals"

    approval_id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    record_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    revision_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    record_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    decision: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    actor: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    actor_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        Index(
            "idx_approvals_record",
            "record_id",
        ),
        Index(
            "idx_approvals_revision",
            "revision_id",
        ),
        Index(
            "idx_approvals_actor",
            "actor",
        ),
        Index(
            "idx_approvals_timestamp",
            "timestamp",
        ),
    )