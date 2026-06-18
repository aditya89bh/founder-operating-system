"""Domain models for the founder report system."""

from __future__ import annotations

from enum import StrEnum


class ReportSection(StrEnum):
    """The canonical sections of a founder report, in display order.

    Both the Markdown and JSON exporters use these as the single source of truth
    for section titles so the two formats stay aligned.
    """

    CURRENT_STATE = "Current State"
    HEALTH_INDICATORS = "Health Indicators"
    HISTORICAL_GROWTH = "Historical Growth"
    REVIEW_HISTORY = "Review History"
