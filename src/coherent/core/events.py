# Event types & streaming definitions
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel


class EventType(str, Enum):
    STAGE_START = "stage_start"
    STAGE_STREAM_TOKEN = "stage_stream_token"
    STAGE_COMPLETED = "stage_completed"
    INTERRUPT_APPROVAL = "interrupt_approval"
    EXECUTION_LOG = "execution_log"
    ERROR = "error"


class CoherentEvent(BaseModel):
    event_type: EventType
    stage: str
    payload: Dict[str, Any]
    message: Optional[str] = None