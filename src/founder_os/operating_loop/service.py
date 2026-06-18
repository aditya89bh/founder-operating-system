"""The operating loop service.

This module aggregates the state of every engine into a single
:class:`~founder_os.operating_loop.models.FounderSnapshot`. Each engine has its
own focused aggregation helper; together they form the deterministic workflow
that turns the collection of engines into one operating system. No scoring,
ranking, recommendation, or AI reasoning happens here -- only counting and
direct reads.
"""

from __future__ import annotations

from founder_os.goals.store import GoalStore
from founder_os.models import GoalStatus, ProjectStatus
from founder_os.projects.store import ProjectStore

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
