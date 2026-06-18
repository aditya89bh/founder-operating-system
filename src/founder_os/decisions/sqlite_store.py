"""SQLite-backed implementation of the decision store."""

from __future__ import annotations

import sqlite3

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
