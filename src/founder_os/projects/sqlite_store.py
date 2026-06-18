"""SQLite-backed implementation of the project store."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime
from pathlib import Path
from types import TracebackType

from founder_os.models import ProjectRecord

_CREATE_PROJECTS_TABLE = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'planned',
    start_date TEXT,
    target_date TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""

_CREATE_GOAL_PROJECTS_TABLE = """
CREATE TABLE IF NOT EXISTS goal_projects (
    project_id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
)
"""


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create the project engine tables on ``connection`` if they do not exist."""
    connection.execute(_CREATE_PROJECTS_TABLE)
    connection.execute(_CREATE_GOAL_PROJECTS_TABLE)
    connection.commit()


class SQLiteProjectStore:
    """A project store backed by a SQLite database."""

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

    def __enter__(self) -> SQLiteProjectStore:
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

    def create_project(self, project: ProjectRecord) -> ProjectRecord:
        """Persist ``project`` and return the stored record."""
        connection = self._require_connection()
        connection.execute(
            """
            INSERT INTO projects
                (id, title, description, status, start_date, target_date,
                 created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project.id,
                project.title,
                project.description,
                project.status.value,
                project.start_date.isoformat() if project.start_date else None,
                project.target_date.isoformat() if project.target_date else None,
                project.created_at.isoformat(),
                project.updated_at.isoformat(),
            ),
        )
        connection.commit()
        return project

    def _row_to_project(self, row: sqlite3.Row) -> ProjectRecord:
        start_date = row["start_date"]
        target_date = row["target_date"]
        return ProjectRecord(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            status=row["status"],
            start_date=date.fromisoformat(start_date) if start_date else None,
            target_date=date.fromisoformat(target_date) if target_date else None,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def get_project(self, project_id: str) -> ProjectRecord | None:
        """Return the project with ``project_id`` or ``None`` if it is absent."""
        connection = self._require_connection()
        cursor = connection.execute(
            """
            SELECT id, title, description, status, start_date, target_date,
                   created_at, updated_at
            FROM projects WHERE id = ?
            """,
            (project_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_project(row)

    def list_projects(self) -> list[ProjectRecord]:
        """Return all stored projects, newest first."""
        connection = self._require_connection()
        cursor = connection.execute(
            """
            SELECT id, title, description, status, start_date, target_date,
                   created_at, updated_at
            FROM projects ORDER BY created_at DESC, id
            """
        )
        return [self._row_to_project(row) for row in cursor.fetchall()]

    def delete_project(self, project_id: str) -> bool:
        """Delete the project with ``project_id``; return ``True`` if a row was removed."""
        connection = self._require_connection()
        cursor = connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        connection.commit()
        return cursor.rowcount > 0
