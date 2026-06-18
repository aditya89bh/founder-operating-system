"""Storage interface for the goal engine.

The :class:`GoalStore` protocol defines the contract that any goal backend must
satisfy. It covers goal persistence as well as the relationship storage that
aligns priorities with the goals they serve. It describes behavior only;
concrete persistence lives in implementations such as
:mod:`founder_os.goals.sqlite_store`.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from founder_os.models import GoalRecord


@runtime_checkable
class GoalStore(Protocol):
    """A backend capable of storing and retrieving goals and their priorities."""

    def create_goal(self, goal: GoalRecord) -> GoalRecord:
        """Persist ``goal`` and return the stored record."""
        ...

    def get_goal(self, goal_id: str) -> GoalRecord | None:
        """Return the goal with ``goal_id`` or ``None`` if it is absent."""
        ...

    def list_goals(self) -> list[GoalRecord]:
        """Return stored goals, newest first."""
        ...

    def delete_goal(self, goal_id: str) -> bool:
        """Delete the goal with ``goal_id``; return ``True`` if a row was removed."""
        ...

    def link_priority_to_goal(self, priority_id: str, goal_id: str) -> None:
        """Align a priority with a goal, replacing any existing alignment."""
        ...

    def get_goal_priorities(self, goal_id: str) -> list[str]:
        """Return the identifiers of priorities aligned with ``goal_id``."""
        ...
