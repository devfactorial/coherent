from coherent.adapters.test_runner import TestRunner
from coherent.config import get_settings
from coherent.core.schemas.state import CoherentState, StageEnum


async def verifier_node(state: CoherentState) -> dict:
    settings = get_settings()
    current_idx = state.get("current_task_index", 0)
    task_dict = state["task_dag"][current_idx]

    runner = TestRunner()
    test_result = await runner.run_command(task_dict["verification_command"])

    if test_result["exit_code"] == 0:
        next_idx = current_idx + 1
        is_finished = next_idx >= len(state["task_dag"])
        return {
            "current_stage": StageEnum.COMPLETED if is_finished else StageEnum.PLANNING,
            "current_task_index": next_idx,
            "retry_count": 0,
            "error_logs": None,
            "stage_approved": False,
            "messages": [{"role": "system", "stage": "verification", "content": "Verification passed."}],
        }
    else:
        retries = state.get("retry_count", 0) + 1
        return {
            "current_stage": StageEnum.VERIFICATION,
            "retry_count": retries,
            "error_logs": test_result["output"],
            "stage_approved": False,
            "messages": [{"role": "system", "stage": "verification", "content": f"Verification failed. Log: {test_result['output']}"}],
        }