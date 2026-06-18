"""SQLite-backed implementation of the goal store."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime
from pathlib import Path
from types import TracebackType

from founder_os.models import GoalRecord

_CREATE_GOALS_TABLE = """
CREATE TABLE IF NOT EXISTS goals (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    timeframe TEXT NOT NULL DEFAULT 'quarterly',
    target_date TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""

_CREATE_GOAL_PRIORITIES_TABLE = """
CREATE TABLE IF NOT EXISTS goal_priorities (
    priority_id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL,
    FOREIGN KEY (goal_id) REFERENCES goals (id) ON DELETE CASCADE
)
"""


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create the goal engine tables on ``connection`` if they do not exist."""
    connection.execute(_CREATE_GOALS_TABLE)
    connection.execute(_CREATE_GOAL_PRIORITIES_TABLE)
    connection.commit()


class SQLiteGoalStore:
    """A goal store backed by a SQLite database."""

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

    def __enter__(self) -> SQLiteGoalStore:
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

    def create_goal(self, goal: GoalRecord) -> GoalRecord:
        """Persist ``goal`` and return the stored record."""
        connection = self._require_connection()
        connection.execute(
            """
            INSERT INTO goals
                (id, title, description, timeframe, target_date, status,
                 created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                goal.id,
                goal.title,
                goal.description,
                goal.timeframe.value,
                goal.target_date.isoformat() if goal.target_date else None,
                goal.status.value,
                goal.created_at.isoformat(),
                goal.updated_at.isoformat(),
            ),
        )
        connection.commit()
        return goal

    def _row_to_goal(self, row: sqlite3.Row) -> GoalRecord:
        target_date = row["target_date"]
        return GoalRecord(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            timeframe=row["timeframe"],
            target_date=date.fromisoformat(target_date) if target_date else None,
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def get_goal(self, goal_id: str) -> GoalRecord | None:
        """Return the goal with ``goal_id`` or ``None`` if it is absent."""
        connection = self._require_connection()
        cursor = connection.execute(
            """
            SELECT id, title, description, timeframe, target_date, status,
                   created_at, updated_at
            FROM goals WHERE id = ?
            """,
            (goal_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_goal(row)

    def list_goals(self) -> list[GoalRecord]:
        """Return all stored goals, newest first."""
        connection = self._require_connection()
        cursor = connection.execute(
            """
            SELECT id, title, description, timeframe, target_date, status,
                   created_at, updated_at
            FROM goals ORDER BY created_at DESC, id
            """
        )
        return [self._row_to_goal(row) for row in cursor.fetchall()]

    def delete_goal(self, goal_id: str) -> bool:
        """Delete the goal with ``goal_id``; return ``True`` if a row was removed."""
        connection = self._require_connection()
        cursor = connection.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        connection.commit()
        return cursor.rowcount > 0

    def link_priority_to_goal(self, priority_id: str, goal_id: str) -> None:
        """Align a priority with a goal, replacing any existing alignment.

        A priority belongs to at most one goal, so re-linking it moves it to the
        new goal rather than creating a second alignment.
        """
        connection = self._require_connection()
        connection.execute(
            "INSERT OR REPLACE INTO goal_priorities (priority_id, goal_id) VALUES (?, ?)",
            (priority_id, goal_id),
        )
        connection.commit()

    def get_goal_priorities(self, goal_id: str) -> list[str]:
        """Return the identifiers of priorities aligned with ``goal_id``.

        The goal engine stores only the alignment; callers can resolve the
        identifiers against the priority engine when they need full records.
        """
        connection = self._require_connection()
        cursor = connection.execute(
            "SELECT priority_id FROM goal_priorities WHERE goal_id = ? ORDER BY priority_id",
            (goal_id,),
        )
        return [row["priority_id"] for row in cursor.fetchall()]
