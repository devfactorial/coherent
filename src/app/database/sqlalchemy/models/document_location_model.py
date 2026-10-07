from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.sqlalchemy.base import Base


class DocumentLocationModel(Base):
    __tablename__ = "document_locations"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    document_revision_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey(
            "document_revisions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    record_revision_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    anchor: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    line_start: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    line_end: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_document_locations_document_revision",
            "document_revision_id",
        ),
        Index(
            "ix_document_locations_record_revision",
            "record_revision_id",
        ),
        Index(
            "ix_document_locations_document_record",
            "document_revision_id",
            "record_revision_id",
            unique=True,
        ),
    )