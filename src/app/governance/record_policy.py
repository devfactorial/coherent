from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.models.graph.records import Record


RecordRenderer = Callable[[Record], str]
RecordAnchorResolver = Callable[[Record], str]


@dataclass(frozen=True, kw_only=True)
class RecordPolicy:
    """
    Declarative governance policy for a graph record type.

    A RecordPolicy defines how a record participates in the governed
    workflow. It does not determine where the record is stored or
    which logical document contains it.

    Responsibilities:
        - Identify the record type governed by the policy.
        - Define whether document representation is required.
        - Define whether provenance is required.
        - Define whether graph representation is required.
        - Define how the record is rendered into Markdown.
        - Define how the Markdown section is identified.

    Document placement is intentionally not part of this policy.

    Placement is represented separately through DocumentMembership.
    """

    record_type: type[Record]

    document_required: bool = True
    provenance_required: bool = True
    graph_required: bool = True

    renderer: RecordRenderer | None = None
    anchor_resolver: RecordAnchorResolver | None = None

    def matches(self, record: Record) -> bool:
        """
        Return True when this policy applies to the supplied record.
        """
        return isinstance(record, self.record_type)

    def require_document_configuration(self) -> None:
        """
        Validate document-related policy configuration.

        A policy requiring document representation must define both
        a renderer and an anchor resolver.

        The logical document itself is deliberately not configured
        here. Document placement is governed separately through
        DocumentMembership.
        """
        if not self.document_required:
            return

        if self.renderer is None:
            raise ValueError(
                f"Renderer is required for "
                f"{self.record_type.__name__}"
            )

        if self.anchor_resolver is None:
            raise ValueError(
                f"Anchor resolver is required for "
                f"{self.record_type.__name__}"
            )

    def render(self, record: Record) -> str:
        """
        Render the record into its Markdown representation.
        """
        self._validate_record(record)

        if not self.document_required:
            raise ValueError(
                f"Document representation is not required for "
                f"{self.record_type.__name__}"
            )

        if self.renderer is None:
            raise ValueError(
                f"No renderer configured for "
                f"{self.record_type.__name__}"
            )

        return self.renderer(record)

    def anchor(self, record: Record) -> str:
        """
        Resolve the Markdown heading used to locate the record.
        """
        self._validate_record(record)

        if not self.document_required:
            raise ValueError(
                f"Document representation is not required for "
                f"{self.record_type.__name__}"
            )

        if self.anchor_resolver is None:
            raise ValueError(
                f"No anchor resolver configured for "
                f"{self.record_type.__name__}"
            )

        return self.anchor_resolver(record)

    def _validate_record(self, record: Record) -> None:
        if not self.matches(record):
            raise ValueError(
                "Record does not match policy. "
                f"Expected {self.record_type.__name__}, "
                f"got {type(record).__name__}"
            )


class RecordPolicyRegistry:
    """
    Registry containing the governance policy for each record type.

    GovernedRecordService uses this registry to resolve the policy
    applicable to a domain record.

    The registry defines governance behavior, not document placement.
    """

    def __init__(
        self,
        policies: list[RecordPolicy],
    ) -> None:
        if not policies:
            raise ValueError(
                "At least one RecordPolicy is required"
            )

        self._policies = tuple(policies)

        self._validate_policies()

    def get(
        self,
        record: Record,
    ) -> RecordPolicy:
        """
        Resolve the policy applicable to a record.
        """
        for policy in self._policies:
            if policy.matches(record):
                return policy

        raise ValueError(
            "No RecordPolicy registered for record type: "
            f"{type(record).__name__}"
        )

    def get_for_type(
        self,
        record_type: type[Record],
    ) -> RecordPolicy:
        """
        Resolve a policy by exact record type.
        """
        for policy in self._policies:
            if policy.record_type is record_type:
                return policy

        raise ValueError(
            "No RecordPolicy registered for record type: "
            f"{record_type.__name__}"
        )

    def all(self) -> tuple[RecordPolicy, ...]:
        """
        Return all registered policies.
        """
        return self._policies

    def _validate_policies(self) -> None:
        """
        Validate registry configuration.

        There must be exactly one policy for each registered record type.
        """
        seen: set[type[Record]] = set()

        for policy in self._policies:
            if policy.record_type in seen:
                raise ValueError(
                    "Duplicate RecordPolicy registered for "
                    f"{policy.record_type.__name__}"
                )

            seen.add(policy.record_type)

            policy.require_document_configuration()