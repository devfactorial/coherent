# TaskNode & DAG models

from enum import Enum
from typing import List
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ScopeContract(BaseModel):
    primary_targets: List[str] = Field(default_factory=list)
    dynamic_expansion_patterns: List[str] = Field(
        default_factory=lambda: ["app/**/router.py", "app/**/__init__.py"]
    )
    immutable_read_only: List[str] = Field(
        default_factory=lambda: ["tests/**"]
    )


class TaskNode(BaseModel):
    id: str
    title: str
    description: str
    scope: ScopeContract = Field(default_factory=ScopeContract)
    dependencies: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    verification_command: str
    status: TaskStatus = TaskStatus.PENDING


class TaskDAG(BaseModel):
    tasks: List[TaskNode] = Field(default_factory=list)

    def get_task(self, task_id: str) -> TaskNode | None:
        for t in self.tasks:
            if t.id == task_id:
                return t
        return None