"""A self-contained demonstration of the Founder Operating System.

This module powers the ``founder-os demo`` command. It loads a small, fixed
demo dataset into temporary SQLite stores and runs the operating loop, historical
insights, and reporting subsystems against it. It uses the engines exactly as
built and adds no new behavior; everything it touches already exists in the
package. The temporary databases are removed when the demo finishes, so running
it leaves nothing behind.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from founder_os.decisions.sqlite_store import SQLiteDecisionStore
from founder_os.goals.sqlite_store import SQLiteGoalStore
from founder_os.memory.sqlite_store import SQLiteMemoryStore
from founder_os.priorities.sqlite_store import SQLitePriorityStore
from founder_os.projects.sqlite_store import SQLiteProjectStore
from founder_os.reviews.sqlite_store import SQLiteReviewStore


@dataclass
class DemoStores:
    """A bundle of connected SQLite stores, one per engine."""

    goals: SQLiteGoalStore
    projects: SQLiteProjectStore
    priorities: SQLitePriorityStore
    decisions: SQLiteDecisionStore
    memories: SQLiteMemoryStore
    reviews: SQLiteReviewStore

    def close(self) -> None:
        """Close every underlying store connection."""
        self.goals.close()
        self.projects.close()
        self.priorities.close()
        self.decisions.close()
        self.memories.close()
        self.reviews.close()


def open_demo_stores(directory: Path) -> DemoStores:
    """Open and connect one SQLite store per engine inside ``directory``."""
    directory.mkdir(parents=True, exist_ok=True)
    goals = SQLiteGoalStore(directory / "goals.db")
    projects = SQLiteProjectStore(directory / "projects.db")
    priorities = SQLitePriorityStore(directory / "priorities.db")
    decisions = SQLiteDecisionStore(directory / "decisions.db")
    memories = SQLiteMemoryStore(directory / "memories.db")
    reviews = SQLiteReviewStore(directory / "reviews.db")
    for store in (goals, projects, priorities, decisions, memories, reviews):
        store.connect()
    return DemoStores(
        goals=goals,
        projects=projects,
        priorities=priorities,
        decisions=decisions,
        memories=memories,
        reviews=reviews,
    )


@contextmanager
def demo_stores() -> Iterator[DemoStores]:
    """Yield connected demo stores backed by a throwaway temporary directory."""
    with TemporaryDirectory() as tmp:
        stores = open_demo_stores(Path(tmp))
        try:
            yield stores
        finally:
            stores.close()
