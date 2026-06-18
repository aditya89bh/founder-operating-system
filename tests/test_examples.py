"""Tests for the founder scenarios and the end-to-end walkthrough."""

from __future__ import annotations

from pathlib import Path

from examples.scenarios import Scenario, all_scenarios
from examples.walkthrough import (
    DemoStores,
    build_demo_report,
    open_demo_stores,
    run_walkthrough,
)

from founder_os.reporting.models import FounderReport


def test_all_scenarios_has_at_least_five_named_scenarios() -> None:
    scenarios = all_scenarios()
    assert len(scenarios) >= 5
    names = [scenario.name for scenario in scenarios]
    assert len(set(names)) == len(names)
    assert all(scenario.description for scenario in scenarios)


def test_every_scenario_contains_records() -> None:
    for scenario in all_scenarios():
        total = (
            len(scenario.goals)
            + len(scenario.projects)
            + len(scenario.priorities)
            + len(scenario.decisions)
            + len(scenario.memories)
            + len(scenario.reviews)
        )
        assert total > 0, f"scenario {scenario.name!r} has no records"


def _load_scenario(stores: DemoStores, scenario: Scenario) -> None:
    for goal in scenario.goals:
        stores.goals.create_goal(goal)
    for project in scenario.projects:
        stores.projects.create_project(project)
    for priority in scenario.priorities:
        stores.priorities.create_priority(priority)
    for decision in scenario.decisions:
        stores.decisions.create_decision(decision)
    for memory in scenario.memories:
        stores.memories.add_memory(memory)
    for review in scenario.reviews:
        stores.reviews.create_review(review)


def test_scenarios_load_into_stores_and_build_a_report(tmp_path: Path) -> None:
    for index, scenario in enumerate(all_scenarios()):
        stores = open_demo_stores(tmp_path / f"scenario-{index}")
        try:
            _load_scenario(stores, scenario)
            report = build_demo_report(stores)
        finally:
            stores.close()
        assert isinstance(report, FounderReport)


def test_walkthrough_builds_expected_snapshot() -> None:
    report = run_walkthrough()
    snapshot = report.snapshot
    assert snapshot.active_goal_count == 2
    assert snapshot.active_project_count == 2
    assert snapshot.active_priority_count == 3
    assert snapshot.recent_decision_count == 5
    assert snapshot.recent_memory_count == 5
    assert not snapshot.health.no_active_goals
    assert not snapshot.health.no_recent_reviews


def test_walkthrough_builds_expected_insights() -> None:
    insights = run_walkthrough().insights
    assert insights.review_count == 5
    assert insights.goal_growth == 1
    assert insights.project_growth == 1
    assert insights.priority_growth == 1
    assert insights.decision_growth == 4
    assert insights.memory_growth == 4
