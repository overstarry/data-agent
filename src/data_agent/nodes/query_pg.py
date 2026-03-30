"""PostgreSQL query node."""

import os
from typing import Any

import psycopg
from psycopg.rows import dict_row

from data_agent.state import AgentState

MAX_ROWS = 2000


def get_data_postgres_url() -> str:
    """Get PostgreSQL URL for data queries from environment."""
    return os.environ.get("DATA_POSTGRES_URL", "postgresql://localhost:5432/data_agent")


def query_pg(state: AgentState) -> dict[str, Any]:
    """Execute PostgreSQL query based on plan.

    Returns:
        dict with "pg_data" key containing list of records.
    """
    plan = state.get("plan", {})
    query = plan.get("pg_query", "")

    if not query:
        return {"pg_data": [], "error": "No PostgreSQL query specified in plan"}

    pg_url = get_data_postgres_url()

    try:
        with psycopg.connect(pg_url, row_factory=dict_row, autocommit=False) as conn:
            conn.read_only = True
            with conn.cursor() as cur:
                cur.execute(query)
                results = cur.fetchmany(MAX_ROWS)
                return {"pg_data": list(results)}
    except Exception as e:
        return {"pg_data": [], "error": f"PostgreSQL query failed: {e}"}
