"""SQLite-backed implementation of the review store."""

from __future__ import annotations

import sqlite3

_CREATE_REVIEWS_TABLE = """
CREATE TABLE IF NOT EXISTS reviews (
    id TEXT PRIMARY KEY,
    review_date TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create the review engine tables on ``connection`` if they do not exist."""
    connection.execute(_CREATE_REVIEWS_TABLE)
    connection.commit()
