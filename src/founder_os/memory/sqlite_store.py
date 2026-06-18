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


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create the memory engine tables on ``connection`` if they do not exist."""
    connection.execute(_CREATE_MEMORIES_TABLE)
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
        connection.commit()
        return memory

    def _row_to_memory(self, row: sqlite3.Row) -> MemoryRecord:
        return MemoryRecord(
            id=row["id"],
            content=row["content"],
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
