"""Tests for PostgreSQL query node."""

from unittest.mock import MagicMock, patch

import pytest

from data_agent.nodes.query_pg import query_pg
from data_agent.state import AgentState


def test_query_pg_no_query():
    state: AgentState = {
        "user_request": "test",
        "plan": {"needs_pg": True, "pg_query": ""},
        "pg_data": [],
        "ga_data": [],
        "report_path": None,
        "error": None,
    }
    result = query_pg(state)
    assert result["pg_data"] == []
    assert "No PostgreSQL query" in result["error"]


def test_query_pg_unsafe_query():
    state: AgentState = {
        "user_request": "test",
        "plan": {"needs_pg": True, "pg_query": "DROP TABLE users"},
        "pg_data": [],
        "ga_data": [],
        "report_path": None,
        "error": None,
    }
    result = query_pg(state)
    assert result["pg_data"] == []
    assert "Only SELECT queries" in result["error"]


@patch("data_agent.nodes.query_pg.psycopg.connect")
def test_query_pg_success(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchmany.return_value = [{"id": 1, "name": "test"}]
    mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    state: AgentState = {
        "user_request": "test",
        "plan": {"needs_pg": True, "pg_query": "SELECT * FROM users"},
        "pg_data": [],
        "ga_data": [],
        "report_path": None,
        "error": None,
    }
    result = query_pg(state)
    assert result["pg_data"] == [{"id": 1, "name": "test"}]
    assert result.get("error") is None
