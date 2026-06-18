"""The operating loop service.

This module aggregates the state of every engine into a single
:class:`~founder_os.operating_loop.models.FounderSnapshot`. Each engine has its
own focused aggregation helper; together they form the deterministic workflow
that turns the collection of engines into one operating system. No scoring,
ranking, recommendation, or AI reasoning happens here -- only counting and
direct reads.
"""

from __future__ import annotations

from datetime import date

from founder_os.decisions.store import DecisionStore
from founder_os.goals.store import GoalStore
from founder_os.memory.store import MemoryStore
from founder_os.models import GoalStatus, PriorityStatus, ProjectStatus
from founder_os.operating_loop.models import FounderSnapshot
from founder_os.priorities.store import PriorityStore
from founder_os.projects.store import ProjectStore
from founder_os.reviews.store import ReviewStore

# The number of most-recent records treated as "recent" activity for an engine.
DEFAULT_RECENT_LIMIT = 5


def count_active_goals(goal_store: GoalStore) -> int:
    """Return the number of goals currently in the active state."""
    return sum(1 for goal in goal_store.list_goals() if goal.status is GoalStatus.ACTIVE)


def count_active_projects(project_store: ProjectStore) -> int:
    """Return the number of projects currently in the active state."""
    return sum(
        1 for project in project_store.list_projects() if project.status is ProjectStatus.ACTIVE
    )


def count_active_priorities(priority_store: PriorityStore) -> int:
    """Return the number of priorities currently in the active state."""
    return sum(
        1
        for priority in priority_store.list_priorities()
        if priority.status is PriorityStatus.ACTIVE
    )


def count_recent_decisions(
    decision_store: DecisionStore, *, limit: int = DEFAULT_RECENT_LIMIT
) -> int:
    """Return the number of recent decisions, capped at the ``limit`` most recent."""
    return len(decision_store.list_decisions()[:limit])


def count_recent_memories(memory_store: MemoryStore, *, limit: int = DEFAULT_RECENT_LIMIT) -> int:
    """Return the number of recent memories, capped at the ``limit`` most recent."""
    return len(memory_store.list_memories()[:limit])


def latest_review_date(review_store: ReviewStore) -> date | None:
    """Return the date of the most recent review, or ``None`` when none exist."""
    reviews = review_store.list_reviews()
    if not reviews:
        return None
    return reviews[0].review_date


def build_founder_snapshot(
    *,
    goal_store: GoalStore,
    project_store: ProjectStore,
    priority_store: PriorityStore,
    decision_store: DecisionStore,
    memory_store: MemoryStore,
    review_store: ReviewStore,
    recent_limit: int = DEFAULT_RECENT_LIMIT,
) -> FounderSnapshot:
    """Assemble a :class:`FounderSnapshot` by aggregating every engine."""
    return FounderSnapshot(
        active_goal_count=count_active_goals(goal_store),
        active_project_count=count_active_projects(project_store),
        active_priority_count=count_active_priorities(priority_store),
        recent_decision_count=count_recent_decisions(decision_store, limit=recent_limit),
        recent_memory_count=count_recent_memories(memory_store, limit=recent_limit),
        latest_review_date=latest_review_date(review_store),
    )
