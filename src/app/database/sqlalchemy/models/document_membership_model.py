from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.sqlalchemy.base import Base


class DocumentMembershipModel(Base):
    __tablename__ = "document_memberships"

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

    record_entity_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_document_memberships_document",
            "document_id",
        ),
        Index(
            "ix_document_memberships_record",
            "record_entity_id",
        ),
        Index(
            "ix_document_memberships_document_record",
            "document_id",
            "record_entity_id",
            unique=True,
        ),
    )