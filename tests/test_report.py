"""Tests for report generation node."""

import os
import tempfile
from pathlib import Path

import pytest

from data_agent.nodes.report import generate_report
from data_agent.state import AgentState


def test_generate_report_success(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("REPORT_OUTPUT_DIR", tmpdir)

        state: AgentState = {
            "user_request": "test",
            "plan": {"report_title": "Test Report"},
            "pg_data": [{"id": 1, "value": 100}],
            "ga_data": [{"date": "2024-01-01", "sessions": 50}],
            "report_path": None,
            "error": None,
        }

        result = generate_report(state)

        assert result["report_path"] is not None
        report_path = Path(result["report_path"])
        assert report_path.exists()
        content = report_path.read_text()
        assert "Test Report" in content
        assert "id" in content
        assert "date" in content


def test_generate_report_shows_empty_requested_sections(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("REPORT_OUTPUT_DIR", tmpdir)

        state: AgentState = {
            "user_request": "test",
            "plan": {
                "report_title": "Empty Results",
                "needs_pg": True,
                "needs_ga": True,
            },
            "pg_data": [],
            "ga_data": [],
            "report_path": None,
            "error": None,
        }

        result = generate_report(state)

        report_path = Path(result["report_path"])
        content = report_path.read_text()
        assert "PostgreSQL Data" in content
        assert "No data returned from PostgreSQL." in content
        assert "Google Analytics Data" in content
        assert "No data returned from Google Analytics." in content
