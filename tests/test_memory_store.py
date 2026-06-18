"""Tests for the SQLite-backed memory store."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from founder_os.memory.sqlite_store import SQLiteMemoryStore
from founder_os.models import MemoryRecord


@pytest.fixture
def store(tmp_path: Path) -> Iterator[SQLiteMemoryStore]:
    memory_store = SQLiteMemoryStore(tmp_path / "memory.db")
    memory_store.connect()
    try:
        yield memory_store
    finally:
        memory_store.close()


def test_add_and_get_memory(store: SQLiteMemoryStore) -> None:
    record = store.add_memory(MemoryRecord(content="Investor call notes"))

    fetched = store.get_memory(record.id)

    assert fetched is not None
    assert fetched.id == record.id
    assert fetched.content == "Investor call notes"


def test_get_missing_memory_returns_none(store: SQLiteMemoryStore) -> None:
    assert store.get_memory("does-not-exist") is None


def test_list_memories_returns_all(store: SQLiteMemoryStore) -> None:
    store.add_memory(MemoryRecord(content="First"))
    store.add_memory(MemoryRecord(content="Second"))

    records = store.list_memories()

    assert {record.content for record in records} == {"First", "Second"}


def test_delete_memory_removes_record(store: SQLiteMemoryStore) -> None:
    record = store.add_memory(MemoryRecord(content="Temporary note"))

    assert store.delete_memory(record.id) is True
    assert store.get_memory(record.id) is None
    assert store.delete_memory(record.id) is False
