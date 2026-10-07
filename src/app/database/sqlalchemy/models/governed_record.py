from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.sqlalchemy.base import Base


class GovernedRecordModel(Base):
    __tablename__ = "governed_records"

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

    record_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )

    __table_args__ = (
        Index(
            "ix_governed_records_entity_version",
            "entity_id",
            "version",
        ),
    )