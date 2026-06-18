"""Storage interface for the priority engine.

The :class:`PriorityStore` protocol defines the contract that any priority
backend must satisfy. It describes behavior only; concrete persistence lives in
implementations such as :mod:`founder_os.priorities.sqlite_store`.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from founder_os.models import PriorityRecord


@runtime_checkable
class PriorityStore(Protocol):
    """A backend capable of storing, retrieving, and ranking priorities."""

    def create_priority(self, priority: PriorityRecord) -> PriorityRecord:
        """Persist ``priority`` and return the stored record."""
        ...

    def get_priority(self, priority_id: str) -> PriorityRecord | None:
        """Return the priority with ``priority_id`` or ``None`` if it is absent."""
        ...

    def list_priorities(self) -> list[PriorityRecord]:
        """Return stored priorities, newest first."""
        ...

    def delete_priority(self, priority_id: str) -> bool:
        """Delete the priority with ``priority_id``; return ``True`` if a row was removed."""
        ...

    def rank_priorities(self) -> list[PriorityRecord]:
        """Return active priorities ordered by deterministic score, highest first."""
        ...
