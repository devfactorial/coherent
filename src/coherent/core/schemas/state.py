# CoherentState TypedDict & StageEnum

import operator
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

class ClarificationQnA(BaseModel):
    question: str
    recommended_default: str
    rationale: str
    user_answer: Optional[str] = None

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
    
    # Gap Analysis & Socratic Discovery
    confirmed_facts: List[str]
    active_assumptions: List[str]
    qna_history: List[Dict[str, Any]]
    current_question: Optional[Dict[str, Any]]  # Active question posed to the user
    clarification_complete: bool                 # True when no more critical gaps remain

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