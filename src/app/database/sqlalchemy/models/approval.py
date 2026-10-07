from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.sqlalchemy.base import Base


class ApprovalModel(Base):
    __tablename__ = "approvals"

    approval_id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    record_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    revision_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
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
            "ix_approvals_revision_timestamp",
            "revision_id",
            "timestamp",
        ),
    )