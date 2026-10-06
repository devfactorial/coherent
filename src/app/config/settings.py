from __future__ import annotations

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Runtime configuration for aigov.

    AIGOV_DATA_ROOT defines where aigov stores its persistent data:

        <AIGOV_DATA_ROOT>/
            db/
                aigov.sqlite
            documents/
                ...

    The value may be supplied through the environment or .env.
    """

    aigov_home: Path

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    @property
    def data_root(self) -> Path:
        return self.aigov_home / ".aigov"

    @property
    def database_path(self) -> Path:
        return self.data_root / "db" / "aigov.sqlite"

    @property
    def document_root(self) -> Path:
        return self.data_root / "documents"

    def initialize_storage(self) -> None:
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.document_root.mkdir(
            parents=True,
            exist_ok=True,
        )