"""Pydantic domain models for the Founder Operating System.

These models define the typed records that the rest of the system is built on.
They describe shape and validation rules only; persistence, retrieval, and
workflow logic live outside of Phase 1.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def _new_id() -> str:
    """Return a new opaque identifier for a record."""
    return uuid4().hex


def _utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(tz=timezone.utc)


class MemoryRecord(BaseModel):
    """A single captured memory: a note, fact, or observation worth keeping."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=_new_id)
    content: str = Field(min_length=1, max_length=10_000)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_utc_now)


class DecisionRecord(BaseModel):
    """A decision made by the founder, with the context and reasoning behind it."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=_new_id)
    title: str = Field(min_length=1, max_length=200)
    context: str = Field(default="", max_length=10_000)
    decision: str = Field(min_length=1, max_length=10_000)
    rationale: str = Field(default="", max_length=10_000)
    created_at: datetime = Field(default_factory=_utc_now)


class PriorityRecord(BaseModel):
    """A ranked priority that orders where the founder's attention should go."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=_new_id)
    title: str = Field(min_length=1, max_length=200)
    rank: int = Field(ge=1)
    created_at: datetime = Field(default_factory=_utc_now)


class GoalStatus(str, Enum):
    """Lifecycle states for a goal."""

    ACTIVE = "active"
    ACHIEVED = "achieved"
    ABANDONED = "abandoned"


class GoalRecord(BaseModel):
    """A goal the founder is working toward over a meaningful horizon."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=_new_id)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=10_000)
    status: GoalStatus = GoalStatus.ACTIVE
    created_at: datetime = Field(default_factory=_utc_now)
