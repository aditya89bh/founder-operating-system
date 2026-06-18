"""The historical insight service.

This module derives :class:`~founder_os.insights.models.HistoricalInsights` from
the review snapshots stored by the review engine. It reads stored snapshots only;
it never recomputes historical state and performs no scoring, forecasting, or AI
reasoning.
"""

from __future__ import annotations

from founder_os.insights.models import HistoricalInsights
from founder_os.reviews.store import ReviewStore


def generate_insights(review_store: ReviewStore) -> HistoricalInsights:
    """Derive historical insights from the stored review snapshots."""
    return HistoricalInsights()
