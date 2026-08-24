from coherent.adapters.claude_code import ClaudeCodeAdapter
from coherent.adapters.aider import AiderAdapter
from coherent.config import get_settings
from coherent.core.schemas.state import CoherentState, StageEnum


async def executor_node(state: CoherentState) -> dict:
    settings = get_settings()
    current_idx = state.get("current_task_index", 0)
    task_dict = state["task_dag"][current_idx]

    if settings.default_agent_backend == "aider":
        adapter = AiderAdapter()
    else:
        adapter = ClaudeCodeAdapter()

    result = await adapter.execute_task(task_dict)

    return {
        "current_stage": StageEnum.EXECUTION,
        "stage_approved": True,  # Auto-advances to verification step
        "error_logs": result.get("stderr") if result.get("exit_code") != 0 else None,
        "messages": [{"role": "assistant", "stage": "execution", "content": f"Task {task_dict['id']} executed."}],
    }