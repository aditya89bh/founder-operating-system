"""Human-readable rendering of :class:`HistoricalInsights`."""

from __future__ import annotations

from founder_os.insights.models import HistoricalInsights


def render_insights_report(insights: HistoricalInsights) -> str:
    """Render historical insights as a plain-text report."""
    if insights.oldest_review_date is not None and insights.newest_review_date is not None:
        review_range = (
            f"{insights.oldest_review_date.isoformat()} "
            f"-> {insights.newest_review_date.isoformat()}"
        )
    else:
        review_range = "no reviews recorded"
    lines = [
        "Historical insights",
        f"  Reviews recorded: {insights.review_count}",
        f"  Review range:     {review_range}",
        "  Growth since earliest review:",
        f"    Goals:      {insights.goal_growth:+d}",
        f"    Projects:   {insights.project_growth:+d}",
        f"    Priorities: {insights.priority_growth:+d}",
        f"    Decisions:  {insights.decision_growth:+d}",
        f"    Memories:   {insights.memory_growth:+d}",
    ]
    return "\n".join(lines)
