# src/app/database/sqlalchemy/base.py

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for aigov SQLAlchemy persistence models."""