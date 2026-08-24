# Thread ID & ExecutionContext
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from .state import StageEnum


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)[:24]


@dataclass
class ExecutionContext:
    project_id: str
    session_id: str
    stage: StageEnum = StageEnum.REFINEMENT

    @property
    def thread_id(self) -> str:
        """Composite thread ID matching LangGraph checkpoint persistence."""
        #return f"{self.project_id}:{self.session_id}:{self.stage.value}"
        return self.session_id

    @classmethod
    def create(cls, project_id: Optional[str] = None, user_prompt: str = "") -> "ExecutionContext":
        proj = project_id or Path.cwd().name or "default-project"
        slug = slugify(user_prompt) if user_prompt else "session"
        short_id = uuid.uuid4().hex[:6]
        sess_id = f"{slug}-{short_id}"
        return cls(project_id=proj, session_id=sess_id)