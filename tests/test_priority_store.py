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


def test_score_uses_deterministic_formula() -> None:
    record = PriorityRecord(title="Scored", urgency=4, importance=3, effort=2)

    assert record.score == pytest.approx(6.0)


def test_default_score_is_neutral() -> None:
    record = PriorityRecord(title="Defaults")

    assert record.score == pytest.approx(3.0)


def test_rank_priorities_orders_by_score_descending(store: SQLitePriorityStore) -> None:
    low = store.create_priority(PriorityRecord(title="Low", urgency=2, importance=2, effort=4))
    high = store.create_priority(PriorityRecord(title="High", urgency=5, importance=5, effort=1))
    mid = store.create_priority(PriorityRecord(title="Mid", urgency=3, importance=3, effort=3))

    ranked = store.rank_priorities()

    assert [record.id for record in ranked] == [high.id, mid.id, low.id]
    assert [round(record.score, 2) for record in ranked] == [25.0, 3.0, 1.0]


def test_rank_priorities_excludes_inactive(store: SQLitePriorityStore) -> None:
    active = store.create_priority(
        PriorityRecord(title="Active", urgency=4, importance=4, effort=2)
    )
    store.create_priority(
        PriorityRecord(
            title="Completed",
            urgency=5,
            importance=5,
            effort=1,
            status=PriorityStatus.COMPLETED,
        )
    )

    ranked = store.rank_priorities()

    assert [record.id for record in ranked] == [active.id]
