# CoherentState TypedDict & StageEnum

import operator
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

class ClarificationQnA(BaseModel):
    question: str
    recommended_default: str
    rationale: str
    user_answer: Optional[str] = None
    
StageType = Literal[
    "refinement",
    "architecture",
    "planning",
    "execution",
    "verification",
    "completed",
]

class StageEnum(str, Enum):
    REFINEMENT = "refinement"
    ARCHITECTURE = "architecture"
    PLANNING = "planning"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    COMPLETED = "completed"


class CoherentState(TypedDict):
    # Context
    project_id: str
    session_id: str
    current_stage: StageEnum

    # Inputs & File References
    raw_prompt: str
    referenced_files: List[str]
    
    # Stage 1: Functional Discovery (Refinement)
    confirmed_facts: List[str]
    active_assumptions: List[str]
    qna_history: List[Dict[str, Any]]
    current_question: Optional[Dict[str, Any]]  # Active question posed to the user
    clarification_complete: bool                 # True when no more critical gaps remain
    
    # Stage 2: Technical Discovery (Architecture)
    tech_stack_context: Optional[Dict[str, str]]  # Captured baseline tech stack
    tech_stack_captured: bool                    # Gate flag for tech intake
    confirmed_tech_decisions: List[str]
    active_tech_tradeoffs: List[str]
    arch_qna_history: List[Dict[str, Any]]
    arch_current_question: Optional[Dict[str, Any]]
    arch_clarification_complete: bool
    

    # Artifact Paths on Disk
    spec_file_path: Optional[str]
    adr_file_paths: List[str]

    # Task DAG & Progress
    task_dag: List[Dict[str, Any]]
    current_task_index: int

    # Governance & Approval Gate
    stage_approved: bool
    user_feedback: Optional[str]
    retry_count: int
    error_logs: Optional[str]

    # Conversational History
    messages: Annotated[List[Dict[str, Any]], operator.add]