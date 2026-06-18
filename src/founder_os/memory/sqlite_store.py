"""SQLite-backed implementation of the memory store."""

from __future__ import annotations

import sqlite3

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
