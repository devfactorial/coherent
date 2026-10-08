from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.sqlalchemy.base import Base


class BaselineModel(Base):
    __tablename__ = "baselines"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    scope: Mapped[str] = mapped_column(String(4000), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )

    __table_args__ = (
        Index("ix_baselines_status_created_at", "status", "created_at"),
    )


class BaselineMembershipModel(Base):
    __tablename__ = "baseline_memberships"

    baseline_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("baselines.id", ondelete="CASCADE"),
        primary_key=True,
    )
    revision_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("governed_records.revision_id", ondelete="RESTRICT"),
        primary_key=True,
    )

    __table_args__ = (
        Index("ix_baseline_memberships_revision", "revision_id"),
    )
