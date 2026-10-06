from __future__ import annotations

from app.config import Settings
from app.database.sqlite import SQLiteDatabase
from app.repositories.document_repository import DocumentRepository
from app.services.document import DocumentService


class Application:
    def __init__(self) -> None:
        pass