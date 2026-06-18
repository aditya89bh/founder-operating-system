"""Tests for the SQLite-backed project store."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest

from founder_os.models import ProjectRecord, ProjectStatus
from founder_os.projects.sqlite_store import SQLiteProjectStore


@pytest.fixture
def store(tmp_path: Path) -> Iterator[SQLiteProjectStore]:
    project_store = SQLiteProjectStore(tmp_path / "projects.db")
    project_store.connect()
    try:
        yield project_store
    finally:
        project_store.close()


def test_create_and_get_project(store: SQLiteProjectStore) -> None:
    record = store.create_project(
        ProjectRecord(
            title="Onboarding revamp",
            description="Rebuild the first-run experience.",
            status=ProjectStatus.ACTIVE,
            start_date=date(2026, 1, 1),
            target_date=date(2026, 3, 31),
        )
    )

    fetched = store.get_project(record.id)

    assert fetched is not None
    assert fetched.id == record.id
    assert fetched.title == "Onboarding revamp"
    assert fetched.description == "Rebuild the first-run experience."
    assert fetched.status is ProjectStatus.ACTIVE
    assert fetched.start_date == date(2026, 1, 1)
    assert fetched.target_date == date(2026, 3, 31)


def test_get_missing_project_returns_none(store: SQLiteProjectStore) -> None:
    assert store.get_project("does-not-exist") is None


def test_list_projects_orders_newest_first(store: SQLiteProjectStore) -> None:
    first = store.create_project(ProjectRecord(title="First"))
    second = store.create_project(ProjectRecord(title="Second"))

    listed = store.list_projects()

    assert [record.id for record in listed] == [second.id, first.id]


def test_delete_project(store: SQLiteProjectStore) -> None:
    record = store.create_project(ProjectRecord(title="Temporary"))

    assert store.delete_project(record.id) is True
    assert store.get_project(record.id) is None


def test_delete_missing_project_returns_false(store: SQLiteProjectStore) -> None:
    assert store.delete_project("does-not-exist") is False


def test_status_round_trip(store: SQLiteProjectStore) -> None:
    record = store.create_project(
        ProjectRecord(title="Migrate billing", status=ProjectStatus.PLANNED)
    )

    fetched = store.get_project(record.id)

    assert fetched is not None
    assert fetched.status is ProjectStatus.PLANNED


def test_project_without_dates_defaults_to_none(store: SQLiteProjectStore) -> None:
    record = store.create_project(ProjectRecord(title="No dates"))

    fetched = store.get_project(record.id)

    assert fetched is not None
    assert fetched.start_date is None
    assert fetched.target_date is None


def test_link_project_to_goal_and_retrieve(store: SQLiteProjectStore) -> None:
    first = store.create_project(ProjectRecord(title="First project"))
    second = store.create_project(ProjectRecord(title="Second project"))

    store.link_project_to_goal(first.id, "goal-a")
    store.link_project_to_goal(second.id, "goal-a")

    assert store.get_goal_projects("goal-a") == sorted([first.id, second.id])


def test_get_goal_projects_empty_by_default(store: SQLiteProjectStore) -> None:
    assert store.get_goal_projects("goal-a") == []


def test_relinking_project_moves_it_to_new_goal(store: SQLiteProjectStore) -> None:
    project = store.create_project(ProjectRecord(title="Movable project"))

    store.link_project_to_goal(project.id, "goal-a")
    store.link_project_to_goal(project.id, "goal-b")

    assert store.get_goal_projects("goal-a") == []
    assert store.get_goal_projects("goal-b") == [project.id]


def test_deleting_project_removes_its_goal_link(store: SQLiteProjectStore) -> None:
    project = store.create_project(ProjectRecord(title="Temporary project"))
    store.link_project_to_goal(project.id, "goal-a")

    assert store.delete_project(project.id) is True
    assert store.get_goal_projects("goal-a") == []
