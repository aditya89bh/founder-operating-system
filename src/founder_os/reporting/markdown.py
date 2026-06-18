"""Markdown exporter for founder reports.

Renders a :class:`FounderReport` as Markdown. The sections and values mirror the
JSON exporter exactly so both formats carry identical information.
"""

from __future__ import annotations

from founder_os.operating_loop.models import FounderSnapshot
from founder_os.reporting.models import FounderReport, ReportSection


def _current_state_lines(snapshot: FounderSnapshot) -> list[str]:
    review = (
        snapshot.latest_review_date.isoformat()
        if snapshot.latest_review_date is not None
        else "never"
    )
    return [
        f"## {ReportSection.CURRENT_STATE}",
        f"- Active goals: {snapshot.active_goal_count}",
        f"- Active projects: {snapshot.active_project_count}",
        f"- Active priorities: {snapshot.active_priority_count}",
        f"- Recent decisions: {snapshot.recent_decision_count}",
        f"- Recent memories: {snapshot.recent_memory_count}",
        f"- Latest review: {review}",
    ]


def _health_indicator_lines(snapshot: FounderSnapshot) -> list[str]:
    health = snapshot.health
    return [
        f"## {ReportSection.HEALTH_INDICATORS}",
        f"- No active goals: {str(health.no_active_goals).lower()}",
        f"- No active projects: {str(health.no_active_projects).lower()}",
        f"- No active priorities: {str(health.no_active_priorities).lower()}",
        f"- No recent reviews: {str(health.no_recent_reviews).lower()}",
    ]


def render_markdown(report: FounderReport) -> str:
    """Render ``report`` as a Markdown document."""
    lines = ["# Founder Report"]
    lines.append("")
    lines.extend(_current_state_lines(report.snapshot))
    lines.append("")
    lines.extend(_health_indicator_lines(report.snapshot))
    return "\n".join(lines)
