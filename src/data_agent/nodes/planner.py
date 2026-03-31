"""Planner node: uses LLM to parse user request and generate query plan."""

import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from data_agent.state import AgentState

PLANNER_SYSTEM_PROMPT = """You are a data analysis planner. Analyze the user's request and create a plan to fetch data from PostgreSQL and/or Google Analytics 4.

Respond with a JSON object following this schema:
{
    "needs_pg": boolean,           // Whether PostgreSQL query is needed
    "needs_ga": boolean,           // Whether GA4 query is needed
    "pg_query": string,            // SQL query for PostgreSQL (if needs_pg)
    "ga_metrics": [string],        // GA4 metrics (e.g., ["activeUsers", "sessions"])
    "ga_dimensions": [string],     // GA4 dimensions (e.g., ["date", "deviceCategory"])
    "date_range": {                // Date range for GA4 (if needs_ga)
        "start_date": "string",    // ISO date or relative like "7daysAgo"
        "end_date": "string"       // ISO date or relative like "yesterday"
    },
    "report_title": string         // Title for the generated report
}

Guidelines:
- Use safe read-only queries for PostgreSQL (SELECT only, no DDL/DML)
- For date ranges, prefer relative dates like "7daysAgo", "30daysAgo", "yesterday"
- Allowed GA4 metrics: activeUsers, newUsers, sessions, bounceRate, sessionConversionRate, screenPageViews, engagedSessions, averageSessionDuration, eventCount, totalUsers
- Allowed GA4 dimensions: date, deviceCategory, country, city, pageTitle, pagePath, sessionDefaultChannelGrouping, operatingSystem, browser, language
- ONLY use the metrics and dimensions listed above
"""


def planner(state: AgentState) -> dict[str, Any]:
    """Generate query plan from user request using LLM."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=f"User request: {state['user_request']}"),
    ]

    # Request JSON output
    response = llm.invoke(messages, response_format={"type": "json_object"})

    plan = json.loads(response.content)
    return {"plan": plan}
