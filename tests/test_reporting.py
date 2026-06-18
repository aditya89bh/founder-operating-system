"""Tests for the founder report service and exporters."""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pytest

from founder_os.decisions.sqlite_store import SQLiteDecisionStore
from founder_os.goals.sqlite_store import SQLiteGoalStore
from founder_os.memory.sqlite_store import SQLiteMemoryStore
from founder_os.models import (
    GoalRecord,
    GoalStatus,
    ProjectRecord,
    ProjectStatus,
    ReviewRecord,
)
from founder_os.priorities.sqlite_store import SQLitePriorityStore
from founder_os.projects.sqlite_store import SQLiteProjectStore
from founder_os.reporting.json_export import render_json
from founder_os.reporting.markdown import render_markdown
from founder_os.reporting.models import ReportSection
from founder_os.reporting.service import build_founder_report
from founder_os.reviews.sqlite_store import SQLiteReviewStore


@dataclass
class Stores:
    goals: SQLiteGoalStore
    projects: SQLiteProjectStore
    priorities: SQLitePriorityStore
    decisions: SQLiteDecisionStore
    memory: SQLiteMemoryStore
    reviews: SQLiteReviewStore


@pytest.fixture
def stores(tmp_path: Path) -> Iterator[Stores]:
    bundle = Stores(
        goals=SQLiteGoalStore(tmp_path / "goals.db"),
        projects=SQLiteProjectStore(tmp_path / "projects.db"),
        priorities=SQLitePriorityStore(tmp_path / "priorities.db"),
        decisions=SQLiteDecisionStore(tmp_path / "decisions.db"),
        memory=SQLiteMemoryStore(tmp_path / "memory.db"),
        reviews=SQLiteReviewStore(tmp_path / "reviews.db"),
    )
    all_stores = (
        bundle.goals,
        bundle.projects,
        bundle.priorities,
        bundle.decisions,
        bundle.memory,
        bundle.reviews,
    )
    for store in all_stores:
        store.connect()
    try:
        yield bundle
    finally:
        for store in all_stores:
            store.close()


def test_report_combines_snapshot_and_insights(stores: Stores) -> None:
    stores.goals.create_goal(GoalRecord(title="Active goal", status=GoalStatus.ACTIVE))
    stores.projects.create_project(
        ProjectRecord(title="Active project", status=ProjectStatus.ACTIVE)
    )
    stores.reviews.create_review(ReviewRecord(review_date=date(2026, 1, 1), active_goals=0))
    stores.reviews.create_review(ReviewRecord(review_date=date(2026, 6, 1), active_goals=4))

    report = build_founder_report(
        goal_store=stores.goals,
        project_store=stores.projects,
        priority_store=stores.priorities,
        decision_store=stores.decisions,
        memory_store=stores.memory,
        review_store=stores.reviews,
    )

    assert report.snapshot.active_goal_count == 1
    assert report.snapshot.active_project_count == 1
    assert report.snapshot.latest_review_date == date(2026, 6, 1)
    assert report.insights.review_count == 2
    assert report.insights.goal_growth == 4
    assert report.insights.oldest_review_date == date(2026, 1, 1)


def test_report_empty_system(stores: Stores) -> None:
    report = build_founder_report(
        goal_store=stores.goals,
        project_store=stores.projects,
        priority_store=stores.priorities,
        decision_store=stores.decisions,
        memory_store=stores.memory,
        review_store=stores.reviews,
    )

    assert report.snapshot.active_goal_count == 0
    assert report.snapshot.health.no_active_goals is True
    assert report.insights.review_count == 0
    assert report.insights.goal_growth == 0
    assert report.insights.oldest_review_date is None


def _populated_report(stores: Stores):  # type: ignore[no-untyped-def]
    stores.goals.create_goal(GoalRecord(title="Active goal", status=GoalStatus.ACTIVE))
    stores.goals.create_goal(GoalRecord(title="Another", status=GoalStatus.ACTIVE))
    stores.projects.create_project(
        ProjectRecord(title="Active project", status=ProjectStatus.ACTIVE)
    )
    stores.reviews.create_review(ReviewRecord(review_date=date(2026, 1, 1), active_goals=0))
    stores.reviews.create_review(ReviewRecord(review_date=date(2026, 6, 1), active_goals=5))
    return build_founder_report(
        goal_store=stores.goals,
        project_store=stores.projects,
        priority_store=stores.priorities,
        decision_store=stores.decisions,
        memory_store=stores.memory,
        review_store=stores.reviews,
    )


def test_markdown_export_has_all_sections(stores: Stores) -> None:
    report = _populated_report(stores)

    markdown = render_markdown(report)

    assert "# Founder Report" in markdown
    for section in ReportSection:
        assert f"## {section.value}" in markdown
    assert "- Active goals: 2" in markdown
    assert "- Goals: +5" in markdown
    assert "- Reviews recorded: 2" in markdown


def test_json_export_has_all_sections(stores: Stores) -> None:
    report = _populated_report(stores)

    payload = json.loads(render_json(report))

    assert set(payload) == {
        "current_state",
        "health_indicators",
        "historical_growth",
        "review_history",
    }
    assert payload["current_state"]["active_goals"] == 2
    assert payload["historical_growth"]["goals"] == 5
    assert payload["review_history"]["reviews_recorded"] == 2
    assert payload["review_history"]["oldest_review_date"] == "2026-01-01"


def test_markdown_and_json_carry_identical_information(stores: Stores) -> None:
    report = _populated_report(stores)

    markdown = render_markdown(report)
    payload = json.loads(render_json(report))

    current = payload["current_state"]
    assert f"- Active goals: {current['active_goals']}" in markdown
    assert f"- Active projects: {current['active_projects']}" in markdown
    assert f"- Goals: {report.insights.goal_growth:+d}" in markdown
    assert payload["historical_growth"]["goals"] == report.insights.goal_growth
    assert current["latest_review_date"] == report.snapshot.latest_review_date.isoformat()
