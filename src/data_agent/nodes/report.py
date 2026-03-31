"""Report generation node."""

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape

from data_agent.state import AgentState


def get_output_dir() -> Path:
    """Get report output directory."""
    path = Path(os.environ.get("REPORT_OUTPUT_DIR", "./reports"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def generate_report(state: AgentState) -> dict[str, Any]:
    """Generate HTML report from query results.

    Returns:
        dict with "report_path" key.
    """
    plan = state.get("plan", {})
    pg_data = state.get("pg_data", [])
    ga_data = state.get("ga_data", [])

    title = plan.get("report_title", "Data Report")

    # Setup Jinja2 environment
    env = Environment(
        loader=PackageLoader("data_agent", "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("report.html")

    # Render HTML
    html_content = template.render(
        title=title,
        pg_data=pg_data,
        ga_data=ga_data,
        generated_at=datetime.now().isoformat(),
        has_pg=plan.get("needs_pg", False) or len(pg_data) > 0,
        has_ga=plan.get("needs_ga", False) or len(ga_data) > 0,
    )

    # Write to file
    output_dir = get_output_dir()
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    file_path = output_dir / filename

    file_path.write_text(html_content, encoding="utf-8")

    return {"report_path": str(file_path)}
