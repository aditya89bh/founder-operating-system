"""Domain models for the Founder Operating Loop."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class HealthIndicators(BaseModel):
    """Boolean flags that highlight gaps in the operating system.

    Each flag is ``True`` when something is missing. They are plain observations,
    not scores or recommendations.
    """

    model_config = ConfigDict(extra="forbid")

    no_active_goals: bool = False
    no_active_projects: bool = False
    no_active_priorities: bool = False
    no_recent_reviews: bool = False


class FounderSnapshot(BaseModel):
    """A deterministic, point-in-time view of the whole operating system."""

    model_config = ConfigDict(extra="forbid")

    active_goal_count: int = Field(default=0, ge=0)
    active_project_count: int = Field(default=0, ge=0)
    active_priority_count: int = Field(default=0, ge=0)
    recent_decision_count: int = Field(default=0, ge=0)
    recent_memory_count: int = Field(default=0, ge=0)
    latest_review_date: date | None = None
    health: HealthIndicators = Field(default_factory=HealthIndicators)
