"""Tests for the SQLite-backed priority store."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from founder_os.models import PriorityRecord, PriorityStatus
from founder_os.priorities.sqlite_store import SQLitePriorityStore


@pytest.fixture
def store(tmp_path: Path) -> Iterator[SQLitePriorityStore]:
    priority_store = SQLitePriorityStore(tmp_path / "priorities.db")
    priority_store.connect()
    try:
        yield priority_store
    finally:
        priority_store.close()


def test_create_and_get_priority(store: SQLitePriorityStore) -> None:
    record = store.create_priority(
        PriorityRecord(
            title="Ship onboarding revamp",
            description="Reduce time-to-value for new users",
            category="product",
            urgency=5,
            importance=4,
            effort=2,
        )
    )

    fetched = store.get_priority(record.id)

    assert fetched is not None
    assert fetched.id == record.id
    assert fetched.title == "Ship onboarding revamp"
    assert fetched.description == "Reduce time-to-value for new users"
    assert fetched.category == "product"
    assert fetched.urgency == 5
    assert fetched.importance == 4
    assert fetched.effort == 2
    assert fetched.status is PriorityStatus.ACTIVE


def test_get_missing_priority_returns_none(store: SQLitePriorityStore) -> None:
    assert store.get_priority("does-not-exist") is None


def test_list_priorities_orders_newest_first(store: SQLitePriorityStore) -> None:
    first = store.create_priority(PriorityRecord(title="First"))
    second = store.create_priority(PriorityRecord(title="Second"))

    listed = store.list_priorities()

    assert [record.id for record in listed] == [second.id, first.id]


def test_delete_priority(store: SQLitePriorityStore) -> None:
    record = store.create_priority(PriorityRecord(title="Temporary"))

    assert store.delete_priority(record.id) is True
    assert store.get_priority(record.id) is None


def test_delete_missing_priority_returns_false(store: SQLitePriorityStore) -> None:
    assert store.delete_priority("does-not-exist") is False
