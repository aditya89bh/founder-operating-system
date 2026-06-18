"""Snapshot generation for the review engine.

A snapshot captures point-in-time counts read from the other engines. It is
computed once when a review is created and then stored on the review, so the
review remains a faithful historical record even as the underlying data changes.
"""

from __future__ import annotations

from dataclasses import dataclass

from founder_os.decisions.store import DecisionStore
from founder_os.goals.store import GoalStore
from founder_os.memory.store import MemoryStore
from founder_os.models import GoalStatus, PriorityStatus, ProjectStatus
from founder_os.priorities.store import PriorityStore
from founder_os.projects.store import ProjectStore


@dataclass(frozen=True)
class ReviewSnapshot:
    """Point-in-time counts captured from across the system."""

    active_goals: int
    completed_goals: int
    active_projects: int
    completed_projects: int
    active_priorities: int
    completed_priorities: int
    decision_count: int
    memory_count: int


def generate_snapshot(
    *,
    goal_store: GoalStore,
    project_store: ProjectStore,
    priority_store: PriorityStore,
    decision_store: DecisionStore,
    memory_store: MemoryStore,
) -> ReviewSnapshot:
    """Compute a :class:`ReviewSnapshot` from the current state of every engine."""
    goals = goal_store.list_goals()
    projects = project_store.list_projects()
    priorities = priority_store.list_priorities()
    return ReviewSnapshot(
        active_goals=sum(1 for goal in goals if goal.status is GoalStatus.ACTIVE),
        completed_goals=sum(1 for goal in goals if goal.status is GoalStatus.COMPLETED),
        active_projects=sum(
            1 for project in projects if project.status is ProjectStatus.ACTIVE
        ),
        completed_projects=sum(
            1 for project in projects if project.status is ProjectStatus.COMPLETED
        ),
        active_priorities=sum(
            1 for priority in priorities if priority.status is PriorityStatus.ACTIVE
        ),
        completed_priorities=sum(
            1 for priority in priorities if priority.status is PriorityStatus.COMPLETED
        ),
        decision_count=len(decision_store.list_decisions()),
        memory_count=len(memory_store.list_memories()),
    )
