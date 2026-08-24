# DocumentRef & registry models

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentRef(BaseModel):
    """Tracks a file artifact on disk without forcing rigid internal schemas."""
    path: Path
    doc_type: str = Field(default="general")
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    sha256_hash: Optional[str] = None

    def read_content(self) -> str:
        if not self.path.exists():
            raise FileNotFoundError(f"Referenced document not found at: {self.path}")
        return self.path.read_text(encoding="utf-8")

    def update_hash(self) -> None:
        content = self.read_content()
        self.sha256_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()


class ProjectKnowledgeRegistry(BaseModel):
    session_id: str
    doc_refs: List[DocumentRef] = Field(default_factory=list)

    def add_document(self, path: str | Path, doc_type: str = "general") -> DocumentRef:
        doc = DocumentRef(path=Path(path), doc_type=doc_type)
        if doc.path.exists():
            doc.update_hash()
        self.doc_refs.append(doc)
        return doc

    def get_all_raw_contents(self) -> Dict[str, str]:
        return {
            str(doc.path): doc.read_content()
            for doc in self.doc_refs
            if doc.path.exists()
        }