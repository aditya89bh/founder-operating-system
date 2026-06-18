"""Storage interface for the decision engine.

The :class:`DecisionStore` protocol defines the contract that any decision
backend must satisfy. It describes behavior only; concrete persistence lives in
implementations such as :mod:`founder_os.decisions.sqlite_store`.
"""

from __future__ import annotations

from datetime import date
from typing import Protocol, runtime_checkable

from founder_os.models import DecisionRecord


@runtime_checkable
class DecisionStore(Protocol):
    """A backend capable of storing, retrieving, and reviewing decisions."""

    def create_decision(self, decision: DecisionRecord) -> DecisionRecord:
        """Persist ``decision`` and return the stored record."""
        ...

    def get_decision(self, decision_id: str) -> DecisionRecord | None:
        """Return the decision with ``decision_id`` or ``None`` if it is absent."""
        ...

    def list_decisions(self) -> list[DecisionRecord]:
        """Return stored decisions, newest first."""
        ...

    def delete_decision(self, decision_id: str) -> bool:
        """Delete the decision with ``decision_id``; return ``True`` if a row was removed."""
        ...

    def update_outcome(
        self,
        decision_id: str,
        outcome: str,
        *,
        outcome_notes: str = "",
        review_date: date | None = None,
    ) -> DecisionRecord | None:
        """Record the outcome of a decision and return the updated record."""
        ...
