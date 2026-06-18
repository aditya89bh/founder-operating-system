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
