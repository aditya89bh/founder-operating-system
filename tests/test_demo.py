"""Tests for the self-contained ``founder-os demo``."""

from __future__ import annotations

from founder_os.demo import (
    demo_decisions,
    demo_goals,
    demo_insights,
    demo_memories,
    demo_priorities,
    demo_projects,
    demo_report,
    demo_reviews,
    demo_snapshot,
    demo_stores,
    load_demo_dataset,
    run_demo,
)
from founder_os.reporting.models import FounderReport


def test_demo_datasets_have_expected_sizes() -> None:
    assert len(demo_goals()) == 4
    assert len(demo_projects()) == 4
    assert len(demo_priorities()) == 5
    assert len(demo_decisions()) == 5
    assert len(demo_memories()) == 6
    assert len(demo_reviews()) == 5


def test_demo_snapshot_is_deterministic() -> None:
    with demo_stores() as stores:
        load_demo_dataset(stores)
        snapshot = demo_snapshot(stores)
    assert snapshot.active_goal_count == 2
    assert snapshot.active_project_count == 2
    assert snapshot.active_priority_count == 3
    assert snapshot.recent_decision_count == 5
    assert snapshot.recent_memory_count == 5
    assert not snapshot.health.no_active_goals
    assert not snapshot.health.no_recent_reviews


def test_demo_insights_capture_growth() -> None:
    with demo_stores() as stores:
        load_demo_dataset(stores)
        insights = demo_insights(stores)
    assert insights.review_count == 5
    assert insights.goal_growth == 1
    assert insights.project_growth == 1
    assert insights.priority_growth == 1
    assert insights.decision_growth == 4
    assert insights.memory_growth == 4


def test_demo_report_is_a_founder_report() -> None:
    with demo_stores() as stores:
        load_demo_dataset(stores)
        report = demo_report(stores)
    assert isinstance(report, FounderReport)
    assert report.snapshot.active_goal_count == 2
    assert report.insights.review_count == 5


def test_run_demo_contains_all_three_sections() -> None:
    output = run_demo()
    assert "Operating loop status" in output
    assert "Historical insights" in output
    assert "Founder report" in output
    assert "# Founder Report" in output


def test_run_demo_is_reproducible() -> None:
    assert run_demo() == run_demo()
