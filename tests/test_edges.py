"""Tests for edge routing logic."""

import pytest

from data_agent.edges import route_queries
from data_agent.state import AgentState


def test_route_queries_both():
    state: AgentState = {
        "user_request": "test",
        "plan": {"needs_pg": True, "needs_ga": True},
        "pg_data": [],
        "ga_data": [],
        "report_path": None,
        "error": None,
    }
    assert route_queries(state) == "both"


def test_route_queries_pg_only():
    state: AgentState = {
        "user_request": "test",
        "plan": {"needs_pg": True, "needs_ga": False},
        "pg_data": [],
        "ga_data": [],
        "report_path": None,
        "error": None,
    }
    assert route_queries(state) == "pg_only"


def test_route_queries_ga_only():
    state: AgentState = {
        "user_request": "test",
        "plan": {"needs_pg": False, "needs_ga": True},
        "pg_data": [],
        "ga_data": [],
        "report_path": None,
        "error": None,
    }
    assert route_queries(state) == "ga_only"


def test_route_queries_report():
    state: AgentState = {
        "user_request": "test",
        "plan": {},
        "pg_data": [],
        "ga_data": [],
        "report_path": None,
        "error": None,
    }
    assert route_queries(state) == "report"


def test_route_queries_error():
    state: AgentState = {
        "user_request": "test",
        "plan": {},
        "pg_data": [],
        "ga_data": [],
        "report_path": None,
        "error": "Something went wrong",
    }
    assert route_queries(state) == "error"
