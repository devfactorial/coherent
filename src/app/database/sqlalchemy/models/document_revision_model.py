from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.sqlalchemy.base import Base


class DocumentRevisionModel(Base):
    __tablename__ = "document_revisions"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    document_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    baseline_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    path: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    content_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    format: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_document_revisions_document",
            "document_id",
        ),
        Index(
            "ix_document_revisions_baseline",
            "baseline_id",
        ),
    )