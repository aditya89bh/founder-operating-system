"""Domain models for the founder report system."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from founder_os.insights.models import HistoricalInsights
from founder_os.operating_loop.models import FounderSnapshot


class ReportSection(StrEnum):
    """The canonical sections of a founder report, in display order.

    Both the Markdown and JSON exporters use these as the single source of truth
    for section titles so the two formats stay aligned.
    """

    CURRENT_STATE = "Current State"
    HEALTH_INDICATORS = "Health Indicators"
    HISTORICAL_GROWTH = "Historical Growth"
    REVIEW_HISTORY = "Review History"


class FounderReport(BaseModel):
    """A deterministic founder report combining live state and historical growth.

    It pairs the operating-loop ``snapshot`` (current state and health) with the
    ``insights`` derived from stored review snapshots (historical growth and
    review history). It is a faithful composition of both, with no added analysis.
    """

    model_config = ConfigDict(extra="forbid")

    snapshot: FounderSnapshot
    insights: HistoricalInsights
