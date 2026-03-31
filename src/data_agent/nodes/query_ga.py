"""Google Analytics 4 query node."""

import os
from typing import Any

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

from data_agent.state import AgentState

ALLOWED_GA_METRICS = {
    "activeUsers",
    "newUsers",
    "sessions",
    "bounceRate",
    "sessionConversionRate",
    "screenPageViews",
    "engagedSessions",
    "averageSessionDuration",
    "eventCount",
    "totalUsers",
}

ALLOWED_GA_DIMENSIONS = {
    "date",
    "deviceCategory",
    "country",
    "city",
    "pageTitle",
    "pagePath",
    "sessionDefaultChannelGrouping",
    "operatingSystem",
    "browser",
    "language",
}


def get_property_id() -> str:
    """Get GA4 Property ID from environment."""
    return os.environ.get("GA_PROPERTY_ID", "")


def query_ga(state: AgentState) -> dict[str, Any]:
    """Execute GA4 query based on plan.

    Returns:
        dict with "ga_data" key containing list of records.
    """
    plan = state.get("plan", {})
    property_id = get_property_id()

    if not property_id:
        return {"ga_data": [], "error": "GA_PROPERTY_ID not configured"}

    metrics = plan.get("ga_metrics", [])
    dimensions = plan.get("ga_dimensions", [])
    date_range = plan.get("date_range", {"start_date": "7daysAgo", "end_date": "yesterday"})

    if not metrics:
        return {"ga_data": [], "error": "No GA4 metrics specified in plan"}

    invalid_metrics = [m for m in metrics if m not in ALLOWED_GA_METRICS]
    if invalid_metrics:
        return {"ga_data": [], "error": f"Disallowed GA4 metrics: {invalid_metrics}"}

    invalid_dims = [d for d in dimensions if d not in ALLOWED_GA_DIMENSIONS]
    if invalid_dims:
        return {"ga_data": [], "error": f"Disallowed GA4 dimensions: {invalid_dims}"}

    try:
        client = BetaAnalyticsDataClient()

        request = RunReportRequest(
            property=f"properties/{property_id}",
            metrics=[Metric(name=m) for m in metrics],
            dimensions=[Dimension(name=d) for d in dimensions],
            date_ranges=[
                DateRange(
                    start_date=date_range.get("start_date", "7daysAgo"),
                    end_date=date_range.get("end_date", "yesterday"),
                )
            ],
        )

        response = client.run_report(request)

        # Convert to list of dicts
        results = []
        for row in response.rows:
            record = {}
            for i, dim in enumerate(response.dimension_headers):
                record[dim.name] = row.dimension_values[i].value
            for i, met in enumerate(response.metric_headers):
                record[met.name] = row.metric_values[i].value
            results.append(record)

        return {"ga_data": results}

    except Exception as e:
        return {"ga_data": [], "error": f"GA4 query failed: {e}"}
