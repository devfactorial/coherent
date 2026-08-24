# High-level Async Engine API

from typing import Any, AsyncGenerator, Dict, Optional
from coherent.core.persistence.checkpointer import get_checkpointer
from coherent.core.graph.workflow import build_coherent_graph
from coherent.core.schemas.context import ExecutionContext
from coherent.core.schemas.state import StageEnum
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


class CoherentEngine:
    def __init__(self, checkpointer: AsyncSqliteSaver):
        self.checkpointer = checkpointer
        self.graph = build_coherent_graph(checkpointer)

    async def initialize(self) -> None:
        if not self.checkpointer:
            self.checkpointer = await get_checkpointer()
            self.graph = build_coherent_graph(self.checkpointer)

    async def start_session(
        self,
        raw_prompt: str,
        referenced_files: list[str],
        project_id: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        #await self.initialize()
        ctx = ExecutionContext.create(project_id=project_id, user_prompt=raw_prompt)

        initial_state = {
            "project_id": ctx.project_id,
            "session_id": ctx.session_id,
            "current_stage": StageEnum.REFINEMENT,
            "raw_prompt": raw_prompt,
            "referenced_files": referenced_files,
            "spec_file_path": None,
            "adr_file_paths": [],
            "task_dag": [],
            "current_task_index": 0,
            "stage_approved": False,
            "user_feedback": None,
            "retry_count": 0,
            "error_logs": None,
            "messages": [],
        }

        config = {"configurable": {"thread_id": ctx.thread_id}}
        async for event in self.graph.astream(initial_state, config=config):
            yield event

    async def resume_session(
        self,
        thread_id: str,
        user_feedback: Optional[str] = None,
        approved: bool = True,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        await self.initialize()
        config = {"configurable": {"thread_id": thread_id}}

        # Update state with feedback before resuming
        await self.graph.aupdate_state(
            config,
            {"stage_approved": approved, "user_feedback": user_feedback},
        )

        async for event in self.graph.astream(None, config=config):
            yield event