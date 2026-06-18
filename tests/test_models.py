"""Tests for the Founder Operating System domain models."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from founder_os.models import (
    DecisionRecord,
    GoalRecord,
    GoalStatus,
    MemoryRecord,
    PriorityRecord,
    PriorityStatus,
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
    record = PriorityRecord(title="Ship onboarding revamp")

    assert record.title == "Ship onboarding revamp"
    assert record.status is PriorityStatus.ACTIVE


def test_goal_record_valid_creation() -> None:
    record = GoalRecord(
        title="Reach 100 paying customers",
        description="Grow from design partners to a repeatable sales motion.",
    )

    assert record.title == "Reach 100 paying customers"
    assert record.status is GoalStatus.ACTIVE


def test_project_record_valid_creation() -> None:
    record = ProjectRecord(
        title="Onboarding revamp",
        description="Rebuild the first-run experience.",
        status=ProjectStatus.ACTIVE,
    )

    assert record.title == "Onboarding revamp"
    assert record.status is ProjectStatus.ACTIVE


def test_memory_record_rejects_empty_content() -> None:
    with pytest.raises(ValidationError):
        MemoryRecord(content="")


def test_memory_record_rejects_unknown_field() -> None:
    with pytest.raises(ValidationError):
        MemoryRecord(content="A note", unexpected="value")


def test_decision_record_requires_decision() -> None:
    with pytest.raises(ValidationError):
        DecisionRecord(title="Pick a stack")


def test_decision_record_rejects_empty_title() -> None:
    with pytest.raises(ValidationError):
        DecisionRecord(title="", decision="Use Postgres.")


def test_priority_record_rejects_invalid_status() -> None:
    with pytest.raises(ValidationError):
        PriorityRecord(title="Refine pricing", status="paused")


def test_goal_record_rejects_invalid_status() -> None:
    with pytest.raises(ValidationError):
        GoalRecord(title="Hire a designer", status="paused")


def test_project_record_rejects_empty_title() -> None:
    with pytest.raises(ValidationError):
        ProjectRecord(title="")
