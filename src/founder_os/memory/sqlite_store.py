"""SQLite-backed implementation of the memory store."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from types import TracebackType

from founder_os.models import MemoryRecord

_CREATE_MEMORIES_TABLE = """
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""

_CREATE_MEMORY_TAGS_TABLE = """
CREATE TABLE IF NOT EXISTS memory_tags (
    memory_id TEXT NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    tag TEXT NOT NULL,
    PRIMARY KEY (memory_id, tag)
)
"""


def _escape_like(term: str) -> str:
    """Escape SQL ``LIKE`` wildcards so a search term is matched literally."""
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create the memory engine tables on ``connection`` if they do not exist."""
    connection.execute(_CREATE_MEMORIES_TABLE)
    connection.execute(_CREATE_MEMORY_TAGS_TABLE)
    connection.commit()


class SQLiteMemoryStore:
    """A memory store backed by a SQLite database."""

    def __init__(self, database: str | Path) -> None:
        self._database = str(database)
        self._connection: sqlite3.Connection | None = None

    def connect(self) -> None:
        """Open the database connection and ensure the schema exists."""
        if self._connection is not None:
            return
        connection = sqlite3.connect(self._database)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        initialize_schema(connection)
        self._connection = connection

    def close(self) -> None:
        """Close the database connection if it is open."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> SQLiteMemoryStore:
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def _require_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            raise RuntimeError("Store is not connected; call connect() first.")
        return self._connection

    def add_memory(self, memory: MemoryRecord) -> MemoryRecord:
        """Persist ``memory`` and return the stored record."""
        connection = self._require_connection()
        connection.execute(
            "INSERT INTO memories (id, content, created_at) VALUES (?, ?, ?)",
            (memory.id, memory.content, memory.created_at.isoformat()),
        )
        self._store_tags(connection, memory.id, memory.tags)
        connection.commit()
        return memory

    def _store_tags(
        self, connection: sqlite3.Connection, memory_id: str, tags: list[str]
    ) -> None:
        connection.executemany(
            "INSERT OR IGNORE INTO memory_tags (memory_id, tag) VALUES (?, ?)",
            [(memory_id, tag) for tag in tags],
        )

    def _load_tags(self, memory_id: str) -> list[str]:
        connection = self._require_connection()
        cursor = connection.execute(
            "SELECT tag FROM memory_tags WHERE memory_id = ? ORDER BY tag",
            (memory_id,),
        )
        return [str(row["tag"]) for row in cursor.fetchall()]

    def _row_to_memory(self, row: sqlite3.Row) -> MemoryRecord:
        return MemoryRecord(
            id=row["id"],
            content=row["content"],
            tags=self._load_tags(row["id"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def get_memory(self, memory_id: str) -> MemoryRecord | None:
        """Return the memory with ``memory_id`` or ``None`` if it does not exist."""
        connection = self._require_connection()
        cursor = connection.execute(
            "SELECT id, content, created_at FROM memories WHERE id = ?",
            (memory_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_memory(row)

    def list_memories(self, *, tag: str | None = None) -> list[MemoryRecord]:
        """Return stored memories, newest first, optionally filtered by ``tag``."""
        connection = self._require_connection()
        if tag is None:
            cursor = connection.execute(
                "SELECT id, content, created_at FROM memories ORDER BY created_at DESC, id"
            )
        else:
            cursor = connection.execute(
                """
                SELECT m.id, m.content, m.created_at
                FROM memories AS m
                JOIN memory_tags AS t ON t.memory_id = m.id
                WHERE t.tag = ?
                ORDER BY m.created_at DESC, m.id
                """,
                (tag,),
            )
        return [self._row_to_memory(row) for row in cursor.fetchall()]

    def search_memories(self, query: str, *, tag: str | None = None) -> list[MemoryRecord]:
        """Return memories whose content matches ``query``, optionally filtered by ``tag``."""
        connection = self._require_connection()
        pattern = f"%{_escape_like(query)}%"
        if tag is None:
            cursor = connection.execute(
                """
                SELECT id, content, created_at
                FROM memories
                WHERE content LIKE ? ESCAPE '\\'
                ORDER BY created_at DESC, id
                """,
                (pattern,),
            )
        else:
            cursor = connection.execute(
                """
                SELECT m.id, m.content, m.created_at
                FROM memories AS m
                JOIN memory_tags AS t ON t.memory_id = m.id
                WHERE m.content LIKE ? ESCAPE '\\' AND t.tag = ?
                ORDER BY m.created_at DESC, m.id
                """,
                (pattern, tag),
            )
        return [self._row_to_memory(row) for row in cursor.fetchall()]

    def delete_memory(self, memory_id: str) -> bool:
        """Delete the memory with ``memory_id``; return ``True`` if a row was removed."""
        connection = self._require_connection()
        cursor = connection.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        connection.commit()
        return cursor.rowcount > 0
