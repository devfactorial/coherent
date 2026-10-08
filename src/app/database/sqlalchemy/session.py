from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


class Database:
    """SQLAlchemy database infrastructure."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)

        self._engine = create_engine(
            self._build_sqlite_url(),
            future=True,
        )

        if self._engine.url.get_backend_name() == "sqlite":
            @event.listens_for(self._engine, "connect")
            def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                try:
                    cursor.execute("PRAGMA foreign_keys=ON")
                finally:
                    cursor.close()

        self._session_factory = sessionmaker(
            bind=self._engine,
            class_=Session,
            autoflush=False,
            expire_on_commit=False,
        )

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def session_factory(self) -> sessionmaker[Session]:
        return self._session_factory

    def create_session(self) -> Session:
        return self._session_factory()

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def dispose(self) -> None:
        self._engine.dispose()

    def _build_sqlite_url(self) -> str:
        return f"sqlite:///{self._database_path}"
