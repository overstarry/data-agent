"""LangGraph StateGraph definition for the Data Agent."""

import os
from contextlib import AbstractContextManager

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph

from data_agent.edges import route_queries
from data_agent.nodes import generate_report, planner, query_ga, query_pg
from data_agent.state import AgentState


def create_graph(
    checkpointer: PostgresSaver | None = None,
) -> StateGraph:
    """Create and compile the Data Agent StateGraph.

    Args:
        checkpointer: Optional PostgresSaver for persistence.
            If not provided, uses in-memory checkpointer.

    Returns:
        Compiled StateGraph.
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planner", planner)
    workflow.add_node("query_pg", query_pg)
    workflow.add_node("query_ga", query_ga)
    workflow.add_node("generate_report", generate_report)

    # Define edges
    workflow.add_edge(START, "planner")

    # Conditional routing from planner
    workflow.add_conditional_edges(
        "planner",
        route_queries,
        {
            "both": "query_pg",
            "pg_only": "query_pg",
            "ga_only": "query_ga",
            "report": "generate_report",
            "error": END,
        },
    )

    # After PG query, check if we need GA
    workflow.add_conditional_edges(
        "query_pg",
        lambda s: "query_ga" if s.get("plan", {}).get("needs_ga") and not s.get("error") else "report" if not s.get("error") else END,
        {
            "query_ga": "query_ga",
            "report": "generate_report",
            END: END,
        },
    )

    # After GA query, go to report
    workflow.add_edge("query_ga", "generate_report")

    # Report generation ends
    workflow.add_edge("generate_report", END)

    # Compile with checkpointer
    if checkpointer is None:
        return workflow.compile()
    return workflow.compile(checkpointer=checkpointer)


def get_postgres_saver() -> AbstractContextManager[PostgresSaver]:
    """Create a PostgresSaver context manager from environment."""
    postgres_url = os.environ.get("STATE_POSTGRES_URL", "postgresql://localhost:5432/data_agent")
    return PostgresSaver.from_conn_string(postgres_url)
