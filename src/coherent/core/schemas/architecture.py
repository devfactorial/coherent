from typing import List, Optional
from pydantic import BaseModel, Field


class NextTechnicalQuestion(BaseModel):
    question: str = Field(
        description="The atomic technical question regarding trade-offs, storage, concurrency, etc."
    )
    recommended_default: str = Field(
        description="A concrete, production-ready default decision."
    )
    rationale: str = Field(
        description="Technical justification grounded in the tech stack."
    )


class ArchDiscoveryResponse(BaseModel):
    arch_clarification_complete: bool = Field(
        default=False,
        description="True ONLY if all critical technical decisions and trade-offs are fully resolved.",
    )
    confirmed_tech_decisions: List[str] = Field(
        default_factory=list,
        description="List of firmly agreed architectural decisions.",
    )
    active_tech_tradeoffs: List[str] = Field(
        default_factory=list,
        description="List of architectural trade-offs currently under consideration.",
    )
    next_question: Optional[NextTechnicalQuestion] = Field(
        default=None,
        description="The next question to ask the user, or null if complete.",
    )