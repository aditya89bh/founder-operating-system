"""SQLite-backed implementation of the project store."""

from __future__ import annotations

import sqlite3

_CREATE_PROJECTS_TABLE = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create the project engine tables on ``connection`` if they do not exist."""
    connection.execute(_CREATE_PROJECTS_TABLE)
    connection.commit()
