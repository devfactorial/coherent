from __future__ import annotations

from app.models.graph.records import (
    AcceptanceCriterion,
    ArtifactRevision,
    Constraint,
    Decision,
    DesignElement,
    Record,
    Requirement,
)


class DefaultRecordPolicy:
    """
    Defines default governance requirements for record types.

    This policy answers:

        - Does the record require a document?
        - Does the record require provenance?
        - Does the record require graph representation?

    It deliberately does NOT determine which physical document
    contains an individual record.

    Document placement is governed by DocumentMembership.

    Example:

        Requirement
            -> document_required = True

        FR-001
            -> DocumentMembership
            -> FRD-ORDERS

        FR-002
            -> DocumentMembership
            -> FRD-CUSTOMERS
    """

    def document_required(
        self,
        record: Record,
    ) -> bool:
        """
        Return whether the record requires a document representation.
        """

        return isinstance(
            record,
            (
                Requirement,
                Constraint,
                AcceptanceCriterion,
                Decision,
                DesignElement,
                ArtifactRevision,
            ),
        )

    def provenance_required(
        self,
        record: Record,
    ) -> bool:
        """
        All governed records require provenance by default.
        """

        return True

    def graph_required(
        self,
        record: Record,
    ) -> bool:
        """
        All governed records participate in the graph by default.
        """

        return True