"""SQLite-backed implementation of the goal store."""

from __future__ import annotations

import sqlite3

_CREATE_GOALS_TABLE = """
CREATE TABLE IF NOT EXISTS goals (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create the goal engine tables on ``connection`` if they do not exist."""
    connection.execute(_CREATE_GOALS_TABLE)
    connection.commit()
