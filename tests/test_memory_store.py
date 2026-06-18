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


def test_tags_are_persisted(store: SQLiteMemoryStore) -> None:
    record = store.add_memory(
        MemoryRecord(content="Closed seed round", tags=["fundraising", "milestone"])
    )

    fetched = store.get_memory(record.id)

    assert fetched is not None
    assert fetched.tags == ["fundraising", "milestone"]


def test_list_memories_filters_by_tag(store: SQLiteMemoryStore) -> None:
    store.add_memory(MemoryRecord(content="Eng standup", tags=["eng"]))
    store.add_memory(MemoryRecord(content="Sales sync", tags=["sales"]))

    results = store.list_memories(tag="eng")

    assert [record.content for record in results] == ["Eng standup"]


def test_search_matches_content(store: SQLiteMemoryStore) -> None:
    store.add_memory(MemoryRecord(content="Spoke with a design partner"))
    store.add_memory(MemoryRecord(content="Refactored billing"))

    results = store.search_memories("design")

    assert [record.content for record in results] == ["Spoke with a design partner"]


def test_search_respects_tag_filter(store: SQLiteMemoryStore) -> None:
    store.add_memory(MemoryRecord(content="Pricing experiment", tags=["growth"]))
    store.add_memory(MemoryRecord(content="Pricing review", tags=["finance"]))

    results = store.search_memories("Pricing", tag="growth")

    assert [record.content for record in results] == ["Pricing experiment"]


def test_search_treats_wildcards_literally(store: SQLiteMemoryStore) -> None:
    store.add_memory(MemoryRecord(content="Plain note without wildcards"))

    assert store.search_memories("%") == []
