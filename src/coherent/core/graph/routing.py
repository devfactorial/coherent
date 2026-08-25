# Conditional edge routers

from coherent.core.schemas.state import CoherentState, StageEnum

def route_gap_analysis(state: CoherentState) -> str:
    # If the LLM has resolved all gaps, move to writing the specification
    if state.get("clarification_complete", False):
        return "spec_writer"
    # Otherwise pause / re-loop for user answer
    return "gap_analyzer"

def route_spec_approval(state: CoherentState) -> str:
    if state.get("stage_approved", False):
        return "arch_analyzer"
    # If user rejects the final spec, send back to gap analyzer with feedback
    return "gap_analyzer"



def route_arch_gap_analysis(state: CoherentState) -> str:
    complete = state.get("arch_clarification_complete", False)
    has_q = state.get("arch_current_question") is not None
    
    # --- DEBUG PRINT ---
    print(f"[DEBUG route_arch_gap_analysis] complete={complete}, has_question={has_q}")
    # -------------------
    
    if complete and not has_q:
        return "adr_writer"
    return "arch_analyzer"


def route_adr_approval(state: CoherentState) -> str:
    if state.get("stage_approved", False):
        return "planning"
    return "arch_analyzer"


def route_planning(state: CoherentState) -> str:
    if state.get("stage_approved"):
        return "execution"
    return "planning"


def route_verification(state: CoherentState) -> str:
    if state.get("error_logs"):
        if state.get("retry_count", 0) <= 3:
            return "execution"  # Self-healing loop
        return "verification"   # Trigger human intervention checkpoint
    
    if state.get("current_task_index", 0) < len(state["task_dag"]):
        return "execution"
    return "end"