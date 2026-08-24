# CLI interactive loop & feedback dispatcher

from pathlib import Path
from typing import List, Optional
from coherent.core.engine import CoherentEngine
from coherent.cli.ui.renderer import (
    render_gap_question,
    render_markdown_artifact,
    render_session_completed,
    render_session_paused,
    render_session_resumed,
    render_stage_header,
    render_warning
)
from coherent.cli.ui.prompts import prompt_stage_approval
from coherent.core.schemas.context import ExecutionContext
from coherent.core.schemas.state import StageEnum
from coherent.core.persistence.checkpointer import get_checkpointer
from InquirerPy import inquirer
import json

async def run_cli_session(prompt: str, files: List[str], project_id: Optional[str] = None,
                          resume_session_id: Optional[str] = None,) -> None:
    async with get_checkpointer() as checkpointer:
        engine = CoherentEngine(checkpointer)
        #await engine.initialize()
        if resume_session_id:
           
            config = {"configurable": {"thread_id": resume_session_id}}
            # Fetch existing state snapshot to retrieve project_id
            snapshot = await engine.graph.aget_state(config)
            if not snapshot.values:
                render_warning(f"No active checkpoint found for session: {resume_session_id}")
                return

            saved_project = snapshot.values.get("project_id", "default-project")
            ctx = ExecutionContext(project_id=saved_project, session_id=resume_session_id)
            render_session_resumed(ctx.session_id)
        else:
            # Create session context
            ctx = ExecutionContext.create(project_id=project_id, user_prompt=prompt)
            config = {"configurable": {"thread_id": ctx.thread_id}}
            
            initial_state = {
                "project_id": ctx.project_id,
                "session_id": ctx.session_id,
                "current_stage": StageEnum.REFINEMENT,
                "raw_prompt": prompt,
                "referenced_files": files,
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
            
            # 1. Run initial stage until first interrupt
            async for event in engine.graph.astream(initial_state, config=config, stream_mode="updates"):
                if isinstance(event, dict):
                    for node_name, state_update in event.items():
                        if isinstance(state_update, dict):
                            stage = state_update.get("current_stage", node_name)
                            if hasattr(stage, "value"):
                                stage = stage.value
                            render_stage_header(stage, ctx.session_id)

        # 2. Interactive approval loop across stages
        while True:
            # Get the latest state snapshot from checkpointer
            state_snapshot = await engine.graph.aget_state(config)
            current_state = state_snapshot.values

            if not current_state:
                render_warning("No active checkpoint state found.")
                break

            current_stage = current_state.get("current_stage", StageEnum.REFINEMENT)
            stage_str = current_stage.value if hasattr(current_stage, "value") else str(current_stage)
            
            # -----------------------------------------------------------------
            # Stage 1A: Socratic Gap Discovery Question Loop
            # -----------------------------------------------------------------
            if stage_str == "refinement" and not current_state.get("clarification_complete"):
                q_data = current_state.get("current_question")

                if q_data:
                    render_gap_question(
                        question=q_data.get("question", ""),
                        recommended_default=q_data.get("recommended_default", ""),
                        rationale=q_data.get("rationale", "Clarifying architectural constraints"),
                    )

                    try:
                        user_answer = await inquirer.text(
                            message="Your answer (Press Enter to accept recommended default):",
                            default=q_data.get("recommended_default", ""),
                        ).execute_async()
                    except KeyboardInterrupt:
                        render_session_paused(ctx.session_id)
                        break

                    # Inject answer into user_feedback and trigger next gap analysis iteration
                    await engine.graph.aupdate_state(
                        config,
                        {"user_feedback": user_answer.strip(), "stage_approved": False},
                    )

                    async for event in engine.graph.astream(
                        None, config=config, stream_mode="updates"
                    ):
                        if isinstance(event, dict):
                            for node_name, state_update in event.items():
                                if isinstance(state_update, dict):
                                    stage = state_update.get("current_stage", node_name)
                                    stage_str = stage.value if hasattr(stage, "value") else str(stage)
                                    render_stage_header(stage_str, ctx.session_id)
                    continue

            # Show artifacts for the stage that just paused
            if stage_str == "refinement" and current_state.get("spec_file_path"):
                spec_path = Path(current_state["spec_file_path"])
                if spec_path.exists():
                    render_markdown_artifact("Generated Requirements Spec", spec_path.read_text(encoding="utf-8"))

            elif stage_str == "architecture" and current_state.get("adr_file_paths"):
                adr_path = Path(current_state["adr_file_paths"][0])
                if adr_path.exists():
                    render_markdown_artifact("Generated Architectural Decision Record", adr_path.read_text(encoding="utf-8"))

            elif stage_str == "planning" and current_state.get("task_dag"):
                render_markdown_artifact("Generated Task DAG", json.dumps(current_state["task_dag"], indent=2))

            elif stage_str == "completed":
                render_session_completed
                break

            # Prompt for human-in-the-loop approval or feedback
            try:
                approved, feedback = await prompt_stage_approval(stage_str)
            except KeyboardInterrupt:
                render_session_paused(ctx.session_id)
                break

            # Update state with approval or feedback
            await engine.graph.aupdate_state(
                config,
                {"stage_approved": approved, "user_feedback": feedback},
            )

            # Resume graph execution
            async for event in engine.graph.astream(None, config=config, stream_mode="updates"):
                if isinstance(event, dict):
                    for node_name, state_update in event.items():
                        if isinstance(state_update, dict):
                            stage = state_update.get("current_stage", node_name)
                            if hasattr(stage, "value"):
                                stage = stage.value
                            render_stage_header(stage, ctx.session_id)

    