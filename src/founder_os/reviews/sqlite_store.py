"""SQLite-backed implementation of the review store."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime
from pathlib import Path
from types import TracebackType

from founder_os.models import ReviewRecord

_CREATE_REVIEWS_TABLE = """
CREATE TABLE IF NOT EXISTS reviews (
    id TEXT PRIMARY KEY,
    review_date TEXT NOT NULL,
    review_type TEXT NOT NULL DEFAULT 'weekly',
    notes TEXT NOT NULL DEFAULT '',
    active_goals INTEGER NOT NULL DEFAULT 0,
    completed_goals INTEGER NOT NULL DEFAULT 0,
    active_projects INTEGER NOT NULL DEFAULT 0,
    completed_projects INTEGER NOT NULL DEFAULT 0,
    active_priorities INTEGER NOT NULL DEFAULT 0,
    completed_priorities INTEGER NOT NULL DEFAULT 0,
    decision_count INTEGER NOT NULL DEFAULT 0,
    memory_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
)
"""

_REVIEW_COLUMNS = (
    "id, review_date, review_type, notes, "
    "active_goals, completed_goals, active_projects, completed_projects, "
    "active_priorities, completed_priorities, decision_count, memory_count, "
    "created_at"
)


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create the review engine tables on ``connection`` if they do not exist."""
    connection.execute(_CREATE_REVIEWS_TABLE)
    connection.commit()


class SQLiteReviewStore:
    """A review store backed by a SQLite database."""

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

    def __enter__(self) -> SQLiteReviewStore:
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

    def create_review(self, review: ReviewRecord) -> ReviewRecord:
        """Persist ``review`` and return the stored record."""
        connection = self._require_connection()
        connection.execute(
            """
            INSERT INTO reviews (id, review_date, review_type, notes, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                review.id,
                review.review_date.isoformat(),
                review.review_type.value,
                review.notes,
                review.created_at.isoformat(),
            ),
        )
        connection.commit()
        return review

    def _row_to_review(self, row: sqlite3.Row) -> ReviewRecord:
        return ReviewRecord(
            id=row["id"],
            review_date=date.fromisoformat(row["review_date"]),
            review_type=row["review_type"],
            notes=row["notes"],
            active_goals=row["active_goals"],
            completed_goals=row["completed_goals"],
            active_projects=row["active_projects"],
            completed_projects=row["completed_projects"],
            active_priorities=row["active_priorities"],
            completed_priorities=row["completed_priorities"],
            decision_count=row["decision_count"],
            memory_count=row["memory_count"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def get_review(self, review_id: str) -> ReviewRecord | None:
        """Return the review with ``review_id`` or ``None`` if it is absent."""
        connection = self._require_connection()
        cursor = connection.execute(
            f"SELECT {_REVIEW_COLUMNS} FROM reviews WHERE id = ?",
            (review_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_review(row)

    def list_reviews(self) -> list[ReviewRecord]:
        """Return all stored reviews, newest first."""
        connection = self._require_connection()
        cursor = connection.execute(
            f"""
            SELECT {_REVIEW_COLUMNS}
            FROM reviews ORDER BY review_date DESC, created_at DESC, id
            """
        )
        return [self._row_to_review(row) for row in cursor.fetchall()]

    def delete_review(self, review_id: str) -> bool:
        """Delete the review with ``review_id``; return ``True`` if a row was removed."""
        connection = self._require_connection()
        cursor = connection.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
        connection.commit()
        return cursor.rowcount > 0
