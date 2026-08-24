# StateGraph compilation & interrupt setup

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from coherent.core.schemas.state import CoherentState
from coherent.core.graph.nodes import (
    gap_analyzer_node,
    spec_writer_node,
    architect_node,
    task_planner_node,
    executor_node,
    verifier_node,
)
from coherent.core.graph.routing import (
    route_gap_analysis,
    route_spec_approval,
    route_architecture,
    route_planning,
    route_verification,
)


def build_coherent_graph(checkpointer: AsyncSqliteSaver):
    builder = StateGraph(CoherentState)

    # Add Nodes
    builder.add_node("gap_analyzer", gap_analyzer_node)
    builder.add_node("spec_writer", spec_writer_node)
    builder.add_node("architecture", architect_node)
    builder.add_node("planning", task_planner_node)
    builder.add_node("execution", executor_node)
    builder.add_node("verification", verifier_node)

    # Add Edges & Conditional Human Checkpoints
    builder.add_edge(START, "gap_analyzer")
    
    # Gap Analysis Loop
    builder.add_conditional_edges(
        "gap_analyzer",
        route_gap_analysis,
        {"gap_analyzer": "gap_analyzer", "spec_writer": "spec_writer"}
    )
    
    # Spec Approval
    builder.add_conditional_edges(
        "spec_writer",
        route_spec_approval,
        {"gap_analyzer": "gap_analyzer", "architecture": "architecture"}
    )

    builder.add_conditional_edges(
        "architecture",
        route_architecture,
        {"architecture": "architecture", "planning": "planning"},
    )
    builder.add_conditional_edges(
        "planning",
        route_planning,
        {"planning": "planning", "execution": "execution"},
    )
    builder.add_edge("execution", "verification")
    builder.add_conditional_edges(
        "verification",
        route_verification,
        {"execution": "execution", "verification": "verification", "end": END},
    )

    return builder.compile(
        checkpointer=checkpointer,
        interrupt_after=["gap_analyzer", "spec_writer", "architecture", "planning", "verification"],
    )