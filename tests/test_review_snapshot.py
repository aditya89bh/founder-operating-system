"""Tests for review snapshot generation and persistence."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
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
from founder_os.priorities.sqlite_store import SQLitePriorityStore
from founder_os.projects.sqlite_store import SQLiteProjectStore
from founder_os.reviews.snapshot import generate_snapshot
from founder_os.reviews.sqlite_store import SQLiteReviewStore


@dataclass
class Stores:
    goals: SQLiteGoalStore
    projects: SQLiteProjectStore
    priorities: SQLitePriorityStore
    decisions: SQLiteDecisionStore
    memory: SQLiteMemoryStore


@pytest.fixture
def stores(tmp_path: Path) -> Iterator[Stores]:
    bundle = Stores(
        goals=SQLiteGoalStore(tmp_path / "goals.db"),
        projects=SQLiteProjectStore(tmp_path / "projects.db"),
        priorities=SQLitePriorityStore(tmp_path / "priorities.db"),
        decisions=SQLiteDecisionStore(tmp_path / "decisions.db"),
        memory=SQLiteMemoryStore(tmp_path / "memory.db"),
    )
    all_stores = (
        bundle.goals,
        bundle.projects,
        bundle.priorities,
        bundle.decisions,
        bundle.memory,
    )
    for store in all_stores:
        store.connect()
    try:
        yield bundle
    finally:
        for store in all_stores:
            store.close()


def test_generate_snapshot_counts_each_engine(stores: Stores) -> None:
    stores.goals.create_goal(GoalRecord(title="Active A", status=GoalStatus.ACTIVE))
    stores.goals.create_goal(GoalRecord(title="Active B", status=GoalStatus.ACTIVE))
    stores.goals.create_goal(GoalRecord(title="Done", status=GoalStatus.COMPLETED))
    stores.goals.create_goal(GoalRecord(title="Planned", status=GoalStatus.PLANNED))

    stores.projects.create_project(ProjectRecord(title="Live", status=ProjectStatus.ACTIVE))
    stores.projects.create_project(ProjectRecord(title="Shipped", status=ProjectStatus.COMPLETED))
    stores.projects.create_project(ProjectRecord(title="Done too", status=ProjectStatus.COMPLETED))

    stores.priorities.create_priority(PriorityRecord(title="P1", status=PriorityStatus.ACTIVE))
    stores.priorities.create_priority(PriorityRecord(title="P2", status=PriorityStatus.ACTIVE))
    stores.priorities.create_priority(PriorityRecord(title="P3", status=PriorityStatus.ACTIVE))
    stores.priorities.create_priority(PriorityRecord(title="P4", status=PriorityStatus.COMPLETED))
    stores.priorities.create_priority(PriorityRecord(title="P5", status=PriorityStatus.DROPPED))

    stores.decisions.create_decision(DecisionRecord(title="D1", decision="Do it"))
    stores.decisions.create_decision(DecisionRecord(title="D2", decision="Do that"))

    for index in range(4):
        stores.memory.add_memory(MemoryRecord(content=f"Note {index}"))

    snapshot = generate_snapshot(
        goal_store=stores.goals,
        project_store=stores.projects,
        priority_store=stores.priorities,
        decision_store=stores.decisions,
        memory_store=stores.memory,
    )

    assert snapshot.active_goals == 2
    assert snapshot.completed_goals == 1
    assert snapshot.active_projects == 1
    assert snapshot.completed_projects == 2
    assert snapshot.active_priorities == 3
    assert snapshot.completed_priorities == 1
    assert snapshot.decision_count == 2
    assert snapshot.memory_count == 4


def test_empty_system_produces_zero_snapshot(stores: Stores) -> None:
    snapshot = generate_snapshot(
        goal_store=stores.goals,
        project_store=stores.projects,
        priority_store=stores.priorities,
        decision_store=stores.decisions,
        memory_store=stores.memory,
    )

    assert snapshot.active_goals == 0
    assert snapshot.completed_goals == 0
    assert snapshot.active_projects == 0
    assert snapshot.completed_projects == 0
    assert snapshot.active_priorities == 0
    assert snapshot.completed_priorities == 0
    assert snapshot.decision_count == 0
    assert snapshot.memory_count == 0


def test_snapshot_values_persist_on_review(tmp_path: Path, stores: Stores) -> None:
    stores.goals.create_goal(GoalRecord(title="Active", status=GoalStatus.ACTIVE))
    stores.decisions.create_decision(DecisionRecord(title="D1", decision="Do it"))
    stores.memory.add_memory(MemoryRecord(content="A note"))

    snapshot = generate_snapshot(
        goal_store=stores.goals,
        project_store=stores.projects,
        priority_store=stores.priorities,
        decision_store=stores.decisions,
        memory_store=stores.memory,
    )

    review_store = SQLiteReviewStore(tmp_path / "reviews.db")
    review_store.connect()
    try:
        created = review_store.create_review(
            ReviewRecord(
                active_goals=snapshot.active_goals,
                completed_goals=snapshot.completed_goals,
                active_projects=snapshot.active_projects,
                completed_projects=snapshot.completed_projects,
                active_priorities=snapshot.active_priorities,
                completed_priorities=snapshot.completed_priorities,
                decision_count=snapshot.decision_count,
                memory_count=snapshot.memory_count,
            )
        )
        fetched = review_store.get_review(created.id)
    finally:
        review_store.close()

    assert fetched is not None
    assert fetched.active_goals == 1
    assert fetched.decision_count == 1
    assert fetched.memory_count == 1
    assert fetched.completed_goals == 0
    assert fetched.active_projects == 0
