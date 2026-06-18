"""SQLite-backed implementation of the priority store."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from types import TracebackType

from founder_os.models import PriorityRecord

_CREATE_PRIORITIES_TABLE = """
CREATE TABLE IF NOT EXISTS priorities (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL DEFAULT '',
    urgency INTEGER NOT NULL DEFAULT 3,
    importance INTEGER NOT NULL DEFAULT 3,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create the priority engine tables on ``connection`` if they do not exist."""
    connection.execute(_CREATE_PRIORITIES_TABLE)
    connection.commit()


class SQLitePriorityStore:
    """A priority store backed by a SQLite database."""

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

    def __enter__(self) -> SQLitePriorityStore:
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

    def create_priority(self, priority: PriorityRecord) -> PriorityRecord:
        """Persist ``priority`` and return the stored record."""
        connection = self._require_connection()
        connection.execute(
            """
            INSERT INTO priorities
                (id, title, description, category, urgency, importance, status,
                 created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                priority.id,
                priority.title,
                priority.description,
                priority.category,
                priority.urgency,
                priority.importance,
                priority.status.value,
                priority.created_at.isoformat(),
                priority.updated_at.isoformat(),
            ),
        )
        connection.commit()
        return priority

    def _row_to_priority(self, row: sqlite3.Row) -> PriorityRecord:
        return PriorityRecord(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            category=row["category"],
            urgency=row["urgency"],
            importance=row["importance"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def get_priority(self, priority_id: str) -> PriorityRecord | None:
        """Return the priority with ``priority_id`` or ``None`` if it is absent."""
        connection = self._require_connection()
        cursor = connection.execute(
            """
            SELECT id, title, description, category, urgency, importance, status,
                   created_at, updated_at
            FROM priorities WHERE id = ?
            """,
            (priority_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_priority(row)

    def list_priorities(self) -> list[PriorityRecord]:
        """Return all stored priorities, newest first."""
        connection = self._require_connection()
        cursor = connection.execute(
            """
            SELECT id, title, description, category, urgency, importance, status,
                   created_at, updated_at
            FROM priorities ORDER BY created_at DESC, id
            """
        )
        return [self._row_to_priority(row) for row in cursor.fetchall()]

    def delete_priority(self, priority_id: str) -> bool:
        """Delete the priority with ``priority_id``; return ``True`` if a row was removed."""
        connection = self._require_connection()
        cursor = connection.execute("DELETE FROM priorities WHERE id = ?", (priority_id,))
        connection.commit()
        return cursor.rowcount > 0
