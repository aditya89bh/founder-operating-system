"""Pydantic domain models for the Founder Operating System.

These models define the typed records that the rest of the system is built on.
They describe shape and validation rules only; persistence, retrieval, and
workflow logic live outside of Phase 1.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def _new_id() -> str:
    """Return a new opaque identifier for a record."""
    return uuid4().hex


def _utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(tz=UTC)


class MemoryRecord(BaseModel):
    """A single captured memory: a note, fact, or observation worth keeping."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=_new_id)
    content: str = Field(min_length=1, max_length=10_000)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_utc_now)


class DecisionOutcome(StrEnum):
    """The reviewed result of a decision."""

    PENDING = "pending"
    SUCCESSFUL = "successful"
    UNSUCCESSFUL = "unsuccessful"
    MIXED = "mixed"
    ABANDONED = "abandoned"


class DecisionRecord(BaseModel):
    """A decision made by the founder, with the context and reasoning behind it."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=_new_id)
    title: str = Field(min_length=1, max_length=200)
    context: str = Field(default="", max_length=10_000)
    decision: str = Field(min_length=1, max_length=10_000)
    rationale: str = Field(default="", max_length=10_000)
    assumptions: str = Field(default="", max_length=10_000)
    outcome: DecisionOutcome = DecisionOutcome.PENDING
    outcome_notes: str = Field(default="", max_length=10_000)
    review_date: date | None = None
    created_at: datetime = Field(default_factory=_utc_now)


class PriorityStatus(StrEnum):
    """Lifecycle states for a priority."""

    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"


class PriorityRecord(BaseModel):
    """A priority the founder may act on, with deterministic ranking inputs."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=_new_id)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=10_000)
    category: str = Field(default="", max_length=200)
    urgency: int = Field(default=3, ge=1, le=5)
    importance: int = Field(default=3, ge=1, le=5)
    effort: int = Field(default=3, ge=1, le=5)
    status: PriorityStatus = PriorityStatus.ACTIVE
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)

    @property
    def score(self) -> float:
        """Deterministic priority score: ``(urgency * importance) / effort``.

        A higher score means the priority deserves attention sooner. ``effort``
        is constrained to be at least ``1``, so the result is always defined.
        """
        return (self.urgency * self.importance) / self.effort


class GoalStatus(StrEnum):
    """Lifecycle states for a goal."""

    ACTIVE = "active"
    ACHIEVED = "achieved"
    ABANDONED = "abandoned"


class GoalTimeframe(StrEnum):
    """The horizon a goal is pursued over."""

    YEARLY = "yearly"
    QUARTERLY = "quarterly"
    MONTHLY = "monthly"
    WEEKLY = "weekly"


class GoalRecord(BaseModel):
    """A goal the founder is working toward over a meaningful horizon."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=_new_id)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=10_000)
    timeframe: GoalTimeframe = GoalTimeframe.QUARTERLY
    status: GoalStatus = GoalStatus.ACTIVE
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)


class ProjectStatus(StrEnum):
    """Lifecycle states for a project."""

    PLANNED = "planned"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectRecord(BaseModel):
    """A project: a concrete body of work that advances one or more goals."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=_new_id)
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=10_000)
    status: ProjectStatus = ProjectStatus.PLANNED
    created_at: datetime = Field(default_factory=_utc_now)
