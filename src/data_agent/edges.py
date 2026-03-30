"""Edge routing logic for the LangGraph state machine."""

from data_agent.state import AgentState


def route_queries(state: AgentState) -> str:
    """Determine which query nodes should be executed based on plan.

    Returns:
        One of: "both", "pg_only", "ga_only", "report", "error"
    """
    if state.get("error"):
        return "error"

    plan = state.get("plan", {})
    needs_pg = plan.get("needs_pg", False)
    needs_ga = plan.get("needs_ga", False)

    if needs_pg and needs_ga:
        return "both"
    elif needs_pg:
        return "pg_only"
    elif needs_ga:
        return "ga_only"
    else:
        return "report"
