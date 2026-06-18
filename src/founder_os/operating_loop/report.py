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
    health = snapshot.health
    indicators = (
        ("No active goals", health.no_active_goals),
        ("No active projects", health.no_active_projects),
        ("No active priorities", health.no_active_priorities),
        ("No recent reviews", health.no_recent_reviews),
    )
    lines.append("  Health:")
    for label, raised in indicators:
        marker = "!" if raised else "-"
        lines.append(f"    [{marker}] {label}: {'yes' if raised else 'no'}")
    return "\n".join(lines)
