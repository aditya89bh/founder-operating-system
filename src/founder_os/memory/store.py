"""Storage interface for the memory engine.

The :class:`MemoryStore` protocol defines the contract that any memory backend
must satisfy. It describes behavior only; concrete persistence lives in the
implementations such as :mod:`founder_os.memory.sqlite_store`.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from founder_os.models import MemoryRecord


@runtime_checkable
class MemoryStore(Protocol):
    """A backend capable of storing and retrieving memories."""

    def add_memory(self, memory: MemoryRecord) -> MemoryRecord:
        """Persist ``memory`` and return the stored record."""
        ...

    def get_memory(self, memory_id: str) -> MemoryRecord | None:
        """Return the memory with ``memory_id`` or ``None`` if it does not exist."""
        ...

    def list_memories(self, *, tag: str | None = None) -> list[MemoryRecord]:
        """Return stored memories, newest first, optionally filtered by ``tag``."""
        ...

    def search_memories(self, query: str, *, tag: str | None = None) -> list[MemoryRecord]:
        """Return memories whose content matches ``query``, optionally filtered by ``tag``."""
        ...

    def delete_memory(self, memory_id: str) -> bool:
        """Delete the memory with ``memory_id``; return ``True`` if a row was removed."""
        ...
