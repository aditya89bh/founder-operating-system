"""SQLite-backed implementation of the priority store."""

from __future__ import annotations

import sqlite3

_CREATE_PRIORITIES_TABLE = """
CREATE TABLE IF NOT EXISTS priorities (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create the priority engine tables on ``connection`` if they do not exist."""
    connection.execute(_CREATE_PRIORITIES_TABLE)
    connection.commit()
