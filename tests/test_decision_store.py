"""Tests for the SQLite-backed decision store."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest

from founder_os.decisions.sqlite_store import SQLiteDecisionStore
from founder_os.models import DecisionOutcome, DecisionRecord


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


def test_rationale_and_context_are_persisted(store: SQLiteDecisionStore) -> None:
    record = store.create_decision(
        DecisionRecord(
            title="Choose database",
            context="Evaluating storage for the memory engine",
            decision="Use SQLite",
            rationale="Zero-config and embedded",
            assumptions="Single-writer workload is sufficient",
        )
    )

    fetched = store.get_decision(record.id)

    assert fetched is not None
    assert fetched.context == "Evaluating storage for the memory engine"
    assert fetched.rationale == "Zero-config and embedded"
    assert fetched.assumptions == "Single-writer workload is sufficient"


def test_new_decision_starts_pending(store: SQLiteDecisionStore) -> None:
    record = store.create_decision(DecisionRecord(title="Plan offsite", decision="Book venue"))

    assert record.outcome is DecisionOutcome.PENDING
    assert record.review_date is None


def test_update_outcome_records_result_and_review(store: SQLiteDecisionStore) -> None:
    record = store.create_decision(DecisionRecord(title="Launch beta", decision="Ship to 50 users"))

    updated = store.update_outcome(
        record.id,
        "successful",
        outcome_notes="Strong engagement",
        review_date=date(2026, 3, 1),
    )

    assert updated is not None
    assert updated.outcome is DecisionOutcome.SUCCESSFUL
    assert updated.outcome_notes == "Strong engagement"
    assert updated.review_date == date(2026, 3, 1)

    reloaded = store.get_decision(record.id)
    assert reloaded is not None
    assert reloaded.outcome is DecisionOutcome.SUCCESSFUL
    assert reloaded.review_date == date(2026, 3, 1)


def test_update_outcome_missing_decision_returns_none(store: SQLiteDecisionStore) -> None:
    assert store.update_outcome("does-not-exist", "successful") is None


def test_update_outcome_rejects_invalid_outcome(store: SQLiteDecisionStore) -> None:
    record = store.create_decision(DecisionRecord(title="Pick CRM", decision="Use a CRM"))

    with pytest.raises(ValueError):
        store.update_outcome(record.id, "not-a-valid-outcome")
