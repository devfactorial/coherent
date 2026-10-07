from __future__ import annotations

from pathlib import Path

from app.database.repository_factory import RepositoryFactory
from app.database.sqlalchemy.session import Database


class DatabaseContext:
    """
    Application database context.

    Owns the SQLAlchemy database infrastructure and repository factory.
    """

    def __init__(
        self,
        database_path: str | Path,
    ) -> None:
        self._database = Database(database_path)

        self._repositories = RepositoryFactory(
            self._database.session_factory,
        )

    @property
    def database(self) -> Database:
        return self._database

    @property
    def repositories(self) -> RepositoryFactory:
        return self._repositories

    def close(self) -> None:
        self._database.dispose()