"""Domain models for historical insights."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class HistoricalInsights(BaseModel):
    """A deterministic summary of how the system has evolved across reviews.

    Growth values are the latest review snapshot minus the earliest review
    snapshot. They are plain integer deltas and may be negative; they are never
    percentages or scores.
    """

    model_config = ConfigDict(extra="forbid")

    review_count: int = Field(default=0, ge=0)
    oldest_review_date: date | None = None
    newest_review_date: date | None = None
    goal_growth: int = 0
    project_growth: int = 0
    priority_growth: int = 0
    decision_growth: int = 0
    memory_growth: int = 0
