from __future__ import annotations

from app.models.graph.records import (
    AcceptanceCriterion,
    ArtifactRevision,
    Assessment,
    AssessmentRun,
    Constraint,
    Decision,
    DesignElement,
    Evidence,
    InterfaceContract,
    Provenance,
    Requirement,
    TestCase,
)

RECORD_TYPES: dict[str, type] = {
    "ARTIFACTREVISION": ArtifactRevision,
    "ACCEPTANCECRITERION": AcceptanceCriterion,
    "REQUIREMENT": Requirement,
    "CONSTRAINT": Constraint,
    "ASSESSMENT": Assessment,
    "DECISION": Decision,
    "DESIGNELEMENT": DesignElement,
    "INTERFACECONTRACT": InterfaceContract,
    "TESTCASE": TestCase,
    "ASSESSMENTRUN": AssessmentRun,
    "EVIDENCE": Evidence,
    "PROVENANCE": Provenance,
}