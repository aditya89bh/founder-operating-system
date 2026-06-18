"""Tests for the historical insight service."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest

from founder_os.insights.models import HistoricalInsights
from founder_os.insights.report import render_insights_report
from founder_os.insights.service import generate_insights
from founder_os.models import ReviewRecord
from founder_os.reviews.sqlite_store import SQLiteReviewStore


@pytest.fixture
def review_store(tmp_path: Path) -> Iterator[SQLiteReviewStore]:
    store = SQLiteReviewStore(tmp_path / "reviews.db")
    store.connect()
    try:
        yield store
    finally:
        store.close()


def _make_review(
    review_date: date,
    *,
    active_goals: int = 0,
    active_projects: int = 0,
    active_priorities: int = 0,
    decision_count: int = 0,
    memory_count: int = 0,
) -> ReviewRecord:
    return ReviewRecord(
        review_date=review_date,
        active_goals=active_goals,
        active_projects=active_projects,
        active_priorities=active_priorities,
        decision_count=decision_count,
        memory_count=memory_count,
    )


def test_empty_insights(review_store: SQLiteReviewStore) -> None:
    insights = generate_insights(review_store)

    assert insights.review_count == 0
    assert insights.oldest_review_date is None
    assert insights.newest_review_date is None
    assert insights.goal_growth == 0
    assert insights.project_growth == 0
    assert insights.priority_growth == 0
    assert insights.decision_growth == 0
    assert insights.memory_growth == 0


def test_single_review_has_zero_growth(review_store: SQLiteReviewStore) -> None:
    review_store.create_review(_make_review(date(2026, 3, 1), active_goals=4, decision_count=10))

    insights = generate_insights(review_store)

    assert insights.review_count == 1
    assert insights.oldest_review_date == date(2026, 3, 1)
    assert insights.newest_review_date == date(2026, 3, 1)
    assert insights.goal_growth == 0
    assert insights.decision_growth == 0


def test_review_count_and_date_range(review_store: SQLiteReviewStore) -> None:
    review_store.create_review(_make_review(date(2026, 1, 1)))
    review_store.create_review(_make_review(date(2026, 4, 1)))
    review_store.create_review(_make_review(date(2026, 6, 1)))

    insights = generate_insights(review_store)

    assert insights.review_count == 3
    assert insights.oldest_review_date == date(2026, 1, 1)
    assert insights.newest_review_date == date(2026, 6, 1)


def test_growth_is_latest_minus_earliest(review_store: SQLiteReviewStore) -> None:
    review_store.create_review(
        _make_review(
            date(2026, 1, 1),
            active_goals=1,
            active_projects=2,
            active_priorities=3,
            decision_count=4,
            memory_count=5,
        )
    )
    review_store.create_review(
        _make_review(
            date(2026, 6, 1),
            active_goals=5,
            active_projects=4,
            active_priorities=10,
            decision_count=20,
            memory_count=30,
        )
    )

    insights = generate_insights(review_store)

    assert insights.goal_growth == 4
    assert insights.project_growth == 2
    assert insights.priority_growth == 7
    assert insights.decision_growth == 16
    assert insights.memory_growth == 25


def test_growth_can_be_negative(review_store: SQLiteReviewStore) -> None:
    review_store.create_review(_make_review(date(2026, 1, 1), active_goals=10))
    review_store.create_review(_make_review(date(2026, 6, 1), active_goals=3))

    insights = generate_insights(review_store)

    assert insights.goal_growth == -7


def test_growth_ignores_insertion_order(review_store: SQLiteReviewStore) -> None:
    # Insert the newest review first to confirm ordering is by review date.
    review_store.create_review(_make_review(date(2026, 6, 1), decision_count=20))
    review_store.create_review(_make_review(date(2026, 1, 1), decision_count=5))

    insights = generate_insights(review_store)

    assert insights.oldest_review_date == date(2026, 1, 1)
    assert insights.newest_review_date == date(2026, 6, 1)
    assert insights.decision_growth == 15


def test_render_report_with_reviews(review_store: SQLiteReviewStore) -> None:
    review_store.create_review(_make_review(date(2026, 1, 1), active_goals=1, memory_count=30))
    review_store.create_review(_make_review(date(2026, 6, 1), active_goals=5, memory_count=10))
    insights = generate_insights(review_store)

    report = render_insights_report(insights)

    assert "Historical insights" in report
    assert "Reviews recorded: 2" in report
    assert "Review range:     2026-01-01 -> 2026-06-01" in report
    assert "Goals:      +4" in report
    assert "Memories:   -20" in report


def test_render_report_for_empty_history() -> None:
    report = render_insights_report(HistoricalInsights())

    assert "Reviews recorded: 0" in report
    assert "Review range:     no reviews recorded" in report
    assert "Goals:      +0" in report
    assert "Decisions:  +0" in report
