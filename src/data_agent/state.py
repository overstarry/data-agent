from typing import Any, TypedDict


class AgentState(TypedDict):
    """State managed by the LangGraph agent."""

    user_request: str
    plan: dict[str, Any]
    pg_data: list[dict[str, Any]]
    ga_data: list[dict[str, Any]]
    report_path: str | None
    error: str | None
