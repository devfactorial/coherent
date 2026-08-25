import json
from pathlib import Path
from typing import List, Optional
from InquirerPy import inquirer

from coherent.cli.ui.prompts import prompt_stage_approval
from coherent.cli.ui.renderer import (
    render_arch_question,
    render_gap_question,
    render_markdown_artifact,
    render_session_completed,
    render_session_paused,
    render_session_resumed,
    render_stage_header,
    render_tech_intake_header,
    render_warning,
)
from coherent.core.engine import CoherentEngine
from coherent.core.persistence.checkpointer import get_checkpointer
from coherent.core.schemas.context import ExecutionContext
from coherent.core.schemas.state import StageEnum


async def run_cli_session(
    prompt: str,
    files: List[str],
    project_id: Optional[str] = None,
    resume_session_id: Optional[str] = None,
) -> None:
    async with get_checkpointer() as checkpointer:
        engine = CoherentEngine(checkpointer)

        # 1. Initialize context and determine configuration
        if resume_session_id:
            config = {"configurable": {"thread_id": resume_session_id}}
            snapshot = await engine.graph.aget_state(config)

            if not snapshot or not snapshot.values:
                render_warning(f"No active checkpoint state found for session: {resume_session_id}")
                return

            saved_project = snapshot.values.get("project_id", project_id or "default-project")
            ctx = ExecutionContext(project_id=saved_project, session_id=resume_session_id)
            render_session_resumed(ctx.session_id)
        else:
            ctx = ExecutionContext.create(project_id=project_id, user_prompt=prompt)
            config = {
                "configurable": {"thread_id": ctx.thread_id},
                "metadata": {"project_id": ctx.project_id},
            }

            initial_state = {
                "project_id": ctx.project_id,
                "session_id": ctx.session_id,
                "current_stage": StageEnum.REFINEMENT.value,
                "raw_prompt": prompt,
                "referenced_files": files,
                # Stage 1: Functional Discovery
                "confirmed_facts": [],
                "active_assumptions": [],
                "qna_history": [],
                "current_question": None,
                "clarification_complete": False,
                "spec_file_path": None,
                # Stage 2: Technical Discovery
                "tech_stack_context": None,
                "tech_stack_captured": False,
                "confirmed_tech_decisions": [],
                "active_tech_tradeoffs": [],
                "arch_qna_history": [],
                "arch_current_question": None,
                "arch_clarification_complete": False,
                "adr_file_paths": [],
                # Stage 3+: Planning & Execution
                "task_dag": [],
                "current_task_index": 0,
                "stage_approved": False,
                "user_feedback": None,
                "retry_count": 0,
                "error_logs": None,
                "messages": [],
            }

            # Run initial stage execution until first interrupt
            async for event in engine.graph.astream(
                initial_state, config=config, stream_mode="updates"
            ):
                if isinstance(event, dict):
                    for node_name, state_update in event.items():
                        if isinstance(state_update, dict):
                            stage = state_update.get("current_stage", node_name)
                            stage_str = stage.value if hasattr(stage, "value") else str(stage)
                            render_stage_header(stage_str, ctx.session_id, ctx.project_id)

        # 2. Main Interactive Lifecycle Loop
        while True:
            state_snapshot = await engine.graph.aget_state(config)
            current_state = state_snapshot.values if state_snapshot else None

            if not current_state:
                render_warning("No active checkpoint state found.")
                break

            current_stage = current_state.get("current_stage", StageEnum.REFINEMENT.value)
            stage_str = current_stage.value if hasattr(current_stage, "value") else str(current_stage)

            # -------------------------------------------------------------
            # Stage 1A: Functional Discovery Socratic Loop (Refinement)
            # -------------------------------------------------------------
            if stage_str == "refinement" and not current_state.get("clarification_complete", False):
                q_data = current_state.get("current_question")
                if q_data:
                    render_gap_question(
                        question=q_data.get("question", ""),
                        recommended_default=q_data.get("recommended_default", ""),
                        rationale=q_data.get("rationale", ""),
                    )

                    try:
                        user_answer = await inquirer.text(
                            message="Your answer (Press Enter to accept recommendation):",
                            default=q_data.get("recommended_default", ""),
                        ).execute_async()
                    except KeyboardInterrupt:
                        render_session_paused(ctx.session_id)
                        break

                    await engine.graph.aupdate_state(
                        config,
                        {"user_feedback": user_answer.strip(), "stage_approved": False},
                    )

                    async for event in engine.graph.astream(None, config=config, stream_mode="updates"):
                        if isinstance(event, dict):
                            for node_name, state_update in event.items():
                                if isinstance(state_update, dict):
                                    stage = state_update.get("current_stage", node_name)
                                    stage_str = stage.value if hasattr(stage, "value") else str(stage)
                                    render_stage_header(stage_str, ctx.session_id, ctx.project_id)
                    continue

            # -------------------------------------------------------------
            # Stage 2A: Tech Stack Baseline Intake (Architecture Pre-flight)
            # -------------------------------------------------------------
            if stage_str == "architecture" and not current_state.get("tech_stack_captured", False):
                render_tech_intake_header()

                try:
                    lang_runtime = await inquirer.text(
                        message="Language & Runtime:",
                        default="Python 3.12 (AsyncIO)",
                    ).execute_async()

                    frameworks = await inquirer.text(
                        message="Core Frameworks / Libraries:",
                        default="FastAPI, Pydantic v2, SQLAlchemy 2.0",
                    ).execute_async()

                    primary_db = await inquirer.text(
                        message="Primary Database / Storage:",
                        default="PostgreSQL 16",
                    ).execute_async()

                    infra_target = await inquirer.text(
                        message="Target Infrastructure / Deployment:",
                        default="Docker Container",
                    ).execute_async()

                    additional_constraints = await inquirer.text(
                        message="Special Constraints / Requirements (optional):",
                        default="None",
                    ).execute_async()

                except KeyboardInterrupt:
                    render_session_paused(ctx.session_id)
                    break

                tech_context = {
                    "language_runtime": lang_runtime.strip(),
                    "frameworks": frameworks.strip(),
                    "database": primary_db.strip(),
                    "deployment_target": infra_target.strip(),
                    "constraints": additional_constraints.strip(),
                }

                await engine.graph.aupdate_state(
                    config,
                    {
                        "tech_stack_context": tech_context,
                        "tech_stack_captured": True,
                        "user_feedback": None,
                        "stage_approved": False,
                    },
                )

                async for event in engine.graph.astream(None, config=config, stream_mode="updates"):
                    if isinstance(event, dict):
                        for node_name, state_update in event.items():
                            if isinstance(state_update, dict):
                                stage = state_update.get("current_stage", node_name)
                                stage_str = stage.value if hasattr(stage, "value") else str(stage)
                                render_stage_header(stage_str, ctx.session_id, ctx.project_id)
                continue

            # -------------------------------------------------------------
            # Stage 2B: Technical Discovery Socratic Loop (Architecture)
            # -------------------------------------------------------------
            if stage_str == "architecture" and not current_state.get("arch_clarification_complete", False):
                arch_q_data = current_state.get("arch_current_question")
                if arch_q_data:
                    render_arch_question(
                        question=arch_q_data.get("question", ""),
                        recommended_default=arch_q_data.get("recommended_default", ""),
                        rationale=arch_q_data.get("rationale", ""),
                    )

                    try:
                        user_answer = await inquirer.text(
                            message="Technical Decision (Press Enter to accept recommendation):",
                            default=arch_q_data.get("recommended_default", ""),
                        ).execute_async()
                    except KeyboardInterrupt:
                        render_session_paused(ctx.session_id)
                        break

                    await engine.graph.aupdate_state(
                        config,
                        {"user_feedback": user_answer.strip(), "stage_approved": False},
                    )

                    async for event in engine.graph.astream(None, config=config, stream_mode="updates"):
                        if isinstance(event, dict):
                            for node_name, state_update in event.items():
                                if isinstance(state_update, dict):
                                    stage = state_update.get("current_stage", node_name)
                                    stage_str = stage.value if hasattr(stage, "value") else str(stage)
                                    render_stage_header(stage_str, ctx.session_id, ctx.project_id)
                    continue

            # -------------------------------------------------------------
            # Render Generated Artifacts for Current Paused Stage
            # -------------------------------------------------------------
            if stage_str == "refinement" and current_state.get("spec_file_path"):
                spec_path = Path(current_state["spec_file_path"])
                if spec_path.exists():
                    render_markdown_artifact(
                        "Generated Requirements Spec",
                        spec_path.read_text(encoding="utf-8"),
                    )

            elif stage_str == "architecture" and current_state.get("adr_file_paths"):
                adr_paths = current_state.get("adr_file_paths", [])
                if adr_paths:
                    adr_path = Path(adr_paths[0])
                    if adr_path.exists():
                        render_markdown_artifact(
                            "Generated Architectural Decision Record",
                            adr_path.read_text(encoding="utf-8"),
                        )

            elif stage_str == "planning" and current_state.get("task_dag"):
                render_markdown_artifact(
                    "Generated Task DAG",
                    json.dumps(current_state["task_dag"], indent=2),
                )

            elif stage_str == "completed":
                render_session_completed()
                break

            # -------------------------------------------------------------
            # Human Stage Approval Gate
            # -------------------------------------------------------------
            try:
                approved, feedback = await prompt_stage_approval(stage_str)
            except KeyboardInterrupt:
                render_session_paused(ctx.session_id)
                break

            await engine.graph.aupdate_state(
                config,
                {"stage_approved": approved, "user_feedback": feedback},
            )

            async for event in engine.graph.astream(None, config=config, stream_mode="updates"):
                if isinstance(event, dict):
                    for node_name, state_update in event.items():
                        if isinstance(state_update, dict):
                            stage = state_update.get("current_stage", node_name)
                            stage_str = stage.value if hasattr(stage, "value") else str(stage)
                            render_stage_header(stage_str, ctx.session_id, ctx.project_id)