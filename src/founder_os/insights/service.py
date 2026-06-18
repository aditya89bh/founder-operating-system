"""The historical insight service.

This module derives :class:`~founder_os.insights.models.HistoricalInsights` from
the review snapshots stored by the review engine. It reads stored snapshots only;
it never recomputes historical state and performs no scoring, forecasting, or AI
reasoning.
"""

from __future__ import annotations

from founder_os.insights.models import HistoricalInsights
from founder_os.models import ReviewRecord
from founder_os.reviews.store import ReviewStore


def _ordered_reviews(review_store: ReviewStore) -> list[ReviewRecord]:
    """Return the stored reviews ordered oldest first.

    The review store lists reviews newest first, so the first element of the
    returned list is the earliest review and the last is the most recent.
    """
    return list(reversed(review_store.list_reviews()))


def generate_insights(review_store: ReviewStore) -> HistoricalInsights:
    """Derive historical insights from the stored review snapshots."""
    reviews = _ordered_reviews(review_store)
    oldest = reviews[0] if reviews else None
    newest = reviews[-1] if reviews else None
    return HistoricalInsights(
        review_count=len(reviews),
        oldest_review_date=oldest.review_date if oldest else None,
        newest_review_date=newest.review_date if newest else None,
    )
