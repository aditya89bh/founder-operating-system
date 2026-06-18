"""SQLite-backed implementation of the decision store."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from types import TracebackType

from founder_os.models import DecisionRecord

_CREATE_DECISIONS_TABLE = """
CREATE TABLE IF NOT EXISTS decisions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    decision TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create the decision engine tables on ``connection`` if they do not exist."""
    connection.execute(_CREATE_DECISIONS_TABLE)
    connection.commit()


class SQLiteDecisionStore:
    """A decision store backed by a SQLite database."""

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

    def __enter__(self) -> SQLiteDecisionStore:
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

    def create_decision(self, decision: DecisionRecord) -> DecisionRecord:
        """Persist ``decision`` and return the stored record."""
        connection = self._require_connection()
        connection.execute(
            "INSERT INTO decisions (id, title, decision, created_at) VALUES (?, ?, ?, ?)",
            (
                decision.id,
                decision.title,
                decision.decision,
                decision.created_at.isoformat(),
            ),
        )
        connection.commit()
        return decision
