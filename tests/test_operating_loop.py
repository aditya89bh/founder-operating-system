"""Tests for the Founder Operating Loop aggregation service."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pytest

from founder_os.decisions.sqlite_store import SQLiteDecisionStore
from founder_os.goals.sqlite_store import SQLiteGoalStore
from founder_os.memory.sqlite_store import SQLiteMemoryStore
from founder_os.models import (
    DecisionRecord,
    GoalRecord,
    GoalStatus,
    MemoryRecord,
    PriorityRecord,
    PriorityStatus,
    ProjectRecord,
    ProjectStatus,
    ReviewRecord,
)
from founder_os.operating_loop.service import (
    build_founder_snapshot,
    build_health_indicators,
    count_active_goals,
    count_active_priorities,
    count_active_projects,
    count_recent_decisions,
    count_recent_memories,
    latest_review_date,
)
from founder_os.priorities.sqlite_store import SQLitePriorityStore
from founder_os.projects.sqlite_store import SQLiteProjectStore
from founder_os.reviews.sqlite_store import SQLiteReviewStore


@dataclass
class Stores:
    goals: SQLiteGoalStore
    projects: SQLiteProjectStore
    priorities: SQLitePriorityStore
    decisions: SQLiteDecisionStore
    memory: SQLiteMemoryStore
    reviews: SQLiteReviewStore


@pytest.fixture
def stores(tmp_path: Path) -> Iterator[Stores]:
    bundle = Stores(
        goals=SQLiteGoalStore(tmp_path / "goals.db"),
        projects=SQLiteProjectStore(tmp_path / "projects.db"),
        priorities=SQLitePriorityStore(tmp_path / "priorities.db"),
        decisions=SQLiteDecisionStore(tmp_path / "decisions.db"),
        memory=SQLiteMemoryStore(tmp_path / "memory.db"),
        reviews=SQLiteReviewStore(tmp_path / "reviews.db"),
    )
    all_stores = (
        bundle.goals,
        bundle.projects,
        bundle.priorities,
        bundle.decisions,
        bundle.memory,
        bundle.reviews,
    )
    for store in all_stores:
        store.connect()
    try:
        yield bundle
    finally:
        for store in all_stores:
            store.close()


def test_count_active_goals(stores: Stores) -> None:
    stores.goals.create_goal(GoalRecord(title="Active", status=GoalStatus.ACTIVE))
    stores.goals.create_goal(GoalRecord(title="Done", status=GoalStatus.COMPLETED))
    stores.goals.create_goal(GoalRecord(title="Planned", status=GoalStatus.PLANNED))

    assert count_active_goals(stores.goals) == 1


def test_count_active_projects(stores: Stores) -> None:
    stores.projects.create_project(ProjectRecord(title="Live", status=ProjectStatus.ACTIVE))
    stores.projects.create_project(ProjectRecord(title="Live too", status=ProjectStatus.ACTIVE))
    stores.projects.create_project(ProjectRecord(title="Shipped", status=ProjectStatus.COMPLETED))

    assert count_active_projects(stores.projects) == 2


def test_count_active_priorities(stores: Stores) -> None:
    stores.priorities.create_priority(PriorityRecord(title="P1", status=PriorityStatus.ACTIVE))
    stores.priorities.create_priority(PriorityRecord(title="P2", status=PriorityStatus.COMPLETED))
    stores.priorities.create_priority(PriorityRecord(title="P3", status=PriorityStatus.DROPPED))

    assert count_active_priorities(stores.priorities) == 1


def test_count_recent_decisions_caps_at_limit(stores: Stores) -> None:
    for index in range(7):
        stores.decisions.create_decision(DecisionRecord(title=f"D{index}", decision="Decide"))

    assert count_recent_decisions(stores.decisions, limit=5) == 5
    assert count_recent_decisions(stores.decisions, limit=10) == 7


def test_count_recent_memories_caps_at_limit(stores: Stores) -> None:
    for index in range(3):
        stores.memory.add_memory(MemoryRecord(content=f"Note {index}"))

    assert count_recent_memories(stores.memory, limit=5) == 3
    assert count_recent_memories(stores.memory, limit=2) == 2


def test_latest_review_date_returns_most_recent(stores: Stores) -> None:
    stores.reviews.create_review(ReviewRecord(review_date=date(2026, 1, 1)))
    stores.reviews.create_review(ReviewRecord(review_date=date(2026, 6, 1)))

    assert latest_review_date(stores.reviews) == date(2026, 6, 1)


def test_latest_review_date_returns_none_when_empty(stores: Stores) -> None:
    assert latest_review_date(stores.reviews) is None


def test_build_founder_snapshot_aggregates_counts(stores: Stores) -> None:
    stores.goals.create_goal(GoalRecord(title="Active goal", status=GoalStatus.ACTIVE))
    stores.projects.create_project(
        ProjectRecord(title="Active project", status=ProjectStatus.ACTIVE)
    )
    stores.priorities.create_priority(
        PriorityRecord(title="Active priority", status=PriorityStatus.ACTIVE)
    )
    stores.decisions.create_decision(DecisionRecord(title="D1", decision="Decide"))
    stores.memory.add_memory(MemoryRecord(content="A note"))
    stores.reviews.create_review(ReviewRecord(review_date=date(2026, 5, 1)))

    snapshot = build_founder_snapshot(
        goal_store=stores.goals,
        project_store=stores.projects,
        priority_store=stores.priorities,
        decision_store=stores.decisions,
        memory_store=stores.memory,
        review_store=stores.reviews,
    )

    assert snapshot.active_goal_count == 1
    assert snapshot.active_project_count == 1
    assert snapshot.active_priority_count == 1
    assert snapshot.recent_decision_count == 1
    assert snapshot.recent_memory_count == 1
    assert snapshot.latest_review_date == date(2026, 5, 1)


def test_health_indicators_all_raised_when_empty() -> None:
    health = build_health_indicators(
        active_goal_count=0,
        active_project_count=0,
        active_priority_count=0,
        review_date=None,
    )

    assert health.no_active_goals is True
    assert health.no_active_projects is True
    assert health.no_active_priorities is True
    assert health.no_recent_reviews is True


def test_health_indicators_clear_when_present() -> None:
    health = build_health_indicators(
        active_goal_count=2,
        active_project_count=1,
        active_priority_count=3,
        review_date=date(2026, 6, 1),
    )

    assert health.no_active_goals is False
    assert health.no_active_projects is False
    assert health.no_active_priorities is False
    assert health.no_recent_reviews is False


def test_snapshot_health_on_empty_system(stores: Stores) -> None:
    snapshot = build_founder_snapshot(
        goal_store=stores.goals,
        project_store=stores.projects,
        priority_store=stores.priorities,
        decision_store=stores.decisions,
        memory_store=stores.memory,
        review_store=stores.reviews,
    )

    assert snapshot.active_goal_count == 0
    assert snapshot.latest_review_date is None
    assert snapshot.health.no_active_goals is True
    assert snapshot.health.no_active_projects is True
    assert snapshot.health.no_active_priorities is True
    assert snapshot.health.no_recent_reviews is True


def test_snapshot_health_partial(stores: Stores) -> None:
    stores.goals.create_goal(GoalRecord(title="Active goal", status=GoalStatus.ACTIVE))
    stores.reviews.create_review(ReviewRecord(review_date=date(2026, 4, 1)))

    snapshot = build_founder_snapshot(
        goal_store=stores.goals,
        project_store=stores.projects,
        priority_store=stores.priorities,
        decision_store=stores.decisions,
        memory_store=stores.memory,
        review_store=stores.reviews,
    )

    assert snapshot.health.no_active_goals is False
    assert snapshot.health.no_recent_reviews is False
    assert snapshot.health.no_active_projects is True
    assert snapshot.health.no_active_priorities is True
