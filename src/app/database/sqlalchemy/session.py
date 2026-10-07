from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


class Database:
    """
    SQLAlchemy database infrastructure.

    Owns:
        - SQLAlchemy Engine
        - Session factory
        - Session lifecycle

    Does NOT own:
        - domain models
        - repositories
        - schema creation/migrations
    """

    def __init__(
        self,
        database_path: str | Path,
    ) -> None:
        self._database_path = Path(database_path)

        self._database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._engine = create_engine(
            self._build_sqlite_url(),
            future=True,
        )

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
        """
        Create a new SQLAlchemy session.

        The caller owns the session and is responsible for closing it.
        """
        return self._session_factory()

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        """
        Transactional session scope.

        Commit on success.
        Roll back on exception.
        Always close the session.
        """
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
        """
        Dispose the SQLAlchemy connection pool.
        """
        self._engine.dispose()

    def _build_sqlite_url(self) -> str:
        return f"sqlite:///{self._database_path}"