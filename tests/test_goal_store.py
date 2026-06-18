"""Tests for the SQLite-backed goal store."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest

from founder_os.goals.sqlite_store import SQLiteGoalStore
from founder_os.models import GoalRecord, GoalStatus, GoalTimeframe


@pytest.fixture
def store(tmp_path: Path) -> Iterator[SQLiteGoalStore]:
    goal_store = SQLiteGoalStore(tmp_path / "goals.db")
    goal_store.connect()
    try:
        yield goal_store
    finally:
        goal_store.close()


def test_create_and_get_goal(store: SQLiteGoalStore) -> None:
    record = store.create_goal(
        GoalRecord(
            title="Reach 100 paying customers",
            description="Grow from design partners to a repeatable sales motion.",
            timeframe=GoalTimeframe.YEARLY,
            target_date=date(2026, 12, 31),
            status=GoalStatus.ACTIVE,
        )
    )

    fetched = store.get_goal(record.id)

    assert fetched is not None
    assert fetched.id == record.id
    assert fetched.title == "Reach 100 paying customers"
    assert fetched.description.startswith("Grow from")
    assert fetched.timeframe is GoalTimeframe.YEARLY
    assert fetched.target_date == date(2026, 12, 31)
    assert fetched.status is GoalStatus.ACTIVE


def test_get_missing_goal_returns_none(store: SQLiteGoalStore) -> None:
    assert store.get_goal("does-not-exist") is None


def test_list_goals_orders_newest_first(store: SQLiteGoalStore) -> None:
    first = store.create_goal(GoalRecord(title="First"))
    second = store.create_goal(GoalRecord(title="Second"))

    listed = store.list_goals()

    assert [record.id for record in listed] == [second.id, first.id]


def test_delete_goal(store: SQLiteGoalStore) -> None:
    record = store.create_goal(GoalRecord(title="Temporary"))

    assert store.delete_goal(record.id) is True
    assert store.get_goal(record.id) is None


def test_delete_missing_goal_returns_false(store: SQLiteGoalStore) -> None:
    assert store.delete_goal("does-not-exist") is False


def test_timeframe_and_status_round_trip(store: SQLiteGoalStore) -> None:
    record = store.create_goal(
        GoalRecord(
            title="Close the seed round",
            timeframe=GoalTimeframe.QUARTERLY,
            status=GoalStatus.PLANNED,
        )
    )

    fetched = store.get_goal(record.id)

    assert fetched is not None
    assert fetched.timeframe is GoalTimeframe.QUARTERLY
    assert fetched.status is GoalStatus.PLANNED


def test_goal_without_target_date_defaults_to_none(store: SQLiteGoalStore) -> None:
    record = store.create_goal(GoalRecord(title="No target date"))

    fetched = store.get_goal(record.id)

    assert fetched is not None
    assert fetched.target_date is None
