"""Tests for the SQLite-backed review store."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest

from founder_os.models import ReviewRecord, ReviewType
from founder_os.reviews.sqlite_store import SQLiteReviewStore


@pytest.fixture
def store(tmp_path: Path) -> Iterator[SQLiteReviewStore]:
    review_store = SQLiteReviewStore(tmp_path / "reviews.db")
    review_store.connect()
    try:
        yield review_store
    finally:
        review_store.close()


def test_create_and_get_review(store: SQLiteReviewStore) -> None:
    record = store.create_review(
        ReviewRecord(
            review_date=date(2026, 6, 15),
            review_type=ReviewType.MONTHLY,
            notes="Strong month for fundraising.",
        )
    )

    fetched = store.get_review(record.id)

    assert fetched is not None
    assert fetched.id == record.id
    assert fetched.review_date == date(2026, 6, 15)
    assert fetched.review_type is ReviewType.MONTHLY
    assert fetched.notes == "Strong month for fundraising."


def test_get_missing_review_returns_none(store: SQLiteReviewStore) -> None:
    assert store.get_review("does-not-exist") is None


def test_list_reviews_orders_newest_first(store: SQLiteReviewStore) -> None:
    older = store.create_review(ReviewRecord(review_date=date(2026, 1, 1)))
    newer = store.create_review(ReviewRecord(review_date=date(2026, 6, 1)))

    listed = store.list_reviews()

    assert [record.id for record in listed] == [newer.id, older.id]


def test_delete_review(store: SQLiteReviewStore) -> None:
    record = store.create_review(ReviewRecord(review_date=date(2026, 3, 1)))

    assert store.delete_review(record.id) is True
    assert store.get_review(record.id) is None


def test_delete_missing_review_returns_false(store: SQLiteReviewStore) -> None:
    assert store.delete_review("does-not-exist") is False
