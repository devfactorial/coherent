from __future__ import annotations

from app.models.graph.node import GraphNode
from app.models.graph.records import Record


def graph_node_from_record(
    record: Record,
) -> GraphNode:
    meta = record.meta

    return GraphNode(
        revision_id=meta.revision_id,
        entity_id=meta.entity_id,
        record_type=type(record).__name__,
        version=meta.version,
        status=meta.status,
        owner_id=meta.owner_id,
        assertion_kind=meta.assertion_kind,
    )