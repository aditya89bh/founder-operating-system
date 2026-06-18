"""Human-readable rendering of a :class:`FounderSnapshot`."""

from __future__ import annotations

from founder_os.operating_loop.models import FounderSnapshot


def render_status_report(snapshot: FounderSnapshot) -> str:
    """Render a founder snapshot as a plain-text status report."""
    review = (
        snapshot.latest_review_date.isoformat()
        if snapshot.latest_review_date is not None
        else "never"
    )
    lines = [
        "Founder Operating System status",
        f"  Active goals:      {snapshot.active_goal_count}",
        f"  Active projects:   {snapshot.active_project_count}",
        f"  Active priorities: {snapshot.active_priority_count}",
        f"  Recent decisions:  {snapshot.recent_decision_count}",
        f"  Recent memories:   {snapshot.recent_memory_count}",
        f"  Latest review:     {review}",
    ]
    return "\n".join(lines)
