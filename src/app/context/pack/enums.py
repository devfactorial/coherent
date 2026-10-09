from enum import Enum


class ContextPackPurpose(str, Enum):
    """Why an agent is requesting context."""

    IMPLEMENTATION = "IMPLEMENTATION"
    VERIFICATION = "VERIFICATION"


class ContextSelectionBasis(str, Enum):
    """How a record became part of a Context Pack."""

    TARGET = "TARGET"
    DIRECT_RELATION = "DIRECT_RELATION"
    TRANSITIVE_RELATION = "TRANSITIVE_RELATION"
    SEMANTIC_RELEVANCE = "SEMANTIC_RELEVANCE"
