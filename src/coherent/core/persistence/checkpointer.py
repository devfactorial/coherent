# Async SQLite saver factory & session queries

from pathlib import Path
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from coherent.config import get_settings
import aiosqlite
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_checkpointer() -> AsyncSqliteSaver:
    """Returns an async SQLite checkpointer connected to .coherent/state.db."""
    settings = get_settings()
    db_path = settings.sqlite_db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    async with AsyncSqliteSaver.from_conn_string(str(db_path)) as saver:
        yield saver