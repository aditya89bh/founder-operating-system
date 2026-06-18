"""JSON exporter for founder reports.

Renders a :class:`FounderReport` as JSON. The sections and values mirror the
Markdown exporter exactly so both formats carry identical information.
"""

from __future__ import annotations

import json
from datetime import date

from founder_os.reporting.models import FounderReport


def _iso_or_none(value: date | None) -> str | None:
    return value.isoformat() if value is not None else None


def render_json(report: FounderReport) -> str:
    """Render ``report`` as a JSON document."""
    snapshot = report.snapshot
    insights = report.insights
    health = snapshot.health
    payload = {
        "current_state": {
            "active_goals": snapshot.active_goal_count,
            "active_projects": snapshot.active_project_count,
            "active_priorities": snapshot.active_priority_count,
            "recent_decisions": snapshot.recent_decision_count,
            "recent_memories": snapshot.recent_memory_count,
            "latest_review_date": _iso_or_none(snapshot.latest_review_date),
        },
        "health_indicators": {
            "no_active_goals": health.no_active_goals,
            "no_active_projects": health.no_active_projects,
            "no_active_priorities": health.no_active_priorities,
            "no_recent_reviews": health.no_recent_reviews,
        },
        "historical_growth": {
            "goals": insights.goal_growth,
            "projects": insights.project_growth,
            "priorities": insights.priority_growth,
            "decisions": insights.decision_growth,
            "memories": insights.memory_growth,
        },
        "review_history": {
            "reviews_recorded": insights.review_count,
            "oldest_review_date": _iso_or_none(insights.oldest_review_date),
            "newest_review_date": _iso_or_none(insights.newest_review_date),
        },
    }
    return json.dumps(payload, indent=2)
