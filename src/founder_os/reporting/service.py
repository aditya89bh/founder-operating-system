"""The founder report service.

This module assembles a single, deterministic founder report by combining the
live operating-loop snapshot with the historical insights derived from stored
review snapshots. It only reads and composes existing results; it performs no
scoring, recommendation, forecasting, or AI reasoning.
"""

from __future__ import annotations

from founder_os.decisions.store import DecisionStore
from founder_os.goals.store import GoalStore
from founder_os.insights.models import HistoricalInsights
from founder_os.insights.service import generate_insights
from founder_os.memory.store import MemoryStore
from founder_os.operating_loop.models import FounderSnapshot
from founder_os.operating_loop.service import build_founder_snapshot
from founder_os.priorities.store import PriorityStore
from founder_os.projects.store import ProjectStore
from founder_os.reviews.store import ReviewStore


def _collect_snapshot(
    *,
    goal_store: GoalStore,
    project_store: ProjectStore,
    priority_store: PriorityStore,
    decision_store: DecisionStore,
    memory_store: MemoryStore,
    review_store: ReviewStore,
) -> FounderSnapshot:
    """Build the live operating-loop snapshot for a report."""
    return build_founder_snapshot(
        goal_store=goal_store,
        project_store=project_store,
        priority_store=priority_store,
        decision_store=decision_store,
        memory_store=memory_store,
        review_store=review_store,
    )


def _collect_insights(review_store: ReviewStore) -> HistoricalInsights:
    """Build the historical insights for a report from stored review snapshots."""
    return generate_insights(review_store)
