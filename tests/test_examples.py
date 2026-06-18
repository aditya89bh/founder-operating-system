"""Tests for the founder scenarios and the end-to-end walkthrough."""

from __future__ import annotations

from pathlib import Path

from examples.cli_workflows import cli_workflows
from examples.datasets import (
    demo_decisions,
    demo_goals,
    demo_memories,
    demo_priorities,
    demo_projects,
    demo_reviews,
)
from examples.scenarios import Scenario, all_scenarios
from examples.walkthrough import (
    DemoStores,
    build_demo_report,
    open_demo_stores,
    render_walkthrough_markdown,
    run_walkthrough,
)

from founder_os.models import PriorityStatus
from founder_os.reporting.models import FounderReport

_SAMPLE_REPORT = Path(__file__).resolve().parent.parent / "examples" / "sample_report.md"


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


def test_demo_datasets_have_expected_sizes() -> None:
    assert len(demo_goals()) == 4
    assert len(demo_projects()) == 4
    assert len(demo_priorities()) == 5
    assert len(demo_decisions()) == 5
    assert len(demo_memories()) == 6
    assert len(demo_reviews()) == 5


def test_demo_datasets_return_fresh_records() -> None:
    first = demo_goals()
    second = demo_goals()
    assert first is not second
    assert all(a is not b for a, b in zip(first, second, strict=True))


def test_demo_priority_statuses_cover_the_lifecycle() -> None:
    statuses = {priority.status for priority in demo_priorities()}
    assert statuses == {
        PriorityStatus.ACTIVE,
        PriorityStatus.COMPLETED,
        PriorityStatus.DROPPED,
    }


def test_demo_priority_scores_are_well_defined() -> None:
    for priority in demo_priorities():
        assert priority.score == (priority.urgency * priority.importance) / priority.effort


def test_demo_reviews_are_ordered_oldest_first() -> None:
    reviews = demo_reviews()
    dates = [review.review_date for review in reviews]
    assert dates == sorted(dates)


def test_cli_workflows_are_well_formed() -> None:
    workflows = cli_workflows()
    assert len(workflows) >= 5
    for workflow in workflows:
        assert workflow.name
        assert workflow.description
        assert workflow.commands
        assert all(command.startswith("founder-os ") for command in workflow.commands)


def test_sample_report_matches_walkthrough_output() -> None:
    saved = _SAMPLE_REPORT.read_text().strip()
    assert saved == render_walkthrough_markdown().strip()
