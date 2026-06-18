"""Tests for the SQLite-backed decision store."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from founder_os.decisions.sqlite_store import SQLiteDecisionStore
from founder_os.models import DecisionRecord


@pytest.fixture
def store(tmp_path: Path) -> Iterator[SQLiteDecisionStore]:
    decision_store = SQLiteDecisionStore(tmp_path / "decisions.db")
    decision_store.connect()
    try:
        yield decision_store
    finally:
        decision_store.close()


def test_create_and_get_decision(store: SQLiteDecisionStore) -> None:
    record = store.create_decision(
        DecisionRecord(title="Adopt weekly planning", decision="Run Monday planning")
    )

    fetched = store.get_decision(record.id)

    assert fetched is not None
    assert fetched.id == record.id
    assert fetched.title == "Adopt weekly planning"
    assert fetched.decision == "Run Monday planning"


def test_get_missing_decision_returns_none(store: SQLiteDecisionStore) -> None:
    assert store.get_decision("does-not-exist") is None


def test_list_decisions_returns_all(store: SQLiteDecisionStore) -> None:
    store.create_decision(DecisionRecord(title="First", decision="Do A"))
    store.create_decision(DecisionRecord(title="Second", decision="Do B"))

    records = store.list_decisions()

    assert {record.title for record in records} == {"First", "Second"}


def test_delete_decision_removes_record(store: SQLiteDecisionStore) -> None:
    record = store.create_decision(DecisionRecord(title="Temporary", decision="Do C"))

    assert store.delete_decision(record.id) is True
    assert store.get_decision(record.id) is None
    assert store.delete_decision(record.id) is False
