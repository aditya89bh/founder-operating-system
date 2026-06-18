"""Storage interface for the review engine.

The :class:`ReviewStore` protocol defines the contract that any review backend
must satisfy. A review is a historical record, so the store only creates,
retrieves, lists, and deletes reviews; it never recomputes their snapshots. It
describes behavior only; concrete persistence lives in implementations such as
:mod:`founder_os.reviews.sqlite_store`.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from founder_os.models import ReviewRecord


@runtime_checkable
class ReviewStore(Protocol):
    """A backend capable of storing and retrieving periodic reviews."""

    def create_review(self, review: ReviewRecord) -> ReviewRecord:
        """Persist ``review`` and return the stored record."""
        ...

    def get_review(self, review_id: str) -> ReviewRecord | None:
        """Return the review with ``review_id`` or ``None`` if it is absent."""
        ...

    def list_reviews(self) -> list[ReviewRecord]:
        """Return stored reviews, newest first."""
        ...

    def delete_review(self, review_id: str) -> bool:
        """Delete the review with ``review_id``; return ``True`` if a row was removed."""
        ...
