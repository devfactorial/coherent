from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.sqlalchemy.base import Base


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    path: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
        unique=True,
    )

    format: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )