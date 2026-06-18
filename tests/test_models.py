"""Tests for the Founder Operating System domain models."""

from __future__ import annotations

from datetime import datetime

from founder_os.models import (
    DecisionRecord,
    GoalRecord,
    GoalStatus,
    MemoryRecord,
    PriorityRecord,
    ProjectRecord,
    ProjectStatus,
)


def test_memory_record_valid_creation() -> None:
    record = MemoryRecord(content="Spoke with a design partner about onboarding.")

    assert record.content == "Spoke with a design partner about onboarding."
    assert record.tags == []
    assert isinstance(record.id, str)
    assert record.id
    assert isinstance(record.created_at, datetime)


def test_decision_record_valid_creation() -> None:
    record = DecisionRecord(
        title="Adopt weekly planning",
        context="Execution felt reactive.",
        decision="Run a structured weekly planning session every Monday.",
        rationale="A fixed cadence reduces context switching.",
    )

    assert record.title == "Adopt weekly planning"
    assert record.context == "Execution felt reactive."
    assert record.decision.startswith("Run a structured")
    assert record.rationale


def test_priority_record_valid_creation() -> None:
    record = PriorityRecord(title="Ship onboarding revamp", rank=1)

    assert record.title == "Ship onboarding revamp"
    assert record.rank == 1


def test_goal_record_valid_creation() -> None:
    record = GoalRecord(
        title="Reach 100 paying customers",
        description="Grow from design partners to a repeatable sales motion.",
    )

    assert record.title == "Reach 100 paying customers"
    assert record.status is GoalStatus.ACTIVE


def test_project_record_valid_creation() -> None:
    record = ProjectRecord(
        name="Onboarding revamp",
        description="Rebuild the first-run experience.",
        status=ProjectStatus.ACTIVE,
    )

    assert record.name == "Onboarding revamp"
    assert record.status is ProjectStatus.ACTIVE
