"""Storage interface for the project engine.

The :class:`ProjectStore` protocol defines the contract that any project backend
must satisfy. It covers project persistence as well as the relationship storage
that aligns projects with the goals they advance. It describes behavior only;
concrete persistence lives in implementations such as
:mod:`founder_os.projects.sqlite_store`.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from founder_os.models import ProjectRecord


@runtime_checkable
class ProjectStore(Protocol):
    """A backend capable of storing and retrieving projects and their goals."""

    def create_project(self, project: ProjectRecord) -> ProjectRecord:
        """Persist ``project`` and return the stored record."""
        ...

    def get_project(self, project_id: str) -> ProjectRecord | None:
        """Return the project with ``project_id`` or ``None`` if it is absent."""
        ...

    def list_projects(self) -> list[ProjectRecord]:
        """Return stored projects, newest first."""
        ...

    def delete_project(self, project_id: str) -> bool:
        """Delete the project with ``project_id``; return ``True`` if a row was removed."""
        ...

    def link_project_to_goal(self, project_id: str, goal_id: str) -> None:
        """Align a project with a goal, replacing any existing alignment."""
        ...

    def get_goal_projects(self, goal_id: str) -> list[str]:
        """Return the identifiers of projects aligned with ``goal_id``."""
        ...
